from flask import Blueprint, jsonify, request,render_template

bp = Blueprint('academic', __name__, url_prefix='/academic')

@bp.route('/')
def dashboard():
    return render_template('academic/dashboard.html')