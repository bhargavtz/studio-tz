
import asyncio
from app.config import settings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

async def test_model():
    print(f"Testing model: {settings.llm_model}")
    try:
        chat = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.llm_model,
            temperature=0.7
        )
        response = await chat.ainvoke([HumanMessage(content="Hello")])
        print("Success!")
        print(response.content)
    except Exception as e:
        print(f"Failure: {e}")

if __name__ == "__main__":
    asyncio.run(test_model())
