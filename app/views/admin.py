from flask import Blueprint, jsonify, request, render_template, url_for, redirect

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Sample Data
class_data = {
    'Form One': [],
    'Form Two': [],
    'Form Three': [],
    'Form Four': []
}

subjects = [
    {'name': 'Mathematics', 'code': 'MATH101', 'class': 'Form One'},
    {'name': 'English', 'code': 'ENG101', 'class': 'Form Two'},
    {'name': 'Biology', 'code': 'BIO101', 'class': 'Form Three'}
]

teachers = [
    {'id': 1, 'name': 'John Doe', 'email': 'john.doe@example.com', 'phone': '555-1234', 'subjects': ['Math'], 'classes': ['Form One']},
    {'id': 2, 'name': 'Jane Smith', 'email': 'jane.smith@example.com', 'phone': '555-5678', 'subjects': ['English'], 'classes': ['Form Two']},
    {'id': 3, 'name': 'Emily Johnson', 'email': 'emily.johnson@example.com', 'phone': '555-8765', 'subjects': ['Civics'], 'classes': ['Form Three']}
]

# Route Definitions
@bp.route('/')
def dashboard():
    return render_template('admin/dashboard.html')

@bp.route('/subjects')
def manage_subjects():
    return render_template('admin/subjects.html', subjects=subjects, class_data=class_data)

@bp.route('/add-subject', methods=['POST'])
def add_subject():
    subject_name = request.form['subject_name']
    subject_code = request.form['subject_code']
    subject_class = request.form['subject_class']
    subjects.append({'name': subject_name, 'code': subject_code, 'class': subject_class})
    return redirect(url_for('admin.manage_subjects'))

@bp.route('/classes')
def classes():
    return render_template('admin/classes.html', class_data=class_data)

@bp.route('/add-stream', methods=['POST'])
def add_stream():
    class_name = request.form['class_name']
    stream_name = request.form['stream_name']
    if class_name in class_data:
        class_data[class_name].append(stream_name)
    return redirect(url_for('admin.classes'))

@bp.route('/class/<class_name>/stream/<stream_name>')
def stream(class_name, stream_name):
    return render_template('admin/stream.html', class_name=class_name, stream_name=stream_name)

@bp.route('/teachers')
def manage_teachers():
    return render_template('admin/teachers.html', teachers=teachers,subjects=['Math', 'English', 'Civics'], classes=list(class_data.keys()))

@bp.route('/teacher/<int:teacher_id>', methods=['GET', 'POST'], endpoint='teacher_dashboard')
def teacher_profile(teacher_id):
    teacher = next((t for t in teachers if t['id'] == teacher_id), None)
    if not teacher:
        return "Teacher not found", 404
    
    if request.method == 'POST':
        # Handle form submission for assigning subjects and classes
        subjects = request.form.getlist('subjects')
        classes = request.form.getlist('classes')
        # Update teacher's subjects and classes
        teacher['subjects'] = subjects
        teacher['classes'] = classes
        return redirect(url_for('admin.teacher_profile', teacher_id=teacher_id))

    # For GET request, render the teacher profile page
    return render_template('admin/teacher_profile.html', teacher=teacher, all_subjects=['Math', 'English', 'Civics'], all_classes=list(class_data.keys()))

@bp.route('/assign-teacher-subject/<int:teacher_id>', methods=['GET', 'POST'])
def assign_teacher_subject(teacher_id):
    teacher = next((t for t in teachers if t['id'] == teacher_id), None)
    if not teacher:
        return redirect(url_for('admin.manage_teachers'))
    if request.method == 'POST':
        teacher['subjects'] = request.form.getlist('subjects')
        return redirect(url_for('admin.teacher_dashboard', teacher_id=teacher_id))
    return render_template('admin/assign_teacher_subject.html', teacher=teacher, subjects=['Math', 'English', 'Civics'])

@bp.route('/assign-teacher-class/<int:teacher_id>', methods=['GET', 'POST'])
def assign_teacher_class(teacher_id):
    teacher = next((t for t in teachers if t['id'] == teacher_id), None)
    if not teacher:
        return redirect(url_for('admin.manage_teachers'))
    if request.method == 'POST':
        teacher['classes'] = request.form.getlist('classes')
        return redirect(url_for('admin.teacher_dashboard', teacher_id=teacher_id))
    return render_template('admin/assign_teacher_class.html', teacher=teacher, classes=list(class_data.keys()))

@bp.route('/add-teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['teacher_name']
        email = request.form['teacher_email']
        phone = request.form['teacher_phone']
        subjects = request.form.getlist('teacher_subjects')
        classes = request.form.getlist('teacher_classes')
        
        # Generate a new ID for the teacher
        new_id = max(teacher['id'] for teacher in teachers) + 1 if teachers else 1
        
        # Add new teacher
        teachers.append({
            'id': new_id,
            'name': name,
            'email': email,
            'phone': phone,
            'subjects': subjects,
            'classes': classes
        })
        
        return redirect(url_for('admin.manage_teachers'))
        subje = ['Math', 'English', 'Civics']
    # For GET request, render the add teacher form
    return render_template('admin/add_teacher.html', classes=list(class_data.keys()), subjects=['Math', 'English', 'Civics'])

@bp.route('/delete-teacher/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    global teachers
    teachers = [t for t in teachers if t['id'] != teacher_id]
    return redirect(url_for('admin.manage_teachers'))

@bp.route('/students')
def students():
    return render_template('admin/students.html')
