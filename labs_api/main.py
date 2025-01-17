import time
import typing as t
import uuid
from multiprocessing import Queue, Process, Manager

import fastapi
import uvicorn
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prediction_market_agent_tooling.deploy.agent import initialize_langfuse
from prediction_market_agent_tooling.gtypes import HexAddress
from prediction_market_agent_tooling.loggers import logger

from labs_api.config import Config
from labs_api.insights.insights import MarketInsightsResponse, market_insights
from labs_api.invalid.invalid import MarketInvalidResponse, market_invalid

HEX_ADDRESS_VALIDATOR = t.Annotated[
    HexAddress,
    fastapi.Query(
        ...,
        description="Hex address of the market on Omen.",
        pattern="^0x[a-fA-F0-9]{40}$",
    ),
]


def f(x):
    print(f"called f with {x=}")
    return x * x


def long_running_task(identifier: str, input_queue: Queue, output_queue: Queue):
    """A dummy function that simulates a long-running task."""
    print(f"Process {identifier} started")
    while True:
        # Check for messages in the queue
        if not input_queue.empty():
            number = input_queue.get()
            result = number**2
            print(f"Process {identifier} received {number}, squared it to {result}")
            output_queue.put(result)
        time.sleep(1)  # Prevent tight loop
    print(f"Process {identifier} ended")  # Only runs if the loop is broken


def create_app() -> fastapi.FastAPI:
    config = Config()
    initialize_langfuse(config.default_enable_langfuse)

    manager = Manager()  # thread-safe shared state
    manager.queue()
    shared_registry = manager.dict()

    app = fastapi.FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/ping/")
    def _ping() -> str:
        """Ping Pong!"""
        logger.info("Pong!")
        return "pong"

    @app.get("/market-insights/")
    def _market_insights(market_id: HEX_ADDRESS_VALIDATOR) -> MarketInsightsResponse:
        """Returns market insights for a given market on Omen."""
        insights = market_insights(market_id)
        logger.info(f"Insights for `{market_id}`: {insights.model_dump()}")
        return insights

    @app.get("/market-invalid/")
    def _market_invalid(market_id: HEX_ADDRESS_VALIDATOR) -> MarketInvalidResponse:
        """Returns whetever the market might be invalid."""
        invalid = market_invalid(market_id)
        logger.info(f"Invalid for `{market_id}`: {invalid.model_dump()}")
        return invalid

    @app.post("/start_process")
    async def start_process():
        """Starts a new process and registers it."""
        process_id = str(uuid.uuid4())  # Unique identifier for the process
        input_queue = Queue()  # Create an input queue for communication
        output_queue = Queue()  # Create an output queue for results
        process = Process(
            target=long_running_task,
            args=(process_id, input_queue, output_queue),
            daemon=True,
        )
        process.start()

        # Store the process and its queues in the registry
        shared_registry[process_id] = {
            "process": process,
            "input_queue": input_queue,
            "output_queue": output_queue,
        }
        return {"message": "Process started", "process_id": process_id}

    @app.post("/end_process/{process_id}")
    async def end_process(process_id: str):
        """Ends a specific process by its ID."""
        entry = shared_registry.get(process_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Process not found")

        # Terminate the process and remove it from the registry
        entry["process"].terminate()
        entry["process"].join()
        del shared_registry[process_id]
        return {"message": f"Process {process_id} terminated"}

    @app.post("/send_message_to_process/{process_id}")
    async def send_message_to_process(process_id: str, number: int):
        """Sends a number to a specific process to calculate its square."""
        entry = shared_registry.get(process_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Process not found")

        # Put the number in the process's queue
        queue = entry["queue"]
        queue.put(number)
        return {"message": f"Sent number {number} to process {process_id}"}

    logger.info("API created.")

    return app


if __name__ == "__main__":
    config = Config()
    uvicorn.run(
        "labs_api.main:create_app",
        factory=True,
        host=config.HOST,
        port=config.PORT,
        workers=config.WORKERS,
        reload=config.RELOAD,
        log_level="error",
    )
