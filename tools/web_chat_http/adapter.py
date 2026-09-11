"""Opt-in HTTP handler extension. Existing server.py stays unchanged."""
from http.server import ThreadingHTTPServer

from tools.web_inquiry.server import Handler, Refused
from tools.web_chat_guard.guard import InvalidRequest, MAX_BODY_BYTES


class ChatHandler(Handler):
    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def do_POST(self):
        if self.path != "/api/chat":
            return super().do_POST()
        self.close_connection = True
        try:
            self.check_host()
            if self.headers.get_all("Origin", []) != [self.server.app.origin]:
                raise Refused(403, "Origin not allowed / Origen no permitido")
            if len(self.headers.get_all("Host", [])) != 1:
                raise Refused(400, "Invalid request / Solicitud no valida")
            if self.headers.get("Transfer-Encoding"):
                raise Refused(400, "Unsupported transfer / Transferencia no admitida")
            if self.headers.get_content_type() != "application/json":
                raise Refused(415, "JSON required / Se requiere JSON")
            lengths = self.headers.get_all("Content-Length", [])
            if len(lengths) != 1 or not lengths[0].isascii() or not lengths[0].isdigit():
                raise Refused(400, "Invalid size / Tamano no valido")
            size = int(lengths[0])
            if not 0 < size <= MAX_BODY_BYTES:
                raise Refused(413, "Message too large / Mensaje demasiado largo")
            body = self.rfile.read(size)
            if len(body) != size:
                raise Refused(400, "Incomplete request / Solicitud incompleta")
            result = self.server.chat.respond(body, self.rate_address)
            code = result.get("status")
            status = {"CHAT_DUPLICATE": 409, "CHAT_RATE_LIMITED": 429,
                      "CHAT_CAPACITY_REACHED": 429, "CHAT_INVALID_REQUEST": 400,
                      "CHAT_ACCOUNTING_UNAVAILABLE": 503}.get(code, 200)
            return self.reply(status, result)
        except InvalidRequest:
            self.reply(400, {"error": "Invalid chat request / Solicitud no valida"})
        except Refused as error:
            self.reply(error.status, {"error": error.message})
        except Exception:
            # Provider or storage details must never appear in the public API.
            self.reply(503, {"error": "Please call Santa / Por favor llame a Santa",
                             "phone": "786-975-9557"})


class ChatServer(ThreadingHTTPServer):
    daemon_threads = False

    def __init__(self, address, app, chat):
        self.app, self.chat = app, chat
        super().__init__(address, ChatHandler)
