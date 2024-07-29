from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict
import uuid

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

# Dicionário para manter as conexões e seus IDs
connections: Dict[str, WebSocket] = {}
# Dicionário para mapear WebSocket para ID
websocket_to_id: Dict[WebSocket, str] = {}


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Gerar um ID único para a nova conexão
    connection_id = str(uuid.uuid4())
    # Aceitar a conexão WebSocket
    await websocket.accept()
    # Adicionar a nova conexão e seu ID à lista
    connections[connection_id] = websocket
    websocket_to_id[websocket] = connection_id

    try:
        while True:
            # Receber uma mensagem do cliente
            data = await websocket.receive_text()
            # Enviar a mensagem para todos os clientes conectados, incluindo o remetente, com o ID de conexão
            sender_id = websocket_to_id[websocket]
            for conn_id, connection in connections.items():
                await connection.send_text(f"{sender_id}: {data}")
    except WebSocketDisconnect:
        # Remover a conexão da lista quando o cliente desconectar
        connections.pop(websocket_to_id[websocket], None)
        websocket_to_id.pop(websocket, None)
