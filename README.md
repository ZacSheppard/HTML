# Checkit

This is a simple task management application built with Flask and SQLAlchemy. The application allows users to create lists, add tasks to lists, and manage tasks with options to edit, delete, and mark tasks as completed.

## Features

- User authentication (sign up, sign in, and logout)
- Create and manage task lists
- Add, edit, and delete tasks
- Mark tasks as completed
- Toggle task details
- Change application theme

## Installation

1. **Follow these steps:**
   ```sh
   # Clone the repository
   git clone https://github.com/your-username/task-management-app.git
   cd task-management-app

   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   # Install the dependencies
   pip install -r requirements.txt

   # Set up the database
   python -c "from app import db; db.create_all()"

   # run the application
   flask run
## Usage

1. **Sign Up:**
   - Navigate to the sign-up page and create a new account.

2. **Sign In:**
   - Sign in with your credentials.

3. **Create a List:**
   - Click on the "Add List" button to create a new task list.

4. **Add Tasks:**
   - Within a list, use the form to add new tasks with a name, description, and details.

5. **Manage Tasks:**
   - Use the edit button to modify task details.
   - Use the delete button to remove tasks.
   - Use the checkbox to mark tasks as completed.

6. **Change Theme:**
   - Use the settings modal to change the application theme.
  
## Credits
- Zac Sheppard
- chatGPT
