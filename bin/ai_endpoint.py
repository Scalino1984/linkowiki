from flask import request, jsonify
from tools.session.manager import load_session
from tools.ai.assistant import run_ai

def register_ai(app):
    @app.route("/ai", methods=["POST"])
    def ai_endpoint():
        s = load_session()
        if not s:
            return jsonify({"error": "no session"}), 403

        data = request.json
        prompt = data.get("prompt")
        result = run_ai(prompt, s["files"])

        return jsonify(result.dict())
