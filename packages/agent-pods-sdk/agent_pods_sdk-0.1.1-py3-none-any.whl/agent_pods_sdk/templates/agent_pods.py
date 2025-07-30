import json
import os
from dataclasses import asdict, is_dataclass
from typing import AsyncGenerator, AsyncIterator, Callable

import uvicorn
from agents import TResponseInputItem
from agents.stream_events import (
    AgentUpdatedStreamEvent,
    RawResponsesStreamEvent,
    RunItemStreamEvent,
)
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from loguru import logger
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

load_dotenv()


class PodAPI:
    app = FastAPI()
    port = 8080  # this MUST always be 8080 - web adapter reads from this
    _chat_handler: Callable[
        [list[TResponseInputItem]],
        AsyncIterator[
            RawResponsesStreamEvent | RunItemStreamEvent | AgentUpdatedStreamEvent,
        ],
    ]

    @classmethod
    def run(cls, *args, **kwargs):
        logger.info(
            f"Starting PodAPI on port {cls.port} with args: {args} and kwargs: {kwargs}"
        )
        uvicorn.run(
            cls.app,
            host="0.0.0.0",
            port=cls.port,
            *args,
            **kwargs,
        )

    @classmethod
    def chat(
        cls,
        func: Callable[
            [list[TResponseInputItem]],
            AsyncIterator[
                RawResponsesStreamEvent | RunItemStreamEvent | AgentUpdatedStreamEvent
            ],
        ],
    ):
        """
        This decorator registers the "/chat" endpoint for the chat agent function.

        The function implementation shoud receive a list of  TResponseInputItem objects and yield them
        as strings. The endpoint will stream the response back to the client using Server-Sent Events (SSE).

        """
        cls._chat_handler = func

        @cls.app.get("/")
        async def health():
            return {"status": "ok"}

        @cls.app.post("/chat")
        async def chat_endpoint(
            messages: list[TResponseInputItem],
            token: str = Header(..., alias="Token", required=True),
        ):
            if token != os.getenv("POD_API_TOKEN"):
                logger.warning("Unauthorized access attempt with token: {}", token)
                raise HTTPException(status_code=401, detail="Unauthorized")

            async def event_stream() -> AsyncGenerator[str, None]:
                async for event in cls._chat_handler(messages):
                    # Prehaps add await here?
                    # Convert event to dict, handling non-serializable fields
                    def default_serializer(obj):
                        if is_dataclass(obj):
                            return asdict(obj)  # type: ignore
                        elif isinstance(obj, BaseModel):
                            return obj.model_dump(exclude_unset=True)
                        elif callable(obj):
                            pass
                        else:
                            print("There it is a unknown object: ", obj)
                            print(obj)

                    yield json.dumps(event, default=default_serializer)

            return EventSourceResponse(
                content=event_stream(), media_type="text/event-stream"
            )

        return func
