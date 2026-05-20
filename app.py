import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ATERNOS_USER    = os.environ.get("ATERNOS_USER", "")
ATERNOS_PASS    = os.environ.get("ATERNOS_PASS", "")
ATERNOS_SESSION = os.environ.get("ATERNOS_SESSION", "")
SECRET_TOKEN    = os.environ.get("SECRET_TOKEN", "changeme")


def get_server():
    from python_aternos import Client
    if ATERNOS_SESSION:
        at = Client.from_session(ATERNOS_SESSION)
    else:
        at = Client.from_credentials(ATERNOS_USER, ATERNOS_PASS)
    servers = at.list_servers()
    if not servers:
        raise Exception("No se encontró ningún servidor en la cuenta")
    return servers[0]


@app.route("/status")
def status():
    try:
        serv = get_server()
        return jsonify({"ok": True, "status": serv.status})
    except Exception as e:
        return jsonify({"ok": False, "status": "error", "error": str(e)})


@app.route("/start", methods=["POST"])
def start():
    token = request.headers.get("X-Token") or (request.json.get("token", "") if request.is_json else "")
    if token.lower() != SECRET_TOKEN.lower():
        return jsonify({"ok": False, "message": "Token inválido"}), 401
    try:
        serv = get_server()
        if serv.status == "online":
            return jsonify({"ok": True, "message": "El servidor ya estaba online", "status": "online"})
        serv.start()
        return jsonify({"ok": True, "message": "Servidor iniciando... puede tardar 2-3 minutos", "status": "starting"})
    except Exception as e:
        err = str(e)
        if "already" in err:
            return jsonify({"ok": True, "message": "El servidor ya estaba online", "status": "online"})
        return jsonify({"ok": False, "message": f"Error: {err}", "status": "error"})


@app.route("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
