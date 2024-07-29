from flask import Blueprint, jsonify, request, render_template

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')