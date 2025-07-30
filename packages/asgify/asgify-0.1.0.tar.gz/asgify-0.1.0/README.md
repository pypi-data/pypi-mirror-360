# asgify

Opinionless ASGI Framework 🙌

## 📦 Installation

### Using pip

```bash
pip install asgify
```

### Using uv (Recommended)

```bash
uv add asgify
```

### From Source

```bash
git clone https://github.com/aprilahijriyan/asgify.git
cd asgify
pip install -e .
```

## 🚀 Showcase

### HTTP Application Example

```python
import json
from asgify.app import Asgify
from asgify.context import HTTPContext
from asgify.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_STATUS_CODES


async def http_handler(ctx: HTTPContext):
    # Get path and method
    path = ctx.path
    method = ctx.method

    if path == "/" and method == "GET":
        await ctx.start(HTTP_200_OK, {"content-type": "application/json"})
        await ctx.end(json.dumps({"message": "Hello from asgify!"}).encode())

    elif path.startswith("/users/") and method == "GET":
        user_id = path.split("/users/")[-1]
        page = ctx.params.get("page", "1")

        await ctx.start(HTTP_200_OK, {"content-type": "application/json"})
        await ctx.end(
            json.dumps({"user_id": user_id, "page": page, "status": "active"}).encode()
        )

    elif path == "/api/data" and method == "POST":
        # Read JSON body
        body = b""
        async for chunk in ctx.read_body():
            body += chunk

        data = json.loads(body.decode())

        await ctx.start(HTTP_201_CREATED, {"content-type": "application/json"})
        await ctx.end(json.dumps({"created": True, "data": data}).encode())

    else:
        await ctx.start(HTTP_404_NOT_FOUND, {"content-type": "text/plain"})
        await ctx.end(HTTP_STATUS_CODES[HTTP_404_NOT_FOUND].encode())


app = Asgify(http=http_handler)

```

To run the HTTP server example above using [uvicorn](https://www.uvicorn.org/), save the code to a file (for example, `showcase_http.py`) and run the following command in your terminal:

```sh
uvicorn showcase_http:app
```

### WebSocket Application Example

```python
import json
from datetime import datetime

from asgify.app import Asgify
from asgify.context import WebSocketContext
from asgify.errors import ClientDisconnected


async def websocket_handler(ctx: WebSocketContext):
    await ctx.accept()
    await ctx.send_bytes("Welcome to asgify 🚀".encode())
    while True:
        try:
            data = await ctx.receive_text()
            print("<", data)
            reply = json.dumps({"echo": data, "timestamp": datetime.now().isoformat()})
            await ctx.send_text(reply)
            print(">", reply)
        except ClientDisconnected:
            print("disconnected with client")
            break

app = Asgify(websocket=websocket_handler)
```

To run the WebSocket server example above using [uvicorn](https://www.uvicorn.org/), save the code to a file (for example, `showcase_websocket.py`) and run the following command in your terminal:

```sh
uvicorn showcase_websocket:app
```

Testing with [wscat](https://github.com/websockets/wscat/):

```sh
❯ wscat -P -c http://localhost:8000
Connected (press CTRL+C to quit)
< Welcome to asgify 🚀
> hehehe
< {"echo": "hehehe", "timestamp": "2025-07-08T13:06:34.899579"}
> %
```

## ✨ Cool Features

### 🚀 **Zero Overhead**

- Pure ASGI implementation with minimal dependencies
- No magic, no hidden costs - what you write is what you get

### ⚡ **Async-First Architecture**

- Built from the ground up for async/await
- Non-blocking I/O for maximum performance

### 🎯 **Context Classes That Rock**

```python
# HTTP Context - Simple & Powerful
await ctx.start(HTTP_200_OK, {"content-type": "application/json"})
await ctx.end(json.dumps({"message": "Hello World"}).encode())

# WebSocket Context - Real-time Ready
await ctx.accept()
message = await ctx.receive_text()
await ctx.send_text(f"Echo: {message}")
```

### 🎨 **Customizable Everything**

- Swap context classes for your needs
- Custom lifespan handlers for app lifecycle
- Full control over request/response flow

### 📦 **Minimal Dependencies**

- Only `asgiref` and `fast-query-parsers`
- No bloat, no surprises

### 🔧 **Developer Experience**

- Clean, intuitive API
- Comprehensive status codes (HTTP + WebSocket)
- Built-in query parameter parsing
- Application state management
