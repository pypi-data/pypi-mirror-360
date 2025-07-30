import asyncio

async def execute_channel(method, sender):
    thread = asyncio.to_thread(__execute__, method, sender)
    asyncio.create_task(thread)


def __execute__(method, sender):
    sender.to_clients(None, [sender.client], 'start')
    method(sender)
    sender.to_clients(None, [sender.client], 'stop')


