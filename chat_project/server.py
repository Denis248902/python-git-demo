import asyncio
import logging
from datetime import datetime
from typing import Dict, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class ChatServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8888):
        self.host = host
        self.port = port
        self.clients: Dict[asyncio.StreamWriter, str] = {}
        self.writers: Set[asyncio.StreamWriter] = set()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        logger.info(f"Новое подключение от {addr}")

        username = f"User_{id(writer)}"
        self.clients[writer] = username
        self.writers.add(writer)

        try:
            greeting = f"Добро пожаловать, {username}! Вы в чате.\n"
            writer.write(greeting.encode("utf-8"))
            await writer.drain()

            join_msg = f"[SYSTEM] {username} присоединился к чату.\n"
            await self.broadcast(join_msg, exclude=writer)

            while True:
                data = await reader.read(1024)
                if not data:
                    break

                message = data.decode("utf-8", errors="ignore").strip()
                if not message:
                    continue

                if message.startswith("/"):
                    if message == "/help":
                        help_text = (
                            "Доступные команды:\n"
                            "/nick <имя> — сменить имя\n"
                            "/help — показать эту справку\n"
                        )
                        writer.write((help_text + "\n").encode("utf-8"))
                        await writer.drain()
                        continue
                    elif message.startswith("/nick "):
                        new_name = message[len("/nick "):].strip()
                        if new_name:
                            old_name = self.clients[writer]
                            self.clients[writer] = new_name
                            change_msg = f"[SYSTEM] {old_name} сменил имя на {new_name}.\n"
                            await self.broadcast(change_msg)
                            logger.info(f"{old_name} -> {new_name}")
                        continue

                now = datetime.now().strftime("%H:%M:%S")
                formatted = f"[{username}, {now}] {message}\n"
                await self.broadcast(formatted)

        except Exception as e:
            logger.exception(f"Ошибка при работе с клиентом {addr}: {e}")
        finally:
            await self.remove_client(writer, username)

    async def remove_client(self, writer: asyncio.StreamWriter, username: str):
        if writer in self.writers:
            self.writers.remove(writer)
        if writer in self.clients:
            del self.clients[writer]

        writer.close()
        await writer.wait_closed()

        leave_msg = f"[SYSTEM] {username} покинул чат.\n"
        await self.broadcast(leave_msg)
        logger.info(f"Клиент {username} отключён")

    async def broadcast(self, message: str, exclude: asyncio.StreamWriter = None):
        dead_writers = []
        for w in self.writers:
            if w is exclude:
                continue
            try:
                w.write(message.encode("utf-8"))
                await w.drain()
            except Exception:
                dead_writers.append(w)

        for w in dead_writers:
            await self.remove_client(w, self.clients.get(w, "Unknown"))

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        addr = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        logger.info(f"Сервер запущен на {addr}")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = ChatServer(host="0.0.0.0", port=8888)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
