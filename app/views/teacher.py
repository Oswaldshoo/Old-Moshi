from flask import Blueprint, jsonify, request, render_template, url_for, redirect, flash, session
from supabase import create_client, Client
from werkzeug.security import check_password_hash, generate_password_hash
import uuid

bp = Blueprint('teacher', __name__, url_prefix='/teacher')

# Define supabase_url and supabase_key variables
supabase_url = "https://xibexzbpueobbznwotlv.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpYmV4emJwdWVvYmJ6bndvdGx2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI1OTY1ODAsImV4cCI6MjAzODE3MjU4MH0.wzM6gsucXBpfRBQWRhJw5y5n1ReKeejyTLnC-2ahadM"

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

@bp.route('/')
def dashboard():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    teacher = supabase.table('teachers').select('*').eq('user_id', teacher_id).single().execute()
    
    if not teacher.data:
        flash('Teacher profile not found', 'error')
        return redirect(url_for('auth.login'))
    
    assigned_classes = supabase.table('teacher_assignments').select('classes(id, name)').eq('teacher_id', teacher.data['id']).execute()
    assigned_subjects = supabase.table('teacher_assignments').select('subjects(id, name)').eq('teacher_id', teacher.data['id']).execute()
    
    return render_template('teacher/dashboard.html', 
                           teacher=teacher.data,
                           classes=[c['classes'] for c in assigned_classes.data if c['classes']],
                           subjects=[s['subjects'] for s in assigned_subjects.data if s['subjects']])

@bp.route('/classes')
def view_classes():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    teacher = supabase.table('teachers').select('id').eq('user_id', teacher_id).single().execute()
    
    if not teacher.data:
        flash('Teacher profile not found', 'error')
        return redirect(url_for('auth.login'))
    
    # Fetch assigned classes
    assigned_classes = supabase.table('teacher_assignments')\
        .select('classes(id, name)')\
        .eq('teacher_id', teacher.data['id'])\
        .execute()
    
    # Fetch assigned subjects with their corresponding classes
    assigned_subjects = supabase.table('teacher_assignments')\
        .select('subjects(id, name), classes(id, name)')\
        .eq('teacher_id', teacher.data['id'])\
        .execute()
    
    # Process the data for the template
    classes = [c['classes'] for c in assigned_classes.data if c['classes']]
    subjects = [
        {
            'id': s['subjects']['id'],
            'name': s['subjects']['name'],
            'classes': s['classes']
        }
        for s in assigned_subjects.data if s['subjects'] and s['classes']
    ]
    
    return render_template('teacher/classes.html', 
                           classes=classes,
                           subjects=subjects)

@bp.route('/class/<class_id>')
def view_class(class_id):
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('auth.login'))
    
    class_info = supabase.table('classes').select('*').eq('id', class_id).single().execute()
    students = supabase.table('students').select('*').eq('class_id', class_id).execute()
    
    return render_template('teacher/class_detail.html', 
                           class_info=class_info.data,
                           students=students.data)

@bp.route('/upload-results', methods=['GET', 'POST'])
def upload_results():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    teacher = supabase.table('teachers').select('id').eq('user_id', teacher_id).single().execute()
    
    if not teacher.data:
        flash('Teacher profile not found', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        class_id = request.form['class_id']
        subject_id = request.form['subject_id']
        exam_type = request.form['exam_type']
        results = request.form['results']  # Assuming this is a JSON string
        
        # Process and save results
        new_results = supabase.table('results').insert({
            'teacher_id': teacher.data['id'],
            'class_id': class_id,
            'subject_id': subject_id,
            'exam_type': exam_type,
            'results': results
        }).execute()
        
        if new_results.data:
            flash('Results uploaded successfully', 'success')
        else:
            flash('Failed to upload results', 'error')
        
        return redirect(url_for('teacher.upload_results'))
    
    assigned_classes = supabase.table('teacher_assignments').select('classes(id, name)').eq('teacher_id', teacher.data['id']).execute()
    assigned_subjects = supabase.table('teacher_assignments').select('subjects(id, name)').eq('teacher_id', teacher.data['id']).execute()
    
    return render_template('teacher/upload_results.html',
                           classes=[c['classes'] for c in assigned_classes.data if c['classes']],
                           subjects=[s['subjects'] for s in assigned_subjects.data if s['subjects']])

@bp.route('/view-students')
def view_students():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    teacher = supabase.table('teachers').select('id').eq('user_id', teacher_id).single().execute()
    
    if not teacher.data:
        flash('Teacher profile not found', 'error')
        return redirect(url_for('auth.login'))
    
    assigned_classes = supabase.table('teacher_assignments').select('classes(id, name)').eq('teacher_id', teacher.data['id']).execute()
    class_ids = [c['classes']['id'] for c in assigned_classes.data if c['classes']]
    
    students = supabase.table('students').select('*, classes(name)').in_('class_id', class_ids).execute()
    
    return render_template('teacher/view_students.html', students=students.data)

@bp.route('/student/<student_id>')
def view_student(student_id):
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('auth.login'))
    
    student = supabase.table('students').select('*').eq('id', student_id).single().execute()
    if not student.data:
        flash('Student not found', 'error')
        return redirect(url_for('teacher.view_students'))
    
    class_info = supabase.table('classes').select('*').eq('id', student.data['class_id']).single().execute()
    
    return render_template('teacher/student_detail.html', 
                           student=student.data,
                           class_info=class_info.data)

@bp.route('/profile')
def profile():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('auth.login'))
    
    teacher_id = session.get('user_id')
    teacher = supabase.table('teachers').select('*').eq('user_id', teacher_id).single().execute()
    
    if not teacher.data:
        flash('Teacher profile not found', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('teacher/profile.html', teacher=teacher.data)

@bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        user = supabase.table('users').select('*').eq('id', session['user_id']).single().execute()
        
        if user.data and check_password_hash(user.data['password'], current_password):
            if new_password == confirm_password:
                # Update password
                supabase.table('users').update({'password': generate_password_hash(new_password)}).eq('id', session['user_id']).execute()
                flash('Password changed successfully', 'success')
                return redirect(url_for('teacher.profile'))
            else:
                flash('New passwords do not match', 'error')
        else:
            flash('Current password is incorrect', 'error')
    
    return render_template('teacher/change_password.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
