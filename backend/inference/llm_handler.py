import os
import requests
import openai
from abc import ABC, abstractmethod
from typing import Generator, Literal
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
import asyncio

load_dotenv()

# --- Interface ---
class LLMHandler(ABC):
    @abstractmethod
    def stream_reply(self, prompt: str) -> Generator[str, None, None]:
        pass

# --- Ollama ---
class OllamaHandler:
    def __init__(self, model="llama3.2"):
        self.chat_model = ChatOllama(model=model)

        self.prompts = {
            "voice": ChatPromptTemplate.from_messages([
                ("system", "You are a helpful and friendly AI voice assistant. Respond conversationally and briefly (less than 20 words) unless user asks for more info. You can ask follow up questions after answering the query. Here is the conversation history: {chat_history}"),
                ("user", "{user_input}")
            ]),
            "chat": ChatPromptTemplate.from_messages([
                ("system", "You are a helpful and friendly AI assistant. Respond conversationally and helpfully. Here is the conversation history: {chat_history}"),
                ("user", "{user_input}")
            ])
        }

    async def stream_reply(
        self,
        user_input: str,
        chat_history: list[BaseMessage],
        mode: Literal["voice", "chat"] = "voice"
            ) -> Generator[str, None, None]:
        prompt = self.prompts[mode]
        messages = prompt.format_messages(user_input=user_input, chat_history=chat_history)

        # Update history with user input
        chat_history.append(messages[1])

        # Stream response from model
        async for chunk in self.chat_model.astream(messages):
            if chunk.content:
                yield chunk.content

        # Re-run for final message (needed for OpenAI-compatible memory)
        full_response = await self.chat_model.ainvoke(messages)
        chat_history.append(AIMessage(full_response.content))

# --- OpenAI ---
class OpenAIHandler(LLMHandler):
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def stream_reply(self, prompt: str) -> Generator[str, None, None]:
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response:
            if 'choices' in chunk:
                delta = chunk['choices'][0]['delta']
                if 'content' in delta:
                    yield delta['content']
