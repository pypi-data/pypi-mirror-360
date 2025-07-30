import websockets
import json
from .event import EmitterManager
from .response import sendPing
from ._type import HelloData, HelloResponse, VersionType, AudioRequest

async def open(url: str, name: str, token: str, version: VersionType, Event: EmitterManager):
    wsUrl = url.replace("http", "ws")
    try:
        async with websockets.connect(wsUrl + "/gateway") as websocket:
            helloData: HelloData = {
                "name": name,
                "token": token
            }
            await websocket.send(json.dumps(helloData))
            response: HelloResponse = json.loads(await websocket.recv())
            if response.get("ok"):
                tabHubVersion = response.get("version")
                tabHubVersionParts = tabHubVersion.split(".")
                if int(tabHubVersionParts[0]) == version.get("Major"):
                    if int(tabHubVersionParts[1]) != version.get("Minor") or int(tabHubVersionParts[2]) != version.get("Patch"):
                        Event.emit("warn", f"The supported tap hub version and the current tap hub version are different. TabHub version {tabHubVersion} | Supported version  {version['Major']}.{version['Minor']}.{version['Patch']}")
                    Event.emit("ready", response)
                    async for message in websocket:
                        audioRequest: AudioRequest = json.loads(message)
                        if audioRequest.get("ping"):
                            await sendPing(url, audioRequest.get("id"))
                        else:
                            Event.emit("audio", audioRequest)
                    Event.emit("close", "WebSocket connection closed normally.")
                else:
                    Event.emit("error", f"You are not on a supported tab hub version. TabHub version {tabHubVersion} | Supported version  {version['Major']}.{version['Minor']}.{version['Patch']}")
                    return
            else:
                Event.emit("error", response.get("message"))
                return
    except websockets.ConnectionClosedError as e:
        Event.emit("error", f"Connection closed with error: {e}")
        return
    except Exception as e:
        Event.emit("error", f"An error occurred: {e}")
        return
