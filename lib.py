import asyncio
import logging
import inspect
import hashlib
from logging import basicConfig, info, INFO
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from rich.console import Console
from rich.table import Table
from rich import box

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
        info("PubSub is starting...")

        self._dispatch_task = asyncio.create_task(self._dispatch())
        info("PubSub is running.")

    async def close(self):
        self._running = False
        if self._dispatch_task:
            await self._dispatch_task
        info("PubSub is closing...")


class MyBroker:
    def __init__(self):
        self.functions = {}
        self.name_to_hash = {}
        self.pubsub = MyPubSub()

    def register(self, func):
        func_hash = self.generate_hash(func)
        self.functions[func_hash] = func
        self.name_to_hash[func.__name__] = func_hash
        info(f"Registered function '{func.__name__}'")
        return func

    def get_function(self, func_hash):
        return self.functions.get(func_hash)

    def get_hash_by_name(self, name):
        return self.name_to_hash.get(name)

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
        return hashlib.sha256(hash_input.encode()).hexdigest()


broker = MyBroker()


class ChainNode:
    def __init__(self, func_name: str, func_hash: str, args: tuple, kwargs: dict):
        self.func_name = func_name
        self.func_hash = func_hash
        self.args = args
        self.kwargs = kwargs
        self.prev: Optional[ChainNode] = None
        self.next: Optional[ChainNode] = None


class MyChain:
    def __init__(self, value, broker: MyBroker):
        self.value = value
        self.initial_value = value
        self.head: Optional[ChainNode] = None
        self.tail: Optional[ChainNode] = None
        self.current: Optional[ChainNode] = None
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
        func_hash = self.broker.get_hash_by_name(func_name)
        if not func_hash:
            raise ValueError(f"Function '{func_name}' is not registered.")
        info(f"Adding function '{func_name}' to the chain...")
        new_node = ChainNode(func_name, func_hash, args, kwargs)
        if self.tail:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        else:
            self.head = self.tail = new_node
        return self

    def pipe(self, chain_fn):
        # Execute the function to get a new MyChain instance
        new_chain = chain_fn(self.value)
        if not isinstance(new_chain, MyChain):
            raise ValueError("The function must return a MyChain instance.")

        # Append the new chain's nodes to the current chain
        node = new_chain.head
        while node:
            self.pipe_by_name(node.func_name, *node.args, **node.kwargs)
            node = node.next

        return self

    async def step(self):
        if not self.current:
            self.current = self.head

        if not self.current:
            raise IndexError("No functions in the chain")

        func_name, func_hash, args, kwargs = (
            self.current.func_name,
            self.current.func_hash,
            self.current.args,
            self.current.kwargs,
        )
        await self.pubsub.publish(
            "step_execution",
            {
                "func_name": func_name,
                "func_hash": func_hash,
                "args": args,
                "kwargs": kwargs,
                "parent": self.current.prev.func_hash if self.current.prev else None,
                "child": self.current.next.func_hash if self.current.next else None,
            },
        )

    async def handle_step_execution(self, data):
        info(f"Executing function '{data['func_name']}'")
        func_hash = data["func_hash"]
        func = self.broker.get_function(func_hash)
        args = data["args"]
        kwargs = data["kwargs"]

        if asyncio.iscoroutinefunction(func):
            self.value = await func(self.value, *args, **kwargs)
        else:
            self.value = func(self.value, *args, **kwargs)

        await self.pubsub.publish(
            "step_executed",
            {
                "func_hash": func_hash,
                "input": (self.value, *args),
                "output": self.value,
                "parent": data["parent"],
                "child": data["child"],
            },
        )

    async def handle_step_executed(self, data):
        info(f"Function '{data['func_hash']}' executed with result: {data['output']}")
        if self.current and self.current.next:
            self.current = self.current.next
            await self.step()
        else:
            self.result_event.set()

    def reset(self):
        info("Resetting the chain...")
        self.current = None
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

    def visualize_dependencies(self):
        logging.info(
            "*********************************************************************************************"
        )
        if self.head:
            self._draw_tree(self.head)

        logging.info(
            "*********************************************************************************************"
        )
        return self

    def _draw_tree(self, node, prefix="", is_last=True):
        logging.info(f"{prefix}{'`- ' if is_last else '|- '}{node.func_name}")
        prefix += "   " if is_last else "|  "
        if node.next:
            self._draw_tree(node.next, prefix, is_last=True)


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
