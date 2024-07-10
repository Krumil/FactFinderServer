from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from utils import load_settings

settings = load_settings()
llm_to_use = settings["llm"]

def generate_tweet(fact_check: str, original_tweet: str) -> str:
    prompt = f"""Given the fact check below, create a short version for a tweet answering to the original tweet:
        Original tweet: {original_tweet}
        Fact check: {fact_check}
        Answer with only the text of the tweet. Sound as human as possible."""
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
                ]
            )
        ]
    )
    if msg.content.startswith('"') and msg.content.endswith('"'):
        return msg.content[1:-1]
    return msg.content