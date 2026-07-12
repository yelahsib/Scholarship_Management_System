from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/scholarship_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELS (As per Assignment Schema) ---

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    # Relationship
    applications = db.relationship('ScholarshipApplication', backref='student', lazy=True, cascade="all, delete-orphan")

class Scholarship(db.Model):
    __tablename__ = 'scholarships'
    scholarship_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scholarship_name = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    # Relationship
    applications = db.relationship('ScholarshipApplication', backref='scholarship', lazy=True, cascade="all, delete-orphan")

class ScholarshipApplication(db.Model):
    __tablename__ = 'scholarship_applications'
    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarships.scholarship_id'), nullable=False)

# Auto-create tables
with app.app_context():
    db.create_all()

# --- ROUTES ---

# Dashboard (Home) - Displays everything
@app.route('/')
def index():
    students = Student.query.all()
    scholarships = Scholarship.query.all()
    applications = ScholarshipApplication.query.all()
    return render_template('index.html', students=students, scholarships=scholarships, applications=applications)

# 1. ADD STUDENT
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        gender = request.form.get('gender')
        address = request.form.get('address')
        birthday_str = request.form.get('birthday')

        if not name or not email or not mobile or not birthday_str:
            flash("All student fields are required!", "danger")
            return redirect(url_for('add_student'))
        try:
            birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
            new_student = Student(name=name, email=email, mobile=mobile, gender=gender, address=address, birthday=birthday)
            db.session.add(new_student)
            db.session.commit()
            flash("Student added successfully!", "success")
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
    return render_template('add_student.html')

# 2. EDIT STUDENT
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.email = request.form.get('email')
        student.mobile = request.form.get('mobile')
        student.gender = request.form.get('gender')
        student.address = request.form.get('address')
        if request.form.get('birthday'):
            student.birthday = datetime.strptime(request.form.get('birthday'), '%Y-%m-%d').date()
        db.session.commit()
        flash("Student updated!", "success")
        return redirect(url_for('index'))
    return render_template('edit_student.html', student=student)

# 3. DELETE STUDENT
@app.route('/delete_student/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student record deleted!", "success")
    return redirect(url_for('index'))

# 4. ADD SCHOLARSHIP
@app.route('/add_scholarship', methods=['GET', 'POST'])
def add_scholarship():
    if request.method == 'POST':
        s_name = request.form.get('scholarship_name')
        amount = request.form.get('amount')
        if s_name and amount:
            new_s = Scholarship(scholarship_name=s_name, amount=float(amount))
            db.session.add(new_s)
            db.session.commit()
            flash("Scholarship created!", "success")
            return redirect(url_for('index'))
    return render_template('add_scholarship.html')

# 5. APPLY FOR SCHOLARSHIP (Links Student & Scholarship)
@app.route('/apply', methods=['GET', 'POST'])
def apply_scholarship():
    if request.method == 'POST':
        s_id = request.form.get('student_id')
        sch_id = request.form.get('scholarship_id')
        if s_id and sch_id:
            new_app = ScholarshipApplication(student_id=int(s_id), scholarship_id=int(sch_id))
            db.session.add(new_app)
            db.session.commit()
            flash("Scholarship Application Submitted!", "success")
            return redirect(url_for('index'))
            
    students = Student.query.all()
    scholarships = Scholarship.query.all()
    return render_template('apply.html', students=students, scholarships=scholarships)

# 6. DELETE APPLICATION
@app.route('/delete_app/<int:id>')
def delete_app(id):
    app_record = ScholarshipApplication.query.get_or_404(id)
    db.session.delete(app_record)
    db.session.commit()
    flash("Application deleted!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)