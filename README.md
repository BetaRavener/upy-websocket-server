# upy-websocket-server
Micropython (ESP8266) websocket server implementation.

Upload all scripts and HTML page to device and execute the `websocket_demo.py` script.

When client connects to the device, `test.html` is served to him, which in turn makes websocket connection to the device and greets it with `Hello`. The device acknowledges this and replies with ` World` appended, which makes client display `Hello World`.

New implementations can be made by subclassing `WebSocketClient` and `WebSocketServer` as shown in `websocket_demo.py`.

### ESP32 users
Because `setsockopt` can't be used on ESP32 to install event handlers, new implementation using `Poll` class has been made and is available in separate folder. From user perspective, both implementation behave the same. The folder contains only files that are different so don't forget to place other files from root folder on your ESP.

Also, if you're having problems importing `websocket` class, make sure that it's available in your firmware using following commands. `websocket` class should be listed in the output. 
```
import websocket # This is importing module, not class
dir(websocket) # List everything that module supports
```

Micropython [revision 0d5bccad](https://github.com/micropython/micropython/commit/0d5bccad) is confirmed to be working correctly.
Thanks for this goes to [@plugowski](https://github.com/plugowski).

### Support for multiple files
It is recommended to keep the page served by server simple as the transfer speed is quite slow. Due to this, the basic implementation supports serving only one HTML page and websocket communication. However, if you really need to use multiple files (images, etc.) you can find extended implementation in `Multiserver` folder. You only need `ws_multiserver.py` file. The rest of files are for demo purposes. If you want to try it out, copy all files from the mentioned folder and run `websocket_multi_demo.py`. The demo page consists of 3 images and CSS file which are all served along the HTML page and websocket communication that happens after content is loaded.


