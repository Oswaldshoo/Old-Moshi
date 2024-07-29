from flask import Flask
from .config import Config
from .views import admin, academic, teacher, parent

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Supabase client (placeholder)
    # supabase = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

    # Register blueprints
    app.register_blueprint(admin.bp)
    app.register_blueprint(academic.bp)
    app.register_blueprint(teacher.bp)
    app.register_blueprint(parent.bp)

    return app