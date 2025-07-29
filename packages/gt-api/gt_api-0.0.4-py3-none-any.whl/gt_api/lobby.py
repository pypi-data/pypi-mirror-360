from websockets.sync.client import connect
from websockets import ConnectionClosed
from . import generic
from .errors import LobbyError
from .client import Client
import threading
import json

CLIENT_VERSION = "0.297.17"


class Lobby:
    def __init__(self, connection, auth_token):
        self.connection = connection
        self.auth_token = auth_token
        self.thread = threading.Thread(target=self._event_loop)
        self.close_reason = "not yet started"
        self.running = False
        self.lobby_token = None
        self.lobby_id = None
        self.lobby_settings = None
        self.handlers = {"fullLobby": [self.handle_full_lobby]}

    def event_handler(self, event):
        def decorator(function):
            self.handlers.setdefault(event, [])
            self.handlers[event].append(function)
            return function

        return decorator

    def feed_event(self, message):
        for handler in self.handlers.get(message["type"], []) + self.handlers.get(
            "*", []
        ):
            threading.Thread(
                target=handler,
                args=(self, message["type"], message.get("data")),
            ).start()  # run in a separate thread so as to not block the event loop

    def run(self):
        if self.running:
            raise RuntimeError("already running")
        try:
            ack = generic.decode_websocket(self.connection.recv())
            self.feed_event(ack)
        except ConnectionClosed:
            self.close_reason = self.connection.close_reason
            raise LobbyError(
                f"Disconnected by server: {self.connection.close_reason}"
            ) from None
        self.running = True
        self.thread.start()

    def disconnect(self):
        self.connection.close()

    def lobby_api_request(self, url, method, *args, **kwargs):
        return generic.geotastic_api_request(
            url,
            method,
            self.auth_token,
            {"Game-Id": self.lobby_id, "Token": self.lobby_token},
            *args,
            **kwargs,
        )

    def _event_loop(self):
        while True:
            try:
                self.close_reason = self.connection.close_reason
                message = generic.decode_websocket(self.connection.recv())
                self.feed_event(message)
            except ConnectionClosed:
                self.running = False
                raise LobbyError(
                    f"Disconnected by server: {self.connection.close_reason}"
                ) from None

    def send_message(self, type, **kwargs):
        if not self.running:
            raise LobbyError(f"Lobby not running: {self.connection.close_reason}")
        payload = {
            "token": self.lobby_token,
            "gameId": self.lobby_id,
            "type": type,
            **kwargs,
        }

        self.connection.send(json.dumps(payload))

    @classmethod
    def create(cls, auth_token, server="multiplayer02"):
        sock = connect(
            f"wss://{server}.geotastic.net/?client_version={CLIENT_VERSION}&t={auth_token}&a=createNewCustomLobby",
            origin="https://geotastic.net",
            subprotocols=["geotastic-protocol"],
        )
        return cls(sock, auth_token)

    @classmethod
    def join(cls, auth_token, lobby_id, name="", server="multiplayer02"):
        sock = connect(
            f"wss://{server}.geotastic.net/?client_version={CLIENT_VERSION}&t={auth_token}&la={lobby_id}&n={name}&a=joinLobby",
            origin="https://geotastic.net",
            subprotocols=["geotastic-protocol"],
        )
        return cls(sock, auth_token)

    def handle_full_lobby(self, lobby, type, message):
        lobby.lobby_token = message["token"]
        lobby.lobby_id = message["lobby"]["id"]
        lobby.lobby_settings = message["lobby"]["settingsOptions"]["settings"]


@Client._register_endpoint
def get_lobby_from_alias(alias, auth_token=None):
    return generic.process_response(
        generic.geotastic_api_request(
            "https://api.geotastic.net/v1/lobby/getLobbyFromAlias.php",
            "GET",
            auth_token,
            params={"alias": alias},
        )
    )
