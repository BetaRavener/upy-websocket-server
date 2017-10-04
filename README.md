# upy-websocket-server
Micropython (ESP8266) websocket server implementation.

Upload all scripts and HTML page to device and execute the `websocket_demo.py` script.

When client connects to the device, `test.html` is served to him, which in turn makes websocket connection to the device and greets it with `Hello`. The device acknowledges this and replies with ` World` appended, which makes client display `Hello World`.

New implementations can be made by subclassing `WebSocketClient` and `WebSocketServer` as shown in `websocket.py`.
