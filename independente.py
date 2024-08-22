from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict
import uuid

"""
POR QUE USAR "connections" E "websocket_to_id" NO MESMO CÓDIGO?

Se o sistema precisar acessar as conexões WebSocket com frequência usando apenas o ID da conexão 
(e não o próprio WebSocket), o dicionário connections pode ser útil. 
Isso evita a necessidade de fazer uma busca reversa no dicionário websocket_to_id para encontrar o WebSocket 
correspondente a um ID específico, o que poderia ser ineficiente se o número de conexões for grande.

Exemplo: Se você estiver implementando uma lógica onde precisa enviar mensagens diretamente para um WebSocket 
específico com base no ID de conexão (por exemplo, notificações/mensagens personalizadas para usuários específicos), 
o uso de connections permitiria um acesso direto e mais eficiente ao WebSocket associado a um determinado ID.

OBS: Enviar mensagens personalizadas para usuários específicos (chat privado) seria um bom motivo para usar 
"connections" e "websocket_to_id".
"""

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
            # for connection, conn_id in websocket_to_id.items():  # -> Utilizando apenas o websocket_to_id
            for conn_id, connection in connections.items():
                await connection.send_text(f"{sender_id}: {data}")
    except WebSocketDisconnect:
        # Remover a conexão da lista quando o cliente desconectar
        connections.pop(websocket_to_id[websocket], None)
        websocket_to_id.pop(websocket, None)


# Exemplo de notificação/mensagem personalizada para usário específico:
async def send_notification(user_id: str, message: str):
    if user_id in connections:
        await connections[user_id].send_text(message)
