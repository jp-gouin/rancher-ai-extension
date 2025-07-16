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
import uuid

rancher_server = os.getenv('RANCHER_URL', "https://rancher.10.144.97.97.sslip.io")
base_url = os.getenv('OLLAMA_SERVER_URL', "http://open-webui-ollama.suseai.svc.cluster.local:11434")
mcpo_url = os.getenv('MCPO_URL', "http://localhost:8090/toolbox")
CONVERSATION_DIR = os.getenv('CONVERSATION_DIR', "/tmp/conversations")
model = os.getenv('LLM_MODEL', "qwen3:4b")
system_prompt = os.getenv('LLM_SYSTEM_PROMPT', "You are a helpful Rancher AI assistant trained to answer concisely and factually. Authorization header are always provided internally and should not be asked for. Limit the number of tools and function call.")
# Ensure the conversation directory exists
if not os.path.exists(CONVERSATION_DIR):
    os.makedirs(CONVERSATION_DIR)
session_store = {}
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[rancher_server, "https://localhost:8005"], 
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
                schema = req_body
            
            # test if req_body["required"] exist and if it is a list that contains "Authorization", if it's true then remove "Authorization" from the list
            if "required" in req_body and isinstance(req_body["required"], list):
                if "Authorization" in req_body["required"]:
                    req_body["required"].remove("Authorization")

            """ params = spec.get("parameters", [])
            if params:
                param_properties = {
                    param["name"]: param["schema"]
                    for param in params
                    if "schema" in param
                }
                schema["properties"]["parameters"] = {
                    "type": "object",
                    "properties": param_properties,
                } """

            functions.append(
                {"type": "function", "function": {"name": function_name, "description": desc, "parameters": schema}}
            )

    return functions
# ------------------ Store ------------------
""" def get_or_create_conversation(token: str, conversation_id: str = None):
    if token not in session_store:
        session_store[token] = {}

    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    if conversation_id not in session_store[token]:
        session_store[token][conversation_id] = []

    return conversation_id, session_store[token][conversation_id] """
def get_or_create_conversation(token: str, conversation_id: str = None):
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    path = get_conversation_path(token, conversation_id)

    if os.path.exists(path):
        with open(path, "r") as f:
            messages = json.load(f)
    else:
        messages = []
        with open(path, "w") as f:
            json.dump(messages, f, indent=2)

    return conversation_id, messages
def save_conversation(token: str, conversation_id: str, messages: list):
    path = get_conversation_path(token, conversation_id)
    with open(path, "w") as f:
        json.dump(messages, f, indent=2)

def get_conversation_path(token: str, conversation_id: str) -> str:
    return os.path.join(CONVERSATION_DIR, f"{token}_{conversation_id}.json")
# ------------------- API -------------------
async def chat_with_tools_loop(client, model, initial_messages, functions, rancher_auth):
    messages = initial_messages.copy()
    # limit the number of tools call if they fail to 2 in order to avoid infinite loops
    tool_call_count = 0
    max_tool_calls = 2
    while True:
        if tool_call_count < max_tool_calls:
            stream = client.chat(
                model=model,
                messages=messages,
                tools=functions,
                stream=True
            )
        else:
            stream = client.chat(
                model=model,
                messages=messages,
                stream=True
            )

        tool_call = None
        collected_message = {}
        collected_content = ""

        for chunk in stream:
            msg = chunk.get("message", {})
            content = msg.get("content", "")

            if content:
                collected_content += content
                yield content
                await asyncio.sleep(0.01)

            collected_message = msg  # Save full message structure

            # Detect tool call
            if msg.get("tool_calls"):
                tool_call = msg["tool_calls"][0]["function"]
                break  # Stop streaming early to handle tool

        if collected_content:
            messages.append({
                "role": "assistant",
                "content": collected_content
            })
        # If no tool call, save final assistant message and break
        if not tool_call:
            break

        # Tool call handling
        tool_name = tool_call.name
        # test if tool_call.arguments is a dict and if it is not a dict then try to parse it as json
        if isinstance(tool_call.arguments, dict):
            tool_args = tool_call.arguments
        else :    
            try:
                tool_args = json.loads(tool_call.arguments)
            except Exception as e:
                print(f"Error parsing tool arguments: {str(e)}")
                tool_args = {}
        tool_args["Authorization"] = f"Bearer {rancher_auth}"
        try:
            tool_output = call_tool_by_name(tool_name, tool_args)
        except Exception as e:
            tool_output = f"Error calling tool {tool_name}: {str(e)}"
            tool_call_count += 1

        # Append assistant's partial response before tool call
        if collected_message:
            messages.append(collected_message)

        # Append tool result
        messages.append({
            "role": "tool",
            "name": tool_name,
            "content": tool_output
        })


@app.get("/chat")
async def chat_endpoint(request: Request, prompt: str = "", conversation_id: str = None):
    user_prompt = prompt
    # Get the cookie R_SESS if it exists from request.cookies
    if 'R_SESS' in request.cookies:
        rancher_auth = request.cookies['R_SESS']
    else:
        rancher_auth = f"none"
    conversation_id, messages = get_or_create_conversation(rancher_auth, conversation_id)
    # Initialize the conversation with a system message if it's a new conversation
    if len(messages) == 0:
        messages.append({
            "role": "system",
            "content": system_prompt
        })
    messages.append({"role": "user", "content": user_prompt})
    
    async def event_generator():
        yield f"{json.dumps({'conversation_id': conversation_id})}\n\n"
        function_call = None
        functions = []
        final_message = ""

        try:
            async with httpx.AsyncClient() as httpclient:
                tools_response = await httpclient.get(f"{mcpo_url}/openapi.json", 
                                                      headers={"Authorization": "Bearer top-secret"})
                tools = jsonref.loads(tools_response.text)
                functions = openapi_to_functions(tools)
                # print(functions)
        except Exception as e:
            yield {"data": f"Error loading tools: {str(e)}"}
            return
        async for content in chat_with_tools_loop(client, model, messages, functions, rancher_auth):
            final_message += content
            yield content
        yield f"[END]]\n\n"
        messages.append({
            "role": "assistant",
            "content": final_message
        })
        save_conversation(rancher_auth, conversation_id, messages)
    return EventSourceResponse(event_generator())
# ------------------- API -------------------
@app.get("/alive")
async def chat_endpoint(request: Request):
    """
    Endpoint to check if the server is alive.
    """
    return {"status": "alive", "timestamp": datetime.now().isoformat()}
# ------------------- API -------------------
""" @app.get("/conversations")
async def list_conversations(request: Request):
    if 'R_SESS' in request.cookies:
        rancher_auth = request.cookies['R_SESS']
    else:
        rancher_auth = f"none"
    return {
        "conversations": list(session_store.get(rancher_auth, {}).keys())
    } """
@app.get("/conversations")
async def list_conversations(request: Request):
    if 'R_SESS' in request.cookies:
        rancher_auth = request.cookies['R_SESS']
    else:
        rancher_auth = f"none"
    conv_ids = []
    prefix = f"{rancher_auth}_"

    for file in os.listdir(CONVERSATION_DIR):
        if file.startswith(prefix) and file.endswith(".json"):
            conv_ids.append(file[len(prefix):-5])  # Strip prefix and .json

    return {"conversations": conv_ids}
""" @app.get("/conversation/{conversation_id}")
async def get_conversation(request: Request, conversation_id: str):
    if 'R_SESS' in request.cookies:
        rancher_auth = request.cookies['R_SESS']
    else:
        rancher_auth = f"none"
    convs = session_store.get(rancher_auth, {})
    if conversation_id not in convs:
        return {"error": "Conversation not found."}
    return {"conversation_id": conversation_id, "messages": convs[conversation_id]} """
@app.get("/conversation/{conversation_id}")
async def get_conversation(request: Request, conversation_id: str):
    """
    Return the full message history of a specific conversation.
    Requires the token that owns the conversation.
    """
    if 'R_SESS' in request.cookies:
        rancher_auth = request.cookies['R_SESS']
    else:
        rancher_auth = f"none"
    path = get_conversation_path(rancher_auth, conversation_id)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Conversation not found")

    with open(path, "r") as f:
        messages = json.load(f)

    return {
        "conversation_id": conversation_id,
        "messages": messages
    }
