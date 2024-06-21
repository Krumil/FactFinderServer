from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool


@tool
def get_image_description(image_url: str) -> str:
    """
    Given an image URL, return a description of the image.
    """
    prompt = """Given the image below, describe the image in detail."""
    model = ChatOpenAI(temperature=0, model="gpt-4o", max_tokens=1024)
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
