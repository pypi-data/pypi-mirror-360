# Ascender LiveAPI Protocol (ALP)

Ascender LiveAPI Protocol (ALP) is a structured, Socket.IO-based event system for real-time communication between clients and backend services. It is simple and easy-to-use implementation of SocketIO into Ascender Framework with framework's architecture and DI support.

---

## Getting Started

### Prerequisites

Ensure you have the following dependencies installed:

- **Python 3.11 or higher**
- **Ascender Framework 2.0 or higher**
- **Poetry** (for dependency management)
- **pip** (Python's package manager)

### Installation

1. **Initiate Ascender Framework Project** (if not already):

   ```bash
   ascender new --name example-alp
   ...
   cd example-alp
   ```

2. **Add ALP as a package to the project**:

   ```bash
   poetry add ascender-alp
   ```

3. **Add provider in bootstrap**:
   In `src/bootstrap.py` add
   ```py
   # src/bootstrap.py
   from alp import provideALP
   from ascender.core.types import IBootstrap

   appBootstrap: IBootstrap = {
      "providers": [
         provideALP()
      ]
   }
   ```

4. **Add an ALPReceiver in your controller**:
   To handle incoming events/messages, use decorator `@ALPReceiver` in your controller.
   ```py
   from alp import ALPReceiver

   @Controller(
      standalone=True,
   )
   class ChatGateway:

      @ALPReceiver("connect", namespace="/chats")
      async def handle_connect(self, sid: str):
         print(f"[ALP] Client connected: {sid}")

      @ALPReceiver("chat-toggle", namespace="/chats")
      async def toggle_chat(self, sid: str, data: UUID):
         print(f"[ALP] Chat toggled: {data}")
         return {"status": "ok"}
   ```

5. **Emit event / Send message via Transmitter**:
   If you need to send message or emit any event, you can use ALP's `TransmitterModule` and `Transmitter` object. To use `Transmitter` object, you should import `TransmitterModule` in your `AscModule` or `Controller` if one is standalone specifying namespace if required.

   ```py
   from alp import TransmitterModule, ALPReceiver, Transmitter
   from ascender.common import BaseDTO

   class MessageDTO(BaseDTO):
      sender_id: str
      message: str
   

   @Controller(
      standalone=True,
      imports=[
         TransmitterModule.with_namespace("/chats")
      ]
   )
   class ChatGateway:

      def __init__(self, transmitter: Transmitter):
         self.transmitter = transmitter

      @ALPReceiver("connect", namespace="/chats")
      async def handle_connect(self, sid: str):
         await self.transmitter.emit("message", MessageDTO(sender_id=sid, message=f"User {sid} joined the chat."), room="cool_convo", namespace="/chat")

         await self.transmitter.enter_room(sid, "cool_convo", namespace="/chat")
         print(f"[ALP] Client connected: {sid}")

      @ALPReceiver("message", namespace="/chats")
      async def handle_message(self, sid: str, data: MessageDTO):
         await self.transmitter.emit("message", data, room="cool_convo", namespace="/chat")
         return {"status": "ok"}
   ```

If everything works, you're done!

## Roadmap
- [x] Typescript ALP Client
- [ ] CLI generator for ALP based controllers
- [ ] Built-in reconnection helpers
- [ ] Websocket testing utils
- [ ] Native websocket support
- [ ] Additional transportation protocols support

## License
MIT © 2025 Ascender Projects

## Get Involved
Have feedback?
Submit issues, PRs, or ideas - let’s make real-time Ascender-native and beautiful.
Don’t forget to star ⭐ the repo if you like it.