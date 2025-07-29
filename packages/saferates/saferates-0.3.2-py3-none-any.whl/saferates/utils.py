import urllib.parse
import json
import base64
from .logger import saferates_log
import httpx
def saferates_encode_emoji(emoji):
    if emoji.startswith("<:") or emoji.startswith("<a:"):
        parts = emoji.strip("<>").split(":")
        if len(parts) == 3:
            name, eid = parts[1], parts[2]
            return f"{name}:{eid}"
    return urllib.parse.quote(emoji)
def saferates_pretty_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)
def saferates_image_to_base64(filepath):
    with open(filepath, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = filepath.split(".")[-1].lower()
    return f"data:image/{ext};base64,{b64}"
def saferates_send_typing(api, channel_id):
    saferates_log("Sending typing indicator", f"channel_id={channel_id}")
    return api.post(f"/channels/{channel_id}/typing")
def saferates_upload_file(api, channel_id, filepath, content=None):
    saferates_log("Uploading file", f"channel={channel_id}, file={filepath}")
    with open(filepath, "rb") as f:
        files = {"file": (filepath, f)}
        data = {"content": content or ""}
        return api.post(f"/channels/{channel_id}/messages", files=files, data=data)