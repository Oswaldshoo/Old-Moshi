from flask import Flask, redirect, url_for
from supabase import create_client, Client
from .config import Config
from .views import admin, academic, teacher, parent, auth

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
    app.register_blueprint(auth.bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app