from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import ollama
import asyncio
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os
from ollama import Client
import httpx
import jsonref

rancher_server = os.getenv('RANCHER_URL', "https://rancher.10.144.97.97.sslip.io")
base_url = os.getenv('OLLAMA_SERVER_URL', "http://open-webui-ollama.suseai.svc.cluster.local:11434")
mcpo_url = os.getenv('MCPO_URL', "http://mcpo-service.suseai.svc.cluster.local:8000/toolbox")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[rancher_server], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
client = Client(
  host=base_url,
)

def call_tool_by_name(name: str, args: dict):
    # Extract the endpoint and HTTP method from the name
    _, endpoint_raw, method = name.split("_")
    endpoint = f"/{endpoint_raw}"  # Convert to RESTful path

    # HTTP method in lowercase
    method = method.lower()

    # Base URL and authorization
    auth_token = "Bearer top-secret"

    # Make the request using httpx
    url = f"{mcpo_url}{endpoint}"

    headers = {
        "Authorization": auth_token,
        "Content-Type": "application/json"
    }

    # Use httpx to send the request
    with httpx.Client() as client:
        response = client.request(
            method=method,
            url=url,
            headers=headers,
            json=args
        )
    # Check for successful response
    if response.status_code == 200:
        return response.text
    else :
        raise Exception(
            f"Error calling tool {name}: {response.status_code} - {response.text}")

def openapi_to_functions(openapi_spec):
    """
    Convert OpenAPI spec to a list of functions for LLM calls.
    From https://cookbook.openai.com/examples/function_calling_with_an_openapi_spec
    Args:
        openapi_spec (dict): The OpenAPI specification as a dictionary.
    Returns:
        list: A list of functions formatted for LLM calls.
    """
    functions = []

    for path, methods in openapi_spec["paths"].items():
        for method, spec_with_ref in methods.items():
            # 1. Resolve JSON references.
            spec = jsonref.replace_refs(spec_with_ref)

            # 2. Extract a name for the functions.
            function_name = spec.get("operationId")

            # 3. Extract a description and parameters.
            desc = spec.get("description") or spec.get("summary", "")

            schema = {"type": "object", "properties": {}}

            req_body = (
                spec.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            if req_body:
                schema["properties"]["requestBody"] = req_body

            params = spec.get("parameters", [])
            if params:
                param_properties = {
                    param["name"]: param["schema"]
                    for param in params
                    if "schema" in param
                }
                schema["properties"]["parameters"] = {
                    "type": "object",
                    "properties": param_properties,
                }

            functions.append(
                {"type": "function", "function": {"name": function_name, "description": desc, "parameters": schema}}
            )

    return functions
# ------------------- API -------------------
@app.get("/chat")
async def chat_endpoint(request: Request, prompt: str = ""):
    user_prompt = prompt
    # Get the cookie R_SESS if it exists from request.cookies
    if 'R_SESS' in request.cookies:
        rancher_auth = request.cookies['R_SESS']
    else:
        rancher_auth = f"none"
    
    async def event_generator():
        messages = [{"role": "user", "content": user_prompt}]
        function_call = None
        functions = []

        try:
            async with httpx.AsyncClient() as httpclient:
                tools_response = await httpclient.get(f"{mcpo_url}/openapi.json", 
                                                      headers={"Authorization": "Bearer top-secret"})
                tools = jsonref.loads(tools_response.text)
                functions = openapi_to_functions(tools)
        except Exception as e:
            yield {"data": f"Error loading tools: {str(e)}"}
            return
        while True:
            # Open a stream to the LLM
        # ---- 1st Call: Initial model response w/ potential function_call ----
        stream = client.chat(
            model="qwen3:1.7b",
            messages=messages,
            tools=functions,
            stream=True
        )

        collected_content = ""
        for chunk in stream:  # sync generator!
            print(chunk['message']['content'], end='', flush=True)
            msg = chunk.get("message", {})
            content = msg.get("content")
            collected_content += content or ""

            #if content:
            yield f"{chunk['message']['content']}"
            await asyncio.sleep(0.01)

            if chunk.message.tool_calls:
                function_call = chunk.message.tool_calls[0].function
                break

        # ---- 2nd Call: After tool execution ----
        if function_call:
            tool_name = function_call.name
           # args = json.loads(function_call.arguments)
           # insert rancher_auth into the function_call.arguments under the key header 
            function_call.arguments["Authorization"] = f"Bearer {rancher_auth}"
           
            try:
              tool_output = call_tool_by_name(tool_name, function_call.arguments)
            except Exception as e:
              tool_output = f"Error calling tool {tool_name}: {str(e)}"

            messages.append(chunk.message)
            messages.append({'role': 'tool', 'content': tool_output, 'name': tool_name})

            # Second LLM response using tool output
            second_stream = client.chat(
                model="qwen3:1.7b",
                messages=messages,
                stream=True
            )

            for chunk in second_stream:
                print(chunk['message']['content'], end='', flush=True)
                content = chunk.get("message", {}).get("content")
                #if content:
                yield f"{chunk['message']['content']}"
                await asyncio.sleep(0.01) 

        yield f"[END]]\n\n"

    return EventSourceResponse(event_generator())
