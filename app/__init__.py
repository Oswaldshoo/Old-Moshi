from flask import Flask
from supabase import create_client, Client
from .config import Config
from .views import admin, academic, teacher, parent

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Supabase client (placeholder)
    #supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    #supabase: Client = create_client(app.config['SUPABASE_URL'], app.config['SUPABASE_KEY'])

    # Register blueprints
    app.register_blueprint(admin.bp)
    app.register_blueprint(academic.bp)
    app.register_blueprint(teacher.bp)
    app.register_blueprint(parent.bp)

    return app