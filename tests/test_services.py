import asyncio
import os
from datetime import datetime

import pytest

from src.abstract.context import AContext
from src.domain.events import Event, FileReplicatedEvent, FileSavedEvent
from src.domain.model import FileInfo, Server
from src.services.event_manager import EventManager
from src.services.file_cleaner import start_file_cleaner
from src.services.handlers import replicate_file, send_replicated_file_status


@pytest.mark.asyncio
async def test_replication_file_with_file_should_publish_event(fake_context):
    file_info = FileInfo(name="text", file_type="txt", origin_url="test")
    event = FileSavedEvent(file_info, 0, datetime.now())
    await replicate_file(fake_context, event)

    assert isinstance(fake_context.events.events[-1], FileReplicatedEvent)


@pytest.mark.asyncio
async def test_send_replicated_file_status_with_correct_data_return_status(
    fake_context,
):
    file = FileInfo(name="test", file_type="txt", origin_url="test")
    server = Server(name="TestVPS", ip="0.0.0.0", zone="test")
    event = FileReplicatedEvent(
        file_info=file,
        duration=10,
        time=datetime.now(),
        server=server,
        is_last_server=True,
    )
    try:
        # method will pass the test if it executes without errors
        await send_replicated_file_status(fake_context, event)
    except Exception:
        pytest.fail("raise Exception")


@pytest.mark.asyncio
async def test_event_manager_publish_with_handlers_should_process(fake_context):
    # create event class
    class TestEvent(Event):
        def __init__(self):
            # contains the names of handlers that processed the event
            self.processed_handlers = []

    # create handler
    async def handler(context: AContext, event: TestEvent):
        event.processed_handlers.append("handler")

    event_manager = EventManager()
    # subscribe handler to TestEvent
    event_manager.subscribe(TestEvent, handler)

    event = TestEvent()
    await event_manager.publish(fake_context, event)
    # Provide control to the handler
    # and wait until it completes its task
    await asyncio.sleep(0.001)

    assert "handler" in event.processed_handlers


@pytest.mark.asyncio
async def test_file_cleaner_with_file_should_delete(context, create_test_file):
    # start cleaner task
    task = asyncio.create_task(start_file_cleaner(context))

    await asyncio.sleep(0.1)

    # stop cleaner task
    task.cancel()

    assert not os.path.exists(context.FILES_DIR / "test.txt")
