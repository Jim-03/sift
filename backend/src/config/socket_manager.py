from fastapi import Depends, WebSocket, WebSocketDisconnect


class SocketManager:
    """Configuration to manage websocket connections"""

    def __init__(self):
        self.clients: list[WebSocket] = []

    async def add_connection(self, client: WebSocket):
        """Add a new live connection with the client

        Args:
            client: Websocket connection
        """
        self.clients.append(client)

        try:
            await client.accept()

            while True:
                await client.receive_text()
        except WebSocketDisconnect:
            await client.close()
            self.clients.remove(client)


SocketManagerDep = Depends(SocketManager)
