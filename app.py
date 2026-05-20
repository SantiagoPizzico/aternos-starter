import os
import asyncio
from flask import Flask, jsonify, request
from flask_cors import CORS
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

ATERNOS_USER = os.environ.get("ATERNOS_USER", "")
ATERNOS_PASS = os.environ.get("ATERNOS_PASS", "")
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "changeme")

status_cache = {"status": "unknown", "players": 0, "max_players": 20}


async def get_server_status():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        try:
            await page.goto("https://aternos.org/go/", timeout=30000)
            await page.fill("#user", ATERNOS_USER)
            await page.fill("#password", ATERNOS_PASS)
            await page.click(".login-button")
            await page.wait_for_load_state("networkidle", timeout=20000)

            # Navegar al panel del servidor
            await page.goto("https://aternos.org/server/", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=20000)

            # Intentar obtener el estado
            status_el = await page.query_selector(".statuslabel-label")
            status_text = "unknown"
            if status_el:
                status_text = (await status_el.inner_text()).strip().lower()

            return {"status": status_text, "ok": True}
        except Exception as e:
            return {"status": "error", "error": str(e), "ok": False}
        finally:
            await browser.close()


async def start_server():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        try:
            await page.goto("https://aternos.org/go/", timeout=30000)
            await page.fill("#user", ATERNOS_USER)
            await page.fill("#password", ATERNOS_PASS)
            await page.click(".login-button")
            await page.wait_for_load_state("networkidle", timeout=20000)

            await page.goto("https://aternos.org/server/", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=20000)

            # Verificar estado actual
            status_el = await page.query_selector(".statuslabel-label")
            current_status = ""
            if status_el:
                current_status = (await status_el.inner_text()).strip().lower()

            if "online" in current_status:
                return {"ok": True, "message": "El servidor ya estaba online", "status": "online"}

            if "starting" in current_status or "loading" in current_status:
                return {"ok": True, "message": "El servidor ya está iniciando", "status": "starting"}

            # Click en el botón de start (queue o start directo)
            start_btn = await page.query_selector("#start")
            if not start_btn:
                start_btn = await page.query_selector(".btn-green")

            if start_btn:
                await start_btn.click()
                await page.wait_for_timeout(3000)

                # Si aparece modal de cola, confirmarlo
                confirm_btn = await page.query_selector(".btn-queue, #confirm-queue, .queue-button")
                if confirm_btn:
                    await confirm_btn.click()
                    await page.wait_for_timeout(2000)

                return {"ok": True, "message": "Servidor iniciando... puede tardar 2-3 minutos", "status": "starting"}
            else:
                return {"ok": False, "message": "No se encontró el botón de inicio", "status": current_status}

        except Exception as e:
            return {"ok": False, "message": f"Error: {str(e)}", "status": "error"}
        finally:
            await browser.close()


@app.route("/status")
def status():
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(get_server_status())
    loop.close()
    return jsonify(result)


@app.route("/start", methods=["POST"])
def start():
    token = request.headers.get("X-Token") or request.json.get("token", "") if request.is_json else ""
    if token.lower() != SECRET_TOKEN.lower():
        return jsonify({"ok": False, "message": "Token inválido"}), 401

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(start_server())
    loop.close()
    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
