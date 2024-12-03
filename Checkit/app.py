from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Database URI
db = SQLAlchemy(app)  # Initialize SQLAlchemy with the Flask app

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(150), unique=True, nullable=False)  # Username field
    password = db.Column(db.String(150), nullable=False)  # Password field

# Define the List model
class List(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(150), nullable=False)  # List name field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    tasks = db.relationship('Task', backref='list', lazy=True, cascade="all, delete-orphan")  # Relationship to Task with cascade delete

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(150), nullable=False)  # Task name field
    description = db.Column(db.String(300), nullable=True)  # Task description field
    completed = db.Column(db.Boolean, default=False)  # Task completion status
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)  # Foreign key to List

# Define the LastList model to keep track of the last accessed list
class LastList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'), nullable=False)

@app.route('/')
def startpage():
    # Render the start page
    return render_template('startpage.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    # Handle user sign-in
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            last_list = LastList.query.filter_by(user_id=user.id).first()
            if last_list:
                return redirect(url_for('view_list', list_id=last_list.list_id))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and/or password', 'danger')
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Handle user sign-up
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Account already exists', 'danger')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('signin'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    # Render the dashboard page
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('signin'))
    user_id = session.get('user_id')
    lists = List.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', username=session.get('username'), lists=lists)

@app.route('/list/<int:list_id>')
def view_list(list_id):
    # Render the list page for a specific list
    if 'user_id' not in session:
        flash('Please log in to access the list.', 'danger')
        return redirect(url_for('signin'))
    user_id = session['user_id']
    last_list = LastList.query.filter_by(user_id=user_id).first()
    if last_list:
        last_list.list_id = list_id
    else:
        new_last_list = LastList(user_id=user_id, list_id=list_id)
        db.session.add(new_last_list)
    db.session.commit()
    list_ = List.query.get_or_404(list_id)
    lists = List.query.filter_by(user_id=user_id).all()
    return render_template('list.html', list=list_, lists=lists, username=session.get('username'))

@app.route('/add_list', methods=['POST'])
def add_list():
    # Handle adding a new list
    if 'user_id' not in session:
        flash('Please log in to add a list.', 'danger')
        return redirect(url_for('signin'))
    list_name = request.form.get('list_name')
    new_list = List(name=list_name, user_id=session['user_id'])
    db.session.add(new_list)
    db.session.commit()
    user_id = session['user_id']
    last_list = LastList.query.filter_by(user_id=user_id).first()
    if last_list:
        last_list.list_id = new_list.id
    else:
        new_last_list = LastList(user_id=user_id, list_id=new_list.id)
        db.session.add(new_last_list)
    db.session.commit()
    flash('List added successfully!', 'success')
    return redirect(url_for('view_list', list_id=new_list.id))

@app.route('/add_task/<int:list_id>', methods=['POST'])
def add_task(list_id):
    # Handle adding a new task to a specific list
    if 'user_id' not in session:
        flash('Please log in to add a task.', 'danger')
        return redirect(url_for('signin'))
    task_name = request.form.get('task_name')
    task_description = request.form.get('task_description')
    new_task = Task(name=task_name, description=task_description, list_id=list_id)
    db.session.add(new_task)
    db.session.commit()
    flash('Task added successfully!', 'success')
    return redirect(url_for('view_list', list_id=list_id))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    # Handle deleting a task
    if 'user_id' not in session:
        flash('Please log in to delete a task.', 'danger')
        return redirect(url_for('signin'))
    task = Task.query.get(task_id)
    list_id = task.list_id
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('view_list', list_id=list_id))

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    # Handle toggling the completion status of a task
    if 'user_id' not in session:
        flash('Please log in to update a task.', 'danger')
        return redirect(url_for('signin'))
    task = Task.query.get(task_id)
    task.completed = not task.completed
    db.session.commit()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('view_list', list_id=task.list_id))

@app.route('/delete_list/<int:list_id>', methods=['POST'])
def delete_list(list_id):
    # Handle deleting a list
    if 'user_id' not in session:
        flash('Please log in to delete a list.', 'danger')
        return redirect(url_for('signin'))
    list_ = List.query.get(list_id)
    db.session.delete(list_)
    db.session.commit()
    flash('List deleted successfully!', 'success')
    
    # Check if there are any remaining lists
    user_id = session['user_id']
    remaining_lists = List.query.filter_by(user_id=user_id).all()
    if remaining_lists:
        # Redirect to the second remaining list if the first list is deleted
        if remaining_lists[0].id == list_id and len(remaining_lists) > 1:
            return redirect(url_for('view_list', list_id=remaining_lists[1].id))
        else:
            return redirect(url_for('view_list', list_id=remaining_lists[0].id))
    else:
        # Redirect to the dashboard if no lists remain
        return redirect(url_for('dashboard'))

@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    # Handle editing a task
    if 'user_id' not in session:
        flash('Please log in to edit a task.', 'danger')
        return redirect(url_for('signin'))
    task = Task.query.get(task_id)
    task.name = request.form.get('task_name')
    task.description = request.form.get('task_description')
    db.session.commit()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('view_list', list_id=task.list_id))

@app.route('/logout')
def logout():
    # Handle user logout
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('startpage'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
        print("Database tables created")
    app.run(debug=True)  # Run the Flask application in debug mode