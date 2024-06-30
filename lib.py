import asyncio
import logging
from logging import info
from collections import defaultdict
from typing import Any, Callable, Dict, List


# Custom formatter to include class name and function name in log messages
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.class_name = record.__dict__.get("class_name", "") or "<unknown>"
        record.func_name = record.__dict__.get("func_name", "") or "<unknown>"
        return super().format(record)


formatter = CustomFormatter(
    "%(levelname)s | %(class_name)s | %(func_name)s | %(message)s"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger()

counter = 5
function_container = {}


def register_function(name):
    def decorator(func):
        function_container[name] = func
        return func

    return decorator


class MyPubSub:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self.queue = asyncio.Queue()
        self._running = True
        self._dispatch_task = None

    async def publish(self, topic: str, data: Any):
        logger.info(
            f"Publishing to topic '{topic}'",
            extra={"class_name": "MyPubSub", "func_name": "publish"},
        )
        await self.queue.put((topic, data))

    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        async def async_callback_wrapper(data):
            if not asyncio.iscoroutinefunction(callback):
                callback(data)
            else:
                await callback(data)

        logger.info(
            f"Subscribing to topic '{topic}'",
            extra={"class_name": "MyPubSub", "func_name": "subscribe"},
        )
        self.subscribers[topic].append(async_callback_wrapper)

    async def _dispatch(self):
        while self._running or not self.queue.empty():
            try:
                topic, data = await asyncio.wait_for(self.queue.get(), timeout=0.1)
                for callback in self.subscribers.get(topic, []):
                    asyncio.create_task(callback(data))
            except asyncio.TimeoutError:
                continue

    def run(self):
        logger.info(
            "PubSub is starting...",
            extra={"class_name": "MyPubSub", "func_name": "run"},
        )
        self._dispatch_task = asyncio.create_task(self._dispatch())
        logger.info(
            "PubSub is running.", extra={"class_name": "MyPubSub", "func_name": "run"}
        )

    async def close(self):
        self._running = False
        if self._dispatch_task:
            await self._dispatch_task
        logger.info(
            "PubSub is closing...",
            extra={"class_name": "MyPubSub", "func_name": "close"},
        )


class MyChain:
    def __init__(self, value, pubsub: MyPubSub):
        self.value = value
        self.initial_value = value
        self.chain = []
        self.index = 0
        self.pubsub = pubsub
        self.result_event = asyncio.Event()

        pubsub.subscribe(
            "execute_step",
            lambda data: asyncio.create_task(self.handle_step_execution(data)),
        )
        pubsub.subscribe(
            "step_executed",
            lambda data: asyncio.create_task(self.handle_step_executed(data)),
        )

    def pipe_by_name(self, func_name, *args, **kwargs):
        logger.info(
            f"Adding function '{func_name}' to the chain...",
            extra={"class_name": "MyChain", "func_name": "pipe_by_name"},
        )
        if func_name not in function_container:
            raise ValueError(f"Function '{func_name}' is not registered.")
        self.chain.append((func_name, args, kwargs))
        return self

    async def step(self):
        logger.info(
            f"Stepping to index {self.index}",
            extra={"class_name": "MyChain", "func_name": "step"},
        )
        global counter
        counter -= 1
        if counter <= 0:
            raise ValueError("Counter is too high")

        if self.index >= len(self.chain):
            raise IndexError("Index out of range")

        func_name, args, kwargs = self.chain[self.index]
        await self.pubsub.publish(
            "execute_step",
            {
                "index": self.index,
                "func_name": func_name,
                "args": args,
                "kwargs": kwargs,
            },
        )

    async def handle_step_execution(self, data):
        logger.info(
            f"Executing step {data['index']}",
            extra={"class_name": "MyChain", "func_name": "handle_step_execution"},
        )
        func_name = data["func_name"]
        func = function_container[func_name]
        args = data["args"]
        kwargs = data["kwargs"]

        if asyncio.iscoroutinefunction(func):
            self.value = await func(self.value, *args, **kwargs)
        else:
            self.value = func(self.value, *args, **kwargs)

        self.index += 1
        await self.pubsub.publish(
            "step_executed", {"index": self.index, "value": self.value}
        )

    async def handle_step_executed(self, data):
        logger.info(
            f"Step {data['index']} executed with value: {data['value']}",
            extra={"class_name": "MyChain", "func_name": "handle_step_executed"},
        )
        if self.index < len(self.chain):
            await self.step()
        else:
            self.result_event.set()

    def reset(self):
        logger.info(
            "Resetting the chain...",
            extra={"class_name": "MyChain", "func_name": "reset"},
        )
        self.index = 0
        self.value = self.initial_value

    async def play(self):
        logger.info(
            "Playing the chain...", extra={"class_name": "MyChain", "func_name": "play"}
        )
        self.reset()
        await self.step()

    async def play_and_wait_result(self):
        logger.info(
            "Playing the chain and waiting for result...",
            extra={"class_name": "MyChain", "func_name": "play_and_wait_result"},
        )
        self.result_event.clear()
        await self.play()
        await self.result_event.wait()
        return self.value


@register_function("add")
def add(input_value: int, amount: int):
    return input_value + amount


@register_function("subtract")
def subtract(input_value: int, amount: int):
    return input_value - amount


@register_function("multiply")
def multiply(input_value: int, factor: int):
    return input_value * factor


@register_function("divide")
def divide(input_value: int, divisor: int):
    if divisor == 0:
        raise ValueError("Division by zero is not allowed.")
    return input_value / divisor


async def main():
    info("You can not run this file directly. Please run lib_test.py instead.")


if __name__ == "__main__":
    asyncio.run(main())
