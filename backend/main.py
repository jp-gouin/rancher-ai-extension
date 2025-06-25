from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
import ollama
import asyncio
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:8006"],  # Or use ["http://localhost:5173"] if you're using Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ollama.base_url = os.getenv('OLLAMA_SERVER_URL', "http://localhost:11434")

# ------------------- Tool Functions -------------------
def get_time() -> str:
  """
  Get the current time


  Returns:
    str: The current time formatted as a string
  """
  return f"The current time is {datetime.now().strftime('%H:%M:%S')}"

def add_two_numbers(a: int, b: int) -> int:
  """
  Add two numbers

  Args:
    a (set): The first number as an int
    b (set): The second number as an int

  Returns:
    int: The sum of the two numbers
  """
  return a + b

def call_tool_by_name(name: str, args: dict):
    if name == "get_time":
        return get_time()
    return f"Unknown tool: {name}"

# ------------------- API -------------------
@app.get("/chat")
async def chat_endpoint(request: Request, prompt: str = ""):
    user_prompt = prompt
    print(request.cookies)
    async def event_generator():
        messages = [{"role": "user", "content": user_prompt}]
        function_call = None

        # ---- 1st Call: Initial model response w/ potential function_call ----
        stream = ollama.chat(
            model="qwen3:4b",
            messages=messages,
            tools=[add_two_numbers, get_time],
            stream=True
        )

        collected_content = ""
        for chunk in stream:  # sync generator!
            msg = chunk.get("message", {})
            content = msg.get("content")
            collected_content += content or ""

            if content:
                yield f"{content}\n\n"
                await asyncio.sleep(0.01)

            if chunk.message.tool_calls:
                print(chunk.message.tool_calls)
                function_call = chunk.message.tool_calls[0].function
                break

        # ---- 2nd Call: After tool execution ----
        if function_call:
            print(function_call)
            tool_name = function_call.name
            # args = json.loads(function_call.arguments)
            tool_output = call_tool_by_name(tool_name, function_call.arguments)

            messages.append(chunk.message)
            messages.append({'role': 'tool', 'content': tool_output, 'name': tool_name})

            # Second LLM response using tool output
            second_stream = ollama.chat(
                model="qwen3:4b",
                messages=messages,
                stream=True
            )

            for chunk in second_stream:
                content = chunk.get("message", {}).get("content")
                if content:
                    yield f"{content}\n\n"
                    await asyncio.sleep(0.01) 

        yield f"[END]]\n\n"

    return EventSourceResponse(event_generator())
