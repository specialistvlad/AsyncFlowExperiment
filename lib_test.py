import pytest
import asyncio
import logging
from lib import MyChain, MyPubSub


@pytest.mark.asyncio
async def test_lib():
    pubsub = MyPubSub()
    pubsub.run()

    try:
        # Directly assert the result within the same line
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


if __name__ == "__main__":
    asyncio.run(test_main())
