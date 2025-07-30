import asyncio
import socketio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("Connected to server")

@sio.event
async def disconnect():
    print("Disconnected from server")

@sio.event
async def ping(data):
    print("Received from server:", data)

async def main():
    await sio.connect("http://localhost:8081")
    await sio.wait()

if __name__ == "__main__":
    asyncio.run(main())