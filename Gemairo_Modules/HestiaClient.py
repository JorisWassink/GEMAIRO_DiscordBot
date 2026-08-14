import asyncio

async def start_event_server(stop_callback):
    print("Starting event server...")
    async def handle_event(reader, writer):
        event = (await reader.read(1024)).decode()

        print(f"Received: {event}")

        response = "OK"

        writer.write(response.encode())
        await writer.drain()

        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(
        handle_event,
        "127.0.0.1",
        8888
    )

    async with server:
        await server.serve_forever()