from flask import Blueprint, jsonify, request,render_template

bp = Blueprint('teacher', __name__, url_prefix='/teacher')

@bp.route('/')
def dashboard():
    return render_template('teacher/dashboard.html')