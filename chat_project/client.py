import asyncio

async def chat_client(host: str = "127.0.0.1", port: int = 8888):
    reader, writer = await asyncio.open_connection(host, port)
    addr = writer.get_extra_info("peername")
    print(f"Подключено к {addr}")

    async def receiver():
        while True:
            data = await reader.read(1024)
            if not data:
                print("Сервер закрыл соединение.")
                break
            print(data.decode("utf-8", errors="ignore"), end="")

    recv_task = asyncio.create_task(receiver())

    try:
        while True:
            message = input()
            if message.strip().lower() in ("exit", "quit"):
                break
            writer.write((message + "\n").encode("utf-8"))
            await writer.drain()
    except KeyboardInterrupt:
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        recv_task.cancel()
        try:
            await recv_task
        except asyncio.CancelledError:
            pass
        print("Отключено от сервера.")

if __name__ == "__main__":
    asyncio.run(chat_client())
