
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not found in environment")
        return

    print(f"Testing Groq API with key: {api_key[:5]}...{api_key[-5:]}")
    import httpx
    print(f"httpx version: {httpx.__version__}")
    
    try:
        # TEST 1: Direct Groq Client
        print("\n--- TEST 1: Direct Groq Client ---")
        from groq import Groq
        print("Imported Groq client.")
        
        client = Groq(api_key=api_key)
        print("Initialized Groq client directly.")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        print("Direct Response:", chat_completion.choices[0].message.content)

        # TEST 2: LangChain ChatGroq
        print("\n--- TEST 2: LangChain ChatGroq ---")
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage
        
        chat = ChatGroq(
            api_key=api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.5
        )
        print("Initialized ChatGroq.")
        response = await chat.ainvoke([HumanMessage(content="Hello")])
        print("LangChain Response:", response.content)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILURE: Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq())
