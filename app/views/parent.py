from flask import Blueprint, jsonify, request,render_template

bp = Blueprint('parent', __name__, url_prefix='/parent')

@bp.route('/')
def dashboard():
    return render_template('parent/dashboard.html')