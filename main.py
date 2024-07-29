from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from typing import List

app = FastAPI()

# Configurar CORS para permitir o acesso do Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # URL do seu app Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients: List[WebSocket] = []


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid4())
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message = {"clientId": data['clientId'], "message": data['message']}
            for client in clients:
                await client.send_json(message)
    except WebSocketDisconnect:
        clients.remove(websocket)
