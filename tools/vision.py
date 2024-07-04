from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from utils import load_settings

settings = load_settings()
llm_to_use = settings["llm"]


@tool
def get_image_description(image_url: str) -> str:
    """
    Given an image URL, return a description of the image.
    """
    prompt = """Given the image below, describe the image in detail."""
    if llm_to_use == "openai":
        model = ChatOpenAI(temperature=0, model="gpt-4o", max_tokens=1024)
    if llm_to_use == "anthropic":
        model = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0,
        )
    else:
        raise ValueError(f"LLM {llm_to_use} is not supported")

    msg = model.invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"{image_url}"},
                    },
                ]
            )
        ]
    )
    return msg.content
