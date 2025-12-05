from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from web_app.routes.main import main_bp
    from web_app.routes.simulation import simulation_bp
    from web_app.routes.analysis import analysis_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(analysis_bp)

    return app
