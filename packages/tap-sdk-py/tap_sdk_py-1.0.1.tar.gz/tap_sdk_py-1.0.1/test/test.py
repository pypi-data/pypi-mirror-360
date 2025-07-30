import io
import asyncio
from zakotap import Client, ClientData, HelloResponse, AudioRequest

streamFile = io.BytesIO(b"test audio data")

clientData: ClientData = {
    "name": "your tap name",
    "token": "your tap token",
    "zakoEndpoint": "zako endpoint (default is https://api.zako.ac)"
}

client = Client(clientData)

def on_ready(data: HelloResponse):
    print("Client is ready. Connected Tab Hub version", data.get("version"))

def on_close(message: str):
    print("Connection closed:", message)

def on_warn(message: str):
    print("Warning:", message)

def on_error(message: str):
    print("Error:", message)

def on_audio_sync(audio_request: AudioRequest):
    print("Audio")
    loop = asyncio.get_event_loop()
    task = loop.create_task(on_audio(audio_request))

async def on_audio(audio_request: AudioRequest):
    print("Received audio request:", audio_request, flush = True)
    await client.send(audio_request.get("id"), streamFile)

client.on("warn", on_warn)
client.on("error", on_error)
client.on("ready", on_ready)
client.on("close", on_close)
client.on("audio", on_audio_sync)

client.connect()
