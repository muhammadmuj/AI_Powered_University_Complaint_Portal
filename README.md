# University Complaint Portal

A web application for university students to submit and track complaints, and for university staff to manage and respond to these complaints.

## Features

- User authentication (login, register, logout)
- Dashboard with complaint statistics
- Submit new complaints
- View and filter complaints
- Respond to complaints
- Update complaint status (staff only)
- Admin panel for managing complaints and categories

## User Roles

- **Regular Users (Students)**: Can submit complaints, view their own complaints, and respond to staff responses.
- **Staff/Admin**: Can view all complaints, respond to complaints, update complaint status, and manage complaint categories.

## Technologies Used

- Django 5.1
- Bootstrap 4.6
- SQLite (development)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd university_complaint_portal
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

5. Create initial complaint categories:
   ```
   python manage.py create_initial_data
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Usage

1. Register a new account or login with an existing account
2. Submit a new complaint from the dashboard
3. View and filter your complaints
4. Respond to staff responses on your complaints
5. Staff can update complaint status and respond to complaints

## Admin Access

Access the admin panel at http://127.0.0.1:8000/admin/ with your superuser credentials to:
- Manage users
- Manage complaint categories
- Manage complaints and responses 