# hiplt/router.py

from typing import Callable, Dict, Any, Awaitable
import asyncio
import websockets
import json


class Router:
    """
    Минималистичный роутер HTTP и WebSocket запросов.
    """

    def __init__(self):
        self._http_routes: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self._ws_routes: Dict[str, Callable[..., Awaitable[Any]]] = {}

    def route(self, path: str):
        """
        Декоратор для HTTP маршрута.
        """
        def decorator(func: Callable[..., Awaitable[Any]]):
            self._http_routes[path] = func
            return func
        return decorator

    def ws_route(self, path: str):
        """
        Декоратор для WebSocket маршрута.
        """
        def decorator(func: Callable[..., Awaitable[Any]]):
            self._ws_routes[path] = func
            return func
        return decorator

    async def handle_http(self, path: str, data: dict = None):
        """
        Обработать HTTP запрос.
        """
        handler = self._http_routes.get(path)
        if not handler:
            return {"error": "Not Found"}, 404

        if asyncio.iscoroutinefunction(handler):
            return await handler(data)
        else:
            return handler(data)

    async def handle_ws(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """
        Обработать WebSocket соединение.
        """
        handler = self._ws_routes.get(path)
        if not handler:
            await websocket.send(json.dumps({"error": "WS route not found"}))
            await websocket.close()
            return
        await handler(websocket)


# Пример использования с websockets
if __name__ == "__main__":
    import websockets

    router = Router()

    @router.route("/hello")
    async def hello_handler(data):
        return {"message": "Hello from CSO router!"}

    @router.ws_route("/echo")
    async def echo_handler(ws):
        async for message in ws:
            await ws.send(message)

    async def main():
        async with websockets.serve(router.handle_ws, "localhost", 8765):
            print("WS server started at ws://localhost:8765")
            await asyncio.Future()  # run forever

    asyncio.run(main())