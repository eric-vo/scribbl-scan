from flask import Flask
from flask_mysqldb import MySQL

# DB CONNECTION HERE If WANTED

''' modular import of bps
bps = ['.routes:home',
        'app.auth:auth',
        'appadmin:admin'
        ]
'''

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    # app.config.from_object('config.Config')

    # SECRETE KEY, SQL HOST, USE, PSWD> PORT

    from routes import home_bp
    # ^ BP ROUTES INIT
    app.register_blueprint(home_bp)
    # REGISTER BP

    return app


app = create_app()
app.config["TEMPLATES_AUTO_RELOAD"] = True # make sure templates are auto reloaded

if __name__ == '__main__':
    app.run(debug=True)