import requests
from ._type import ErrorMessage

async def sendAudioData(url: str, id:str, audioStream):
    okUrl = f"{url}/data/{id}/ok"
    requests.post(okUrl, data=audioStream, stream=True)

async def sendPing(url: str, id: str):
    okUrl = f"{url}/data/{id}/ok"
    requests.post(okUrl)

async def sendError(url: str, id: str, errorMessage: str):
    errorUrl = f"{url}/data/{id}/err"
    errorMessage: ErrorMessage = {"message": errorMessage}
    requests.post(errorUrl, json=errorMessage)
