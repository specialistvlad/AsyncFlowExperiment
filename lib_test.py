import pytest
import asyncio
from lib import (
    MyChain,
    broker,
    MyBroker,
    MyPubSub,
)


@pytest.mark.asyncio
async def test_simple_chain():
    broker.run_pubsub()

    try:
        result = await (
            MyChain(10, broker)
            .pipe_by_name("add", 5)
            .pipe_by_name("subtract", 3)
            .pipe_by_name("multiply", 2)
            .pipe_by_name("divide", 3)
            .play_and_wait_result()
        )
        assert result == 8, "The chain calculation did not return the expected result."
    finally:
        await broker.close_pubsub()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet.")
async def test_nested_chain():
    broker.run_pubsub()

    try:
        result = await (
            MyChain(10, broker)
            .pipe(
                lambda value: MyChain(value, broker)
                .pipe_by_name("add", 5)
                .pipe_by_name("subtract", 3)
                .pipe_by_name("multiply", 2)
                .pipe_by_name("divide", 3)
            )
            .pipe_by_name("add", 5)
            .pipe_by_name("subtract", 3)
            .pipe_by_name("multiply", 2)
            .pipe_by_name("divide", 3)
            .play_and_wait_result()
        )
        expected_result = [0, 1, 2, 3, 4]
        assert (
            result == expected_result
        ), "The chain calculation did not return the expected result."
    finally:
        await broker.close_pubsub()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet.")
async def test_flat_map():
    broker.run_pubsub()

    try:
        result = await (
            MyChain(None, broker)
            .pipe_by_name("load_array", 5)
            .map_by_name("add", 5)
            .map_by_name("subtract", 3)
            .map_by_name("multiply", 2)
            .map_by_name("divide", 3)
            .play_and_wait_result()
        )
        expected_result = [0, 1, 2, 3, 4]
        assert (
            result == expected_result
        ), "The chain calculation did not return the expected result."
    finally:
        await broker.close_pubsub()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet.")
async def test_nested_map():
    broker.run_pubsub()

    try:
        result = await (
            MyChain(None, broker)
            .pipe_by_name("load_array", 5)
            .map(
                lambda value: MyChain(value, broker)
                .pipe_by_name("add", 5)
                .pipe_by_name("subtract", 3)
                .pipe_by_name("multiply", 2)
                .pipe_by_name("divide", 3)
            )
            .play_and_wait_result()
        )
        expected_result = [0, 1, 2, 3, 4]
        assert (
            result == expected_result
        ), "The chain calculation did not return the expected result."
    finally:
        await broker.close_pubsub()
