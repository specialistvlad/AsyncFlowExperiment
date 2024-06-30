import asyncio
import logging
import inspect
import hashlib
from logging import basicConfig, info, INFO
from collections import defaultdict
from typing import Any, Callable, Dict, List

basicConfig(level=INFO)


class MyPubSub:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self.queue = asyncio.Queue()
        self._running = True
        self._dispatch_task = None

    async def publish(self, topic: str, data: Any):
        info(f"Publishing to topic '{topic}'")
        await self.queue.put((topic, data))

    def subscribe(self, topic: str, callback: Callable[[Any], None]):
        async def async_callback_wrapper(data):
            if not asyncio.iscoroutinefunction(callback):
                callback(data)
            else:
                await callback(data)

        info(f"Subscribing to topic '{topic}'")
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
        info(
            "PubSub is starting...",
            extra={"class_name": "MyPubSub", "func_name": "run"},
        )
        self._dispatch_task = asyncio.create_task(self._dispatch())
        info("PubSub is running.", extra={"class_name": "MyPubSub", "func_name": "run"})

    async def close(self):
        self._running = False
        if self._dispatch_task:
            await self._dispatch_task
        info("PubSub is closing...")


class MyBroker:
    def __init__(self):
        self.functions = {}
        self.pubsub = MyPubSub()

    def register(self, func):
        name = func.__name__
        self.functions[name] = func
        self.generate_hash(func)
        return func

    def get_function(self, name):
        return self.functions.get(name)

    def run_pubsub(self):
        self.pubsub.run()

    async def close_pubsub(self):
        await self.pubsub.close()

    def generate_hash(self, func: Callable) -> str:
        name = func.__name__
        sig = inspect.signature(func)
        input_interface = str(sig.parameters)
        output_interface = str(sig.return_annotation)
        hash_input = name + input_interface + output_interface
        info(f"Generating hash for function '{name}' with input: {hash_input}")
        return hashlib.sha256(hash_input.encode()).hexdigest()


broker = MyBroker()


class MyChain:
    def __init__(self, value, broker: MyBroker):
        self.value = value
        self.initial_value = value
        self.chain = []
        self.index = 0
        self.broker = broker
        self.pubsub = broker.pubsub
        self.result_event = asyncio.Event()

        self.pubsub.subscribe(
            "step_execution",
            lambda data: asyncio.create_task(self.handle_step_execution(data)),
        )
        self.pubsub.subscribe(
            "step_executed",
            lambda data: asyncio.create_task(self.handle_step_executed(data)),
        )

    def pipe_by_name(self, func_name, *args, **kwargs):
        info(f"Adding function '{func_name}' to the chain...")
        if func_name not in self.broker.functions:
            raise ValueError(f"Function '{func_name}' is not registered.")
        self.chain.append((func_name, args, kwargs))
        return self

    async def step(self):
        info(f"Stepping to index {self.index}")
        if self.index >= len(self.chain):
            raise IndexError("Index out of range")

        func_name, args, kwargs = self.chain[self.index]
        await self.pubsub.publish(
            "step_execution",
            {
                "index": self.index,
                "func_name": func_name,
                "args": args,
                "kwargs": kwargs,
            },
        )

    async def handle_step_execution(self, data):
        info(f"Executing step {data['index']}")
        func_name = data["func_name"]
        func = self.broker.get_function(func_name)
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
        info(f"Step {data['index']} executed with value: {data['value']}")
        if self.index < len(self.chain):
            await self.step()
        else:
            self.result_event.set()

    def reset(self):
        info("Resetting the chain...")
        self.index = 0
        self.value = self.initial_value

    async def play(self):
        info("Playing the chain...")
        self.reset()
        await self.step()

    async def play_and_wait_result(self):
        info("Playing the chain and waiting for result...")
        self.result_event.clear()
        await self.play()
        await self.result_event.wait()
        return self.value


@broker.register
def add(input_value: int, amount: int):
    return input_value + amount


@broker.register
def subtract(input_value: int, amount: int):
    return input_value - amount


@broker.register
def multiply(input_value: int, factor: int):
    return input_value * factor


@broker.register
def divide(input_value: int, divisor: int):
    if divisor == 0:
        raise ValueError("Division by zero is not allowed.")
    return input_value / divisor


@broker.register
def load_array(n):
    return [i for i in range(n)]


async def main():
    info("You can not run this file directly. Please run lib_test.py instead.")


if __name__ == "__main__":
    asyncio.run(main())
