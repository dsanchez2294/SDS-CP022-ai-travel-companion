from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from my_agent.chat import chat
from starlette.responses import StreamingResponse

class Request(BaseModel):
    user_input: str
    thread: str


app = FastAPI()


@app.post("/agent")
async def query_agent(request: Request):
    try:
        return StreamingResponse(chat(request.user_input, request.thread), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Agent API is running"}