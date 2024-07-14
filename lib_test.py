import pytest
import asyncio
import logging
from lib import (
    MyChain,
    broker,
    MyBroker,
    MyPubSub,
)


@pytest.fixture(scope="function", autouse=True)
async def setup_teardown_pubsub():
    broker.run_pubsub()
    yield
    await broker.stop_pubsub()  # Assuming there is a method to stop the pubsub
    await asyncio.sleep(0)  # Give asyncio a moment to clean up


@pytest.mark.asyncio
async def test_simple_chain():
    result = await (
        MyChain(10, broker)
        .pipe_by_name("add", 5)
        .pipe_by_name("subtract", 3)
        .pipe_by_name("multiply", 2)
        .pipe_by_name("divide", 3)
        .visualize_dependencies()
        .play_and_wait_result()
    )
    assert result == 8, "The chain calculation did not return the expected result."


# @pytest.mark.asyncio
# async def test_simple_chain2():
#     result = await (
#         MyChain(10, broker)
#         .pipe_by_name("add", 5)
#         .pipe_by_name("subtract", 3)
#         .pipe_by_name("multiply", 2)
#         .pipe_by_name("divide", 3)
#         .visualize_dependencies()
#         .play_and_wait_result()
#     )
#     assert result == 8, "The chain calculation did not return the expected result."


# @pytest.mark.asyncio
# # @pytest.mark.skip(reason="Just skip for now")
# async def test_simple2_chain():
#     broker.run_pubsub()

#     chain1 = (
#         MyChain(10, broker)
#         .pipe_by_name("add", 5)
#         .pipe_by_name("subtract", 3)
#         .pipe_by_name("multiply", 2)
#         .pipe_by_name("divide", 3)
#         .visualize_dependencies()
#     )

#     result = await chain1.play_and_wait_result()
#     assert result == 8, "The chain calculation did not return the expected result."


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
