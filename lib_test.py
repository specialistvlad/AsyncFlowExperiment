import pytest
import asyncio
import logging
from lib import MyChain, MyPubSub


@pytest.mark.asyncio
async def test_simple_chain():
    pubsub = MyPubSub()
    pubsub.run()

    try:
        assert 8 == await (
            MyChain(10, pubsub)
            .pipe_by_name("add", 5)
            .pipe_by_name("subtract", 3)
            .pipe_by_name("multiply", 2)
            .pipe_by_name("divide", 3)
            .play_and_wait_result()
        ), "The chain calculation did not return the expected result."
    finally:
        await pubsub.close()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet.")
async def test_nested_chain():
    pubsub = MyPubSub()
    pubsub.run()

    try:
        result = await (
            MyChain(10, pubsub)
            .pipe(
                lambda value: MyChain(value, pubsub)
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
            expected_result == result
        ), "The chain calculation did not return the expected result."
    finally:
        await pubsub.close()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet.")
async def test_flat_map():
    pubsub = MyPubSub()
    pubsub.run()

    try:
        result = await (
            MyChain(None, pubsub)
            .pipe_by_name("load_array", 5)
            .map_by_name("add", 5)
            .map_by_name("subtract", 3)
            .map_by_name("multiply", 2)
            .map_by_name("divide", 3)
            .play_and_wait_result()
        )
        expected_result = [0, 1, 2, 3, 4]
        assert (
            expected_result == result
        ), "The chain calculation did not return the expected result."
    finally:
        await pubsub.close()


@pytest.mark.asyncio
@pytest.mark.skip(reason="Not implemented yet.")
async def test_nested_map():
    pubsub = MyPubSub()
    pubsub.run()

    try:
        result = await (
            MyChain(None, pubsub)
            .pipe_by_name("load_array", 5)
            .map(
                lambda value: MyChain(value, pubsub)
                .pipe_by_name("add", 5)
                .pipe_by_name("subtract", 3)
                .pipe_by_name("multiply", 2)
                .pipe_by_name("divide", 3)
            )
            .play_and_wait_result()
        )
        expected_result = [0, 1, 2, 3, 4]
        assert (
            expected_result == result
        ), "The chain calculation did not return the expected result."
    finally:
        await pubsub.close()
