import asyncio
import socketio
from aiohttp import web

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

async def broadcast_hello():
    while True:
        await sio.emit("ping", "hello")
        await asyncio.sleep(1)

async def start_Server():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8081)
    await site.start()
    print("Server started at http://localhost:8081")
    #await broadcast_hello()
    asyncio.create_task(broadcast_hello())
    
    while True:
        await asyncio.sleep(60)
if __name__ == '__main__':
    asyncio.run(start_Server())