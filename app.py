from flask import Flask

from routes import home_bp


app = Flask(__name__, instance_relative_config=False)
app.register_blueprint(home_bp)
