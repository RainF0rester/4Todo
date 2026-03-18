# Minimal Flask app
from apiflask import APIFlask
from db import init_db, close_session
from modules.tasks.routes import bp as tasks_bp


# @app.route('/')
# def index():
#     return render_template('index.html')

app = APIFlask(__name__)

def create_app():
    # create tables
    init_db()
    app.register_blueprint(tasks_bp)

    @app.teardown_appcontext
    def _teardown(exception):
        close_session()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
