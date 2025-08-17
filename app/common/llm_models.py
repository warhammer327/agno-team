from agno.models.openai import OpenAIChat
from app.config import config


def get_gpt4o_model(temperature=0.1):
    return OpenAIChat(
        id="gpt-4o", api_key=config.OPENAI_API_KEY, temperature=temperature
    )


def get_gpt4o_mini_model(temperature=0.1):
    return OpenAIChat(
        id="gpt-4o-mini",
        api_key=config.OPENAI_API_KEY,
        temperature=temperature,
    )
