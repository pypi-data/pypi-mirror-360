import threading
import time
import json
import os
import sys
import httpx
from websocket import WebSocketApp
from .logger import saferates_log
GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
class SaferatesOnliner:
    def __init__(self, tokens, status="online", activity=None):
        if isinstance(tokens, str):
            tokens = [tokens]
        self.tokens = tokens
        self.status = status
        self.activity = activity
        self.threads = []
    def start(self):
        for token in self.tokens:
            t = threading.Thread(target=self._run, args=(token,), daemon=True)
            t.start()
            self.threads.append(t)
        saferates_log("Onliner", f"Started onliner for {len(self.tokens)} token(s).", level="SUCCESS")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            saferates_log("Onliner", "Shutting down onliner.", level="INFO")
            sys.exit(0)
    def _run(self, token):
        def on_open(ws):
            saferates_log("Onliner", "Gateway connection opened.", level="DEBUG")
        def on_message(ws, message):
            data = json.loads(message)
            op = data.get("op")
            t = data.get("t")
            if op == 10:
                heartbeat_interval = data["d"]["heartbeat_interval"] / 1000
                ws.send(json.dumps(self._identify_payload(token)))
                saferates_log("Onliner", "Sent IDENTIFY.", level="DEBUG")
                threading.Thread(target=self._heartbeat, args=(ws, heartbeat_interval), daemon=True).start()
            elif op == 11:
                saferates_log("Onliner", "Received HEARTBEAT_ACK.", level="DEBUG")
            elif t == "READY":
                username = data["d"]["user"]["username"]
                saferates_log("Onliner", f"{username} is now ONLINE.", level="SUCCESS")
        def on_close(ws, code, reason):
            saferates_log("Onliner", f"Gateway closed: {code} {reason}", level="WARN")
        def on_error(ws, error):
            saferates_log("Onliner", f"WebSocket error: {error}", level="ERROR")
        while True:
            try:
                ws = WebSocketApp(
                    GATEWAY_URL,
                    header={"Authorization": token},
                    on_open=on_open,
                    on_message=on_message,
                    on_close=on_close,
                    on_error=on_error,
                )
                ws.run_forever()
            except Exception as e:
                saferates_log("Onliner", f"Exception: {e}", level="ERROR")
            time.sleep(5)
    def _heartbeat(self, ws, interval):
        while True:
            try:
                ws.send(json.dumps({"op": 1, "d": None}))
                saferates_log("Onliner", "Sent HEARTBEAT.", level="DEBUG")
                time.sleep(interval)
            except Exception as e:
                saferates_log("Onliner", f"Heartbeat error: {e}", level="ERROR")
                break
    def _identify_payload(self, token):
        payload = {
            "op": 2,
            "d": {
                "token": token,
                "capabilities": 4093,
                "properties": {
                    "os": os.name,
                    "browser": "saferates",
                    "device": "saferates"
                },
                "presence": {
                    "status": self.status,
                    "since": 0,
                    "afk": False,
                    "activities": [self.activity] if self.activity else []
                },
                "compress": False,
                "client_state": {
                    "guild_versions": {},
                    "highest_last_message_id": "0",
                    "read_state_version": 0,
                    "user_guild_settings_version": -1,
                    "user_settings_version": -1
                }
            }
        }
        return payload
    def saferates_check_token(token):    
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Discord-iOS/2220.0.0 CFNetwork/1390 Darwin/22.0.0"
        }
        try:
            resp = httpx.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=10)
            if resp.status_code == 200:
                return "valid", resp.json().get("username")
            elif resp.status_code == 401:
                return "invalid", "Token unauthorized"
            elif resp.status_code == 403:
                data = resp.json()
                if data.get("message", "").lower().startswith("you need to verify your account"):
                    return "locked", "Account locked/phone verification required"
                if "banned" in data.get("message", "").lower() or "disabled" in data.get("message", "").lower():
                    return "banned", data.get("message", "Account banned or disabled")
                return "forbidden", data.get("message", "Forbidden")
            elif resp.status_code == 429:
                return "rate_limited", "Too many requests"
            else:
                return "unknown", f"HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            return "unknown", str(e)