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

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
if not os.getenv("TAVILY_API_KEY"):
    raise ValueError("TAVILY_API_KEY environment variable is not set")

prompt = hub.pull("hwchase17/openai-tools-agent")
search = TavilySearchAPIWrapper()
tools = [TavilySearchResults(max_results=3, api_wrapper=search), get_image_description]

llm = ChatOpenAI(model="gpt-4o", temperature=0)
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# async def agent_response(input_text: str):
#     async for chunk in agent_executor.astream({"input": input_text}):
#         if "output" in chunk:
#             yield f'data:{chunk["output"]}\n\n'
#         else:
#             yield f"data: Error: Invalid chunk\n\n"
#         yield "data:\n"


# @app.get("/stream")
# async def stream(request: Request):
#     input_text = request.query_params.get("input")
#     if not input_text:
#         return {"error": "No input provided"}
#     response = agent_executor.invoke({"input": input_text})
#     return response
#     # return StreamingResponse(agent_response(input_text), media_type="text/event-stream")


# create a similar post endpoint
@app.post("/stream")
async def stream(request: Request):
    response = await request.json()
    input_text = response.get("input")
    image_url = response.get("image")
    if not input_text:
        return {"error": "No input provided"}

    input_text = (
        "Is this fact correct? "
        + input_text
        + ". If not please provide the correct fact and why it is correct toghether with the source."
    )

    if image_url:
        input_text = "Considering the image here: " + image_url + ". " + input_text

    response = agent_executor.invoke({"input": input_text})
    return response


if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
