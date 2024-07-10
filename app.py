from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_openai_tools_agent,
    create_tool_calling_agent,
)
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from tools.tweet_generator import generate_tweet
from tools.vision import get_image_description
from tools.fact_checker import check_fact, check_news
from utils import load_settings
from prompt import generate_fact_check_prompt
import os
import logging
from datetime import datetime

settings = load_settings()
llm_to_use = settings["llm"]


# Configure logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)


load_dotenv()
logger.info("Environment variables loaded")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise ValueError("OPENAI_API_KEY environment variable is not set")
logger.info("OPENAI_API_KEY is set")

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    logger.error("ANTHROPIC_API_KEY environment variable is not set")
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
logger.info("ANTHROPIC_API_KEY is set")

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
if not os.getenv("TAVILY_API_KEY"):
    logger.error("TAVILY_API_KEY environment variable is not set")
    raise ValueError("TAVILY_API_KEY environment variable is not set")
logger.info("TAVILY_API_KEY is set")

logger.info("Initializing LangChain components")
prompt = hub.pull("krumil/openai-tools-agent")
search = TavilySearchAPIWrapper()
tools = [
    TavilySearchResults(max_results=3, api_wrapper=search),
    check_fact,
    check_news,
    get_image_description,
]

if llm_to_use == "openai":
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
if llm_to_use == "anthropic":
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        temperature=0,
        timeout=None,
        max_retries=2,
    )
else:
    raise ValueError("Invalid LLM specified")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("FastAPI app initialized with CORS middleware")


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Fact Checker API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/stream")
async def stream(request: Request):
    logger.info("Received POST request to /stream")
    try:

        response = await request.json()
        input_text = response.get("input")
        image_url = response.get("image")
        if not input_text and not image_url:
            logger.warning("No input provided in the request")
            return {"error": "No input provided"}

        today = datetime.today().strftime("%B %d, %Y")
        input_text = generate_fact_check_prompt(input_text, today)

        if image_url:
            logger.info(f"Image URL provided: {image_url}")
            input_text = f"Considering the image here: {image_url}. {input_text}"

        if llm_to_use == "openai":
            agent = create_openai_tools_agent(llm, tools, prompt)
        elif llm_to_use == "anthropic":
            agent = create_tool_calling_agent(llm, tools, prompt)

        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        logger.info("LangChain components initialized")

        logger.info(f"Invoking agent executor with input: {input_text}")
        response = agent_executor.invoke({"input": input_text})
        logger.info("Agent executor response received")
        
        if llm_to_use == "anthropic":
            response = response["output"][0]["text"]
        if llm_to_use == "openai":
            response = response["output"]

        return response
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {"error": str(e)}


class FactCheckRequest(BaseModel):
    factCheck: str
    originalTweet: str

@app.post("/generate_tweet")
async def generate_tweet_endpoint(request: FactCheckRequest):
    logger.info("Received POST request to /generate_tweet")
    fact_check = request.factCheck
    original_tweet = request.originalTweet
    tweet = generate_tweet(fact_check, original_tweet)
    return {"tweet": tweet}



if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    # uvicorn.run("app:app", host="localhost", port=port, log_level="debug", ssl_keyfile="privatekey.key", ssl_certfile="certificate.crt")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")