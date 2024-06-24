from fastapi import FastAPI, Request
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
from tools.vision import get_image_description
import os
import logging

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

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
if not os.getenv("TAVILY_API_KEY"):
    logger.error("TAVILY_API_KEY environment variable is not set")
    raise ValueError("TAVILY_API_KEY environment variable is not set")
logger.info("TAVILY_API_KEY is set")

logger.info("Initializing LangChain components")
prompt = hub.pull("krumil/openai-tools-agent")
search = TavilySearchAPIWrapper()
tools = [TavilySearchResults(max_results=3, api_wrapper=search), get_image_description]

llm = ChatOpenAI(model="gpt-4o", temperature=0)
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
logger.info("LangChain components initialized")

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
        if not input_text:
            logger.warning("No input provided in the request")
            return {"error": "No input provided"}

        input_text = (
            "Is this fact correct? "
            + input_text
            + ". If not please provide the correct fact and why it is correct together with the source."
        )

        if image_url:
            logger.info(f"Image URL provided: {image_url}")
            input_text = f"Considering the image here: {image_url}. {input_text}"

        logger.info(f"Invoking agent executor with input: {input_text}")
        response = agent_executor.invoke({"input": input_text})
        logger.info("Agent executor response received")
        return response
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
