# UniVoice

Student Complaints & Suggestions Management System for the Faculty of Computers and Information.

## Technology
- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite
- HTML, CSS and JavaScript (frontend foundation)

## Run on Windows

1. Install Python 3.11 or newer.
2. Extract this folder.
3. Open Command Prompt or PowerShell inside the `UniVoice` folder.
4. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt:

   ```cmd
   .venv\Scripts\activate.bat
   ```

5. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   py run.py
   ```

7. Open `http://127.0.0.1:5000`.

## Current starter functionality
- Student registration and login
- Password hashing
- Student complaint/suggestion submission
- Image/PDF attachment extension and size checks
- Student request list and detail page
- Admin request review, assignment and status update
- Admin creation of staff accounts
- Staff assigned-request view, replies and status updates
- Status history and student feedback data models

## First-run admin account

For safety, public registration only creates student accounts. Create the first admin account from the Flask shell after installing dependencies:

```powershell
py -c "from app import create_app; from app.extensions import db; from app.models import User; app=create_app(); ctx=app.app_context(); ctx.push(); u=User(full_name='System Admin', email='admin@univoice.local', role='admin'); u.set_password('ChangeMe123!'); db.session.add(u); db.session.commit(); print('Admin created')"
```

Then sign in with:
- Email: `admin@univoice.local`
- Password: `ChangeMe123!`

Change this password after the first login. This is a local development account only.

## Important development notes
- This is the initial runnable foundation, not a production deployment.
- Configure a private `SECRET_KEY` before deployment.
- Add CSRF protection, email verification, rate limiting, secure attachment serving, audit logging and automated tests before real university use.
- SQLite is suitable for the coursework prototype. A production deployment should use a managed database.
- Uploaded files are stored under `app/static/uploads` in this starter. Before deployment, move them to private storage and serve them only after permission checks.
