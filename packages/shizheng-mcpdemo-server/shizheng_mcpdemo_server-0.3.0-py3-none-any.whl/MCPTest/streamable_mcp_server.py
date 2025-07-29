from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langgraph.graph import Graph
from langchain_core.messages import HumanMessage, AIMessage
from functools import partial
import asyncio
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# 启用 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义状态为字典
def update_state(state, new_messages):
    return {"messages": state["messages"] + new_messages}

# 定义 agent 节点
def agent_node(state, update_state):
    last_message = state["messages"][-1]
    if isinstance(last_message, HumanMessage):
        response = f"Echo: {last_message.content}"
        return update_state(state, [AIMessage(content=response)])
    return state

# 创建图
builder = Graph()
builder.add_node("agent", partial(agent_node, update_state=update_state))
builder.add_edge("agent", "__end__")
builder.set_entry_point("agent")
graph = builder.compile()

# 流式处理函数
async def stream_graph_updates(input_text: str):
    state = {"messages": [HumanMessage(content=input_text)]}
    try:
        for event in graph.stream(state):
            await asyncio.sleep(0.1)
            print(event)
            if "messages" in event:
                for message in event["messages"]:
                    if isinstance(message, AIMessage):
                        yield f"data: {message.content}\n\n"
            else:
                yield f"data: {"hello !!!"}"
    except Exception as e:
        yield f"data: [ERROR] {str(e)}\n\n"

# 接口路由
@app.post("/mcp/invoke")
async def mcp_invoke(request: Request):
    try:
        data = await request.json()
        input_text = data.get("input")
        if not input_text:
            raise HTTPException(status_code=400, detail="Missing input text")
        logging.info(f"Received input: {input_text}")
        return StreamingResponse(stream_graph_updates(input_text), media_type="text/event-stream")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
