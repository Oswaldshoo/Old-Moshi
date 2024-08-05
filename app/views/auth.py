# app/views/auth.py
from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash
from supabase import create_client, Client

bp = Blueprint('auth', __name__, url_prefix='/auth')

supabase_url = "https://xibexzbpueobbznwotlv.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpYmV4emJwdWVvYmJ6bndvdGx2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI1OTY1ODAsImV4cCI6MjAzODE3MjU4MH0.wzM6gsucXBpfRBQWRhJw5y5n1ReKeejyTLnC-2ahadM"
supabase: Client = create_client(supabase_url, supabase_key)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = supabase.table('users').select('*').eq('email', email).execute()
        
        if user and user.data and check_password_hash(user.data[0]['password'], password):
            session['user_id'] = user.data[0]['id']
            session['user_role'] = user.data[0]['role']
            flash('Logged in successfully.', 'success')
            
            # Redirect based on user role
            if user.data[0]['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.data[0]['role'] == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif user.data[0]['role'] == 'academic':
                return redirect(url_for('academic.dashboard'))
            else:
                flash('Unknown user role.', 'error')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = 'admin'  # Change this to match your database constraints
        
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        
        if existing_user and existing_user.data:
            flash('Email already registered.', 'error')
        else:
            hashed_password = generate_password_hash(password)
            try:
                new_user = supabase.table('users').insert({
                    'email': email,
                    'password': hashed_password,
                    'role': role
                }).execute()
                
                if new_user and new_user.data:
                    flash('Registration successful. Please log in.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash('Registration failed. Please try again.', 'error')
            except Exception as e:
                flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
