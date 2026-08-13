# Minimal Flask app
from apiflask import APIFlask
from flask_cors import CORS
from flask_socketio import SocketIO
from backend.db import init_db, close_session
from backend.modules.tasks.routes import bp as tasks_bp
from backend.modules.users.routes import bp as users_bp
from backend.modules.pomodoro.route import bp as pomodoro_bp
from backend.modules.ai.route import bp as ai_bp

socketio = SocketIO()

def create_app():

    flaskapp = APIFlask(__name__)
    flaskapp.config["SECURITY_SCHEMES"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    CORS(flaskapp, origins=["http://4todo.site", "https://4todo.site", "https://4todo.pages.dev", "http://localhost:5173"], supports_credentials=True, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

    socketio.init_app(flaskapp, cors_allowed_origins="*", async_mode="threading", manage_session=False)

    # create tables
    init_db()
    flaskapp.register_blueprint(tasks_bp)
    flaskapp.register_blueprint(users_bp)
    flaskapp.register_blueprint(pomodoro_bp)
    flaskapp.register_blueprint(ai_bp)

    from backend.modules.ai.socket import register_handlers
    register_handlers(socketio)

    @flaskapp.teardown_appcontext
    def _teardown(exception):
        close_session()

    return flaskapp

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host="0.0.0.0", port=5077, allow_unsafe_werkzeug=True)
