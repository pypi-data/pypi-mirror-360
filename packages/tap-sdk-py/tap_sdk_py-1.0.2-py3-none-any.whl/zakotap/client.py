from .utils import ClientData, VersionType, EmitterEvents
import asyncio
from .utils import EmitterManager
from .utils import open
from .utils import sendAudioData, sendError

BaseTabHubVersion: VersionType = {
    "Major": 1,
    "Minor": 0,
    "Patch": 0
}

class Client():
    def __init__(self, clientData: ClientData):
        self.name = clientData['name']
        self.token = clientData['token']
        self.zakoEndpoint = clientData.get('zakoEndpoint')
        self.clientEvent = EmitterManager()
        if not self.zakoEndpoint:
            self.zakoEndpoint = "https://api.zako.ac"

    def connect(self):
        asyncio.run(open(self.zakoEndpoint, self.name, self.token, BaseTabHubVersion, self.clientEvent))
    
    def on(self, event: EmitterEvents, listener):
        self.clientEvent.on(event, listener)
    
    async def send(self, id: str, audioStream):
        try:
            await sendAudioData(self.zakoEndpoint, id, audioStream)
        except Exception as e:
            await sendError(self.zakoEndpoint, id, str(e))
