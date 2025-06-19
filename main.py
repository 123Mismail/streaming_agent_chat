import os
import fitz  # PyMuPDF for PDF parsing
from dotenv import load_dotenv
import chainlit as cl
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled,function_tool
from agents.run import RunConfig
from openai.types.responses import ResponseTextDeltaEvent
 
 

# Load environment variables


load_dotenv()
set_tracing_disabled(True)

api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise ValueError("GEMINI_KEY not found in environment variables")

base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
client = AsyncOpenAI(api_key=api_key, base_url=base_url)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=client
)

run_config = RunConfig(model=model, model_provider=client)
 
 
    

@function_tool
async def getuser_info(query:str):
    """
    get the user information.
    """
   
    
    return "docs"
    
agent = Agent(
    name="test agent",
    instructions=(
        "You are a helpful assistant. "
         
    ),
    model=model,
     
)
 

# Chat start
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", [])
    
    await cl.Message(content="👋 Welcome to the Agentic AI chatbot!").send()
    
@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content="🔍 Thinking...").send()

    # Get existing history or initialize
    history = cl.user_session.get("chat_history") or []

    # Append current user message
    history.append({"role": "user", "content": message.content})

    # Construct prompt from history
    prompt = ""
    for msg in history:
        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
    prompt += "Assistant:"

    # Start streamed response
    res = Runner.run_streamed(agent, prompt)

    # Stream tokens to frontend
    stream_msg = cl.Message(content="")
    await stream_msg.send()

    response = ""
    async for event in res.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            token = event.data.delta
            response += token
            await stream_msg.stream_token(token)

    await stream_msg.update()

    # Save assistant response in history
    history.append({"role": "assistant", "content": response})
    cl.user_session.set("chat_history", history)

# Handle actions like Help / Restart
 
@cl.on_chat_resume
async def on_chat_resume():
    await cl.Message(content="🔁 Resuming your previous session...").send()

 
# Handle stop
@cl.on_stop
def on_stop():
    print("⛔ User stopped the task!")

# Handle end of chat
@cl.on_chat_end
def on_chat_end():
    print("⚠️ Chat ended due to network or session closure.")

# Run the app
if __name__ == "__main__":
    cl.run()
