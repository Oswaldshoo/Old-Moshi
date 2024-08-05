from flask import Blueprint, jsonify, request, render_template, url_for, redirect, flash, session
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import logging

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Define supabase_url and supabase_key variables
supabase_url = "https://xibexzbpueobbznwotlv.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhpYmV4emJwdWVvYmJ6bndvdGx2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI1OTY1ODAsImV4cCI6MjAzODE3MjU4MH0.wzM6gsucXBpfRBQWRhJw5y5n1ReKeejyTLnC-2ahadM"

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

@bp.before_request
def require_login():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@bp.route('/')
def dashboard():
    num_subjects = supabase.table('subjects').select('id', count='exact').execute()
    num_classes = supabase.table('classes').select('id', count='exact').execute()
    num_teachers = supabase.table('teachers').select('id', count='exact').execute()
    num_students = supabase.table('students').select('id', count='exact').execute()

    return render_template('admin/dashboard.html',
                           num_subjects=num_subjects.count if num_subjects else 0,
                           num_classes=num_classes.count if num_classes else 0,
                           num_teachers=num_teachers.count if num_teachers else 0,
                           num_students=num_students.count if num_students else 0)

@bp.route('/subjects')
def manage_subjects():
    subjects = supabase.table('subjects').select('id, name, code, class_id').execute()
    classes = supabase.table('classes').select('id, name').execute()
    class_dict = {c['id']: c['name'] for c in classes.data}

    for subject in subjects.data:
        subject['class'] = class_dict.get(subject['class_id'], 'Unknown')

    class_data = {c['name']: c['id'] for c in classes.data}

    return render_template('admin/subjects.html', subjects=subjects.data, class_data=class_data)

@bp.route('/add-subject', methods=['POST'])
def add_subject():
    subject_name = request.form['subject_name']
    subject_code = request.form['subject_code']
    class_name = request.form['subject_class']

    class_result = supabase.table('classes').select('id').eq('name', class_name).single().execute()

    if not class_result.data:
        flash('Invalid class selected', 'error')
        return redirect(url_for('admin.manage_subjects'))

    class_id = class_result.data['id']

    supabase.table('subjects').insert({
        'name': subject_name,
        'code': subject_code,
        'class_id': class_id
    }).execute()

    flash('Subject added successfully', 'success')
    return redirect(url_for('admin.manage_subjects'))

@bp.route('/classes')
def classes():
    classes = supabase.table('classes').select('*').execute()
    streams = supabase.table('streams').select('*').execute()
    class_data = {c['name']: [s['name'] for s in streams.data if s['class_id'] == c['id']] for c in classes.data}
    return render_template('admin/classes.html', class_data=class_data)

@bp.route('/add-stream', methods=['POST'])
def add_stream():
    class_name = request.form['class_name']
    stream_name = request.form['stream_name']
    class_data = supabase.table('classes').select('id').eq('name', class_name).execute()
    if class_data.data:
        supabase.table('streams').insert({
            'name': stream_name,
            'class_id': class_data.data[0]['id']
        }).execute()
    return redirect(url_for('admin.classes'))

@bp.route('/add-class', methods=['POST'])
def add_class():
    class_name = request.form['class_name']
    supabase.table('classes').insert({'name': class_name}).execute()
    return redirect(url_for('admin.classes'))

@bp.route('/class/<class_name>/stream/<stream_name>')
def stream(class_name, stream_name):
    return render_template('admin/stream.html', class_name=class_name, stream_name=stream_name)

@bp.route('/assign-teacher-subject/<teacher_id>', methods=['GET', 'POST'])
def assign_teacher_subject(teacher_id):
    teacher = supabase.table('teachers').select('*').eq('id', teacher_id).single().execute()
    if not teacher.data:
        flash('Teacher not found', 'error')
        return redirect(url_for('admin.manage_teachers'))

    all_subjects = supabase.table('subjects').select('*').execute()

    if request.method == 'POST':
        subject_ids = request.form.getlist('subjects')

        supabase.table('teacher_assignments').delete().eq('teacher_id', teacher_id).execute()

        for subject_id in subject_ids:
            supabase.table('teacher_assignments').insert({
                'teacher_id': teacher_id,
                'subject_id': subject_id,
                'class_id': '00000000-0000-0000-0000-000000000000'
            }).execute()

        flash('Subjects assigned successfully', 'success')
        return redirect(url_for('admin.teacher_profile', teacher_id=teacher_id))

    return render_template('admin/assign_teacher_subject.html', teacher=teacher.data, subjects=all_subjects.data)

@bp.route('/assign-teacher-class/<teacher_id>', methods=['GET', 'POST'])
def assign_teacher_class(teacher_id):
    teacher = supabase.table('teachers').select('*').eq('id', teacher_id).single().execute()
    if not teacher.data:
        flash('Teacher not found', 'error')
        return redirect(url_for('admin.manage_teachers'))

    all_classes = supabase.table('classes').select('*').execute()

    if request.method == 'POST':
        class_ids = request.form.getlist('classes')

        for class_id in class_ids:
            supabase.table('teacher_assignments').update({
                'class_id': class_id
            }).eq('teacher_id', teacher_id).eq('class_id', '00000000-0000-0000-0000-000000000000').execute()

        flash('Classes assigned successfully', 'success')
        return redirect(url_for('admin.teacher_profile', teacher_id=teacher_id))

    return render_template('admin/assign_teacher_class.html', teacher=teacher.data, classes=all_classes.data)

@bp.route('/teachers')
def manage_teachers():
    teachers = supabase.table('teachers').select('*, teacher_assignments(subject_id, class_id, stream_id)').execute()
    subjects = supabase.table('subjects').select('id, name').execute()
    classes = supabase.table('classes').select('id, name').execute()
    streams = supabase.table('streams').select('id, name, class_id').execute()
    subject_dict = {s['id']: s['name'] for s in subjects.data}
    class_dict = {c['id']: c['name'] for c in classes.data}
    stream_dict = {s['id']: {'name': s['name'], 'class_id': s['class_id']} for s in streams.data}

    for teacher in teachers.data:
        teacher['subjects'] = list(set([subject_dict[a['subject_id']] for a in teacher['teacher_assignments'] if a['subject_id'] in subject_dict]))

        class_streams = {}
        for assignment in teacher['teacher_assignments']:
            if assignment['class_id'] in class_dict and assignment['stream_id'] in stream_dict:
                class_name = class_dict[assignment['class_id']]
                stream_name = stream_dict[assignment['stream_id']]['name']
                if class_name not in class_streams:
                    class_streams[class_name] = set()
                class_streams[class_name].add(stream_name)

        teacher['class_streams'] = [f"{class_name} ({', '.join(streams)})" for class_name, streams in class_streams.items()]
        teacher['classes'] = list(class_streams.keys())

    return render_template('admin/teachers.html', teachers=teachers.data, subjects=subjects.data, classes=classes.data)

@bp.route('/teacher/<teacher_id>', methods=['GET', 'POST'])
def teacher_profile(teacher_id):
    teacher_result = supabase.table('teachers').select('*').eq('id', teacher_id).single().execute()

    if teacher_result is None or not teacher_result.data:
        flash("Error fetching teacher data", "error")
        return redirect(url_for('admin.manage_teachers'))

    teacher = teacher_result.data

    assignments = supabase.table('teacher_assignments').select('subjects(name), classes(name)').eq('teacher_id', teacher_id).execute()

    teacher['subjects'] = list(set([a['subjects']['name'] for a in assignments.data if a['subjects']]))
    teacher['classes'] = list(set([a['classes']['name'] for a in assignments.data if a['classes']]))

    return render_template('admin/teacher_profile.html', teacher=teacher)

@bp.route('/add-teacher', methods=['POST'])
def add_teacher():
    try:
        name = request.form['teacher_name']
        email = request.form['teacher_email']
        phone = request.form['teacher_phone']
        subjects = request.form.getlist('teacher_subjects')
        class_id = request.form['teacher_classes']
        streams = request.form.getlist('teacher_streams')

        if not all([name, email, phone, subjects, class_id, streams]):
            flash("All fields are required", "error")
            return redirect(url_for('admin.manage_teachers'))

        existing_user = supabase.table('users').select('id').eq('email', email).execute()
        if existing_user.data:
            flash("A user with this email already exists", "error")
            return redirect(url_for('admin.manage_teachers'))

        default_password = "12345"
        hashed_password = generate_password_hash(default_password)

        new_user = supabase.table('users').insert({
            'email': email,
            'password': hashed_password,
            'role': 'teacher'
        }).execute()

        if not new_user.data:
            raise Exception("Failed to create user account for the teacher")

        new_user_id = new_user.data[0]['id']

        new_teacher = supabase.table('teachers').insert({
            'user_id': new_user_id,
            'name': name,
            'email': email,
            'phone': phone
        }).execute()

        if not new_teacher.data:
            supabase.table('users').delete().eq('id', new_user_id).execute()
            raise Exception("Failed to add new teacher")

        new_teacher_id = new_teacher.data[0]['id']

        for subject_id in subjects:
            for stream_id in streams:
                assignment = supabase.table('teacher_assignments').insert({
                    'teacher_id': new_teacher_id,
                    'subject_id': subject_id,
                    'class_id': class_id,
                    'stream_id': stream_id
                }).execute()

                if not assignment.data:
                    raise Exception("Failed to assign subject, class, and stream to teacher")

        flash("Teacher added successfully. A user account has been created with the default password '12345'.", "success")
        return redirect(url_for('admin.teacher_profile', teacher_id=new_teacher_id))

    except Exception as e:
        logging.error(f"Error adding teacher: {str(e)}")
        flash(f"An error occurred while adding the teacher: {str(e)}", "error")
        return redirect(url_for('admin.manage_teachers'))

@bp.route('/get-streams/<class_id>')
def get_streams(class_id):
    if 'user_id' not in session:
        return jsonify([])

    streams = supabase.table('streams').select('id, name').eq('class_id', class_id).execute()
    return jsonify(streams.data)

@bp.route('/delete-teacher/<teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    supabase.table('teachers').delete().eq('id', teacher_id).execute()
    return redirect(url_for('admin.manage_teachers'))

@bp.route('/students')
def manage_students():
    students = supabase.table('students').select('*').execute()
    classes = supabase.table('classes').select('name').order('name').execute()
    return render_template('admin/students.html', students=students.data, classes=[c['name'] for c in classes.data])

@bp.route('/add-student', methods=['POST'])
def add_student():
    name = request.form['student_name']
    class_name = request.form['student_class']
    gender = request.form['student_gender']
    parent_phone = request.form['parent_phone']

    class_id = supabase.table('classes').select('id').eq('name', class_name).execute().data[0]['id']

    supabase.table('students').insert({
        'name': name,
        'class_id': class_id,
        'gender': gender,
        'parent_phone': parent_phone
    }).execute()

    return redirect(url_for('admin.manage_students'))

@bp.route('/delete-student/<student_id>', methods=['POST'])
def delete_student(student_id):
    supabase.table('students').delete().eq('id', student_id).execute()
    return redirect(url_for('admin.manage_students'))

@bp.route('/view-student/<student_id>')
def view_student(student_id):
    student = supabase.table('students').select('*').eq('name', student_id).execute().data[0]
    class_name = supabase.table('classes').select('name').eq('id', student['class_id']).execute().data[0]['name']
    student['class'] = class_name
    return render_template('admin/student_detail.html', student=student)

@bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
