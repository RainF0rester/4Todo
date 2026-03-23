# Minimal Flask app
from apiflask import APIFlask
from db import init_db, close_session
from modules.tasks.routes import bp as tasks_bp
from modules.users.routes import bp as users_bp


# @app.route('/')
# def index():
#     return render_template('index.html')


def create_app():

    flaskapp = APIFlask(__name__)

    # create tables
    init_db()
    flaskapp.register_blueprint(tasks_bp)
    flaskapp.register_blueprint(users_bp)

    @flaskapp.teardown_appcontext
    def _teardown(exception):
        close_session()

    return flaskapp

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
