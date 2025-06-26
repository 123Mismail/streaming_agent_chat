import os
import fitz  # PyMuPDF for PDF parsing
from dotenv import load_dotenv
import chainlit as cl
from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled,function_tool
from agents.run import RunConfig
from openai.types.responses import ResponseTextDeltaEvent
from load_store_data import search
from deep_translator import GoogleTranslator
import google.generativeai as genai 



load_dotenv()
set_tracing_disabled(True)
api_key = os.getenv("GEMINI_KEY")
genai.configure(api_key=api_key)
if not api_key:
    raise ValueError("GEMINI_KEY not found in environment variables")

base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
client = AsyncOpenAI(api_key=api_key, base_url=base_url)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

run_config = RunConfig(model=model, model_provider=client)
 
@function_tool
async def getuser_info(query: str) -> str:
    if not query:
        return (
            "🔎 Query: [empty]\n"
            "📝 Answer: Please provide a valid query related to the Constitution of Pakistan.\n"
            "📘 جواب: براہ کرم پاکستان کے آئین سے متعلق ایک درست سوال فراہم کریں۔"
        )

    results = await search(query, top_k=5)

    if not results:
        return (
            f"🔎 Query: {query}\n"
            f"📝 Answer: No relevant information found in the Constitution of Pakistan.\n"
            f"📘 جواب: معذرت، پاکستان کے آئین میں آپ کے سوال سے متعلق کوئی معلومات نہیں ملی۔"
        )

    formatted_context = "\n\n".join(
        [f"[{i+1}] {r['text']}" for i, r in enumerate(results)]
    )
    llm_prompt = (
        f"You are an expert on the Constitution of Pakistan.\n"
        f"A user asked: \"{query}\"\n"
        f"Here are 5 possible answers retrieved from the Constitution:\n\n"
        f"{formatted_context}\n\n"
        f"Please return only the most relevant one."
    )

    # Use Gemini 1.5 Flash model
    model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
    response = model.generate_content(llm_prompt)
    selected_answer = response.text 
    print(f"\n\n ******* Selected answer ****** \n\n : {selected_answer}")

    # Translate to Urdu
    urdu_translation = GoogleTranslator(source='en', target='ur').translate(selected_answer)

    return (
        f"🔎 Query: {query}\n"
        f"📝 Answer:\n{selected_answer}\n\n"
        f"📘 جواب:\n{urdu_translation}"
    )
agent = Agent(
    name="Pakistan Constitution Agent",
    instructions=(
        "You are a helpful assistant. "
        "You are only allowed to answer questions using the tool `getuser_info`. "
        "Do not attempt to answer on your own. "
        "All responses must include the original query, a formatted answer, and its Urdu translation. "
        "If the tool does not return relevant information, reply with: "
        "'Sorry, I couldn't find any information related to your question in the Constitution of Pakistan.'"
    ),
    tools=[getuser_info],
    model=model,
)



 

# Chat start
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("chat_history", [])
    
    await cl.Message(content = (
    "📜 Welcome to the Agentic AI Constitutional Chatbot! 🇵🇰\n\n"
    "Ask questions, explore your rights, and uncover the wisdom of the Constitution of Pakistan.\n"
    "⚖️ Let justice guide you. 📚 Let knowledge empower you. 🕊️ Let your voice be informed."
)).send()
    
@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content="📚 Consulting the Constitution...").send()

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
    stream_msg = cl.Message(content="⚖️")
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

 