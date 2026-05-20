import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ATERNOS_SESSION = os.environ.get("ATERNOS_SESSION", "")
CF_CLEARANCE    = os.environ.get("CF_CLEARANCE", "")
SECRET_TOKEN    = os.environ.get("SECRET_TOKEN", "changeme")

BASE = "https://aternos.org"

def get_headers():
    cookie = f"ATERNOS_SESSION={ATERNOS_SESSION}; ATERNOS_LANGUAGE=en"
    if CF_CLEARANCE:
        cookie += f"; cf_clearance={CF_CLEARANCE}"
    return {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://aternos.org/server/",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

def get_server_info():
    r = requests.get(f"{BASE}/panel/ajax/account.php", headers=get_headers(), timeout=15)
    data = r.json()
    servers = data.get("servers", [])
    if not servers:
        raise Exception("No se encontró ningún servidor")
    return servers[0]


@app.route("/debug")
def debug():
    try:
        r = requests.get(f"{BASE}/panel/ajax/account.php", headers=get_headers(), timeout=15)
        return jsonify({
            "status_code": r.status_code,
            "content_type": r.headers.get("content-type", ""),
            "body_preview": r.text[:500],
        })
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/status")
def status():
    try:
        serv = get_server_info()
        return jsonify({
            "ok": True,
            "status": serv.get("status", "unknown"),
            "players": serv.get("players", 0),
        })
    except Exception as e:
        return jsonify({"ok": False, "status": "error", "error": str(e)})


@app.route("/start", methods=["POST"])
def start():
    token = request.headers.get("X-Token") or (request.json.get("token", "") if request.is_json else "")
    if token.lower() != SECRET_TOKEN.lower():
        return jsonify({"ok": False, "message": "Token inválido"}), 401
    try:
        serv = get_server_info()
        stat = serv.get("status", "")
        if stat == "online":
            return jsonify({"ok": True, "message": "El servidor ya estaba online", "status": "online"})
        if stat in ("starting", "loading", "preparing"):
            return jsonify({"ok": True, "message": "El servidor ya está iniciando", "status": stat})

        r = requests.get(
            f"{BASE}/panel/ajax/start.php",
            params={"headstart": 0, "access-credits": 0},
            headers=get_headers(),
            timeout=15
        )
        if r.status_code == 200:
            return jsonify({"ok": True, "message": "Servidor iniciando... puede tardar 2-3 minutos", "status": "starting"})
        else:
            return jsonify({"ok": False, "message": f"Aternos respondió {r.status_code}: {r.text[:200]}", "status": "error"})

    except Exception as e:
        return jsonify({"ok": False, "message": str(e), "status": "error"})


@app.route("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
