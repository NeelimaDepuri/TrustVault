from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from datetime import datetime
from flask import Flask, render_template, request, redirect
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)
from models import db, User, Document, Permission, AuditLog
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'trustvault123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trustvault.db'

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return "TrustVault Running"

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        existing_user = User.query.filter_by(
            email=request.form["email"]
        ).first()

        if existing_user:
            return "Email already exists"

        user = User(
        username=request.form["username"],
        email=request.form["email"],
        password=generate_password_hash(
        request.form["password"]
    ),
    role=request.form["role"]
)

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/dashboard")

        return "Invalid Login"

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        user=current_user
    )

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    if request.method == "POST":

        file = request.files["file"]

        if file:

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            doc = Document(
                filename=file.filename,
                filepath=filepath,
                owner_id=current_user.id
            )

            db.session.add(doc)
            db.session.commit()

            log = AuditLog(
                action="UPLOAD",
                user_email=current_user.email,
                created_at=str(datetime.now())
            )

            db.session.add(log)
            db.session.commit()

            return "File Uploaded Successfully"

    return render_template("upload.html")

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/login")
@app.route("/documents")
@login_required
def documents():

    docs = Document.query.filter_by(
        owner_id=current_user.id
    ).all()

    return render_template(
        "documents.html",
        docs=docs
    )
@app.route("/delete/<int:id>")
@login_required
def delete_document(id):

    doc = Document.query.get_or_404(id)

    if doc.owner_id != current_user.id:
        return "Access Denied"

    db.session.delete(doc)
    db.session.commit()

    return redirect("/documents")

@app.route("/permission/<int:id>", methods=["GET", "POST"])
@login_required
def permission(id):

    doc = Document.query.get_or_404(id)

    if doc.owner_id != current_user.id:
        return "Access Denied"

    if request.method == "POST":

        p = Permission(
            document_id=id,
            user_email=request.form["email"],
            access_type=request.form["access"]
        )

        db.session.add(p)
        db.session.commit()

        return "Permission Granted"

    return render_template("permissions.html")

@app.route("/logs")
@login_required
def logs():

    all_logs = AuditLog.query.all()

    return render_template(
        "logs.html",
        logs=all_logs
    )
@app.route("/admin")
@login_required
def admin():

    users = User.query.count()
    docs = Document.query.count()
    logs = AuditLog.query.count()

    return render_template(
        "admin.html",
        users=users,
        docs=docs,
        logs=logs
    )

@app.route("/revoke/<int:id>")
@login_required
def revoke(id):

    permission = Permission.query.get_or_404(id)

    db.session.delete(permission)
    db.session.commit()

    log = AuditLog(
        action="PERMISSION_REVOKED",
        user_email=current_user.email,
        created_at=str(datetime.now())
    )

    db.session.add(log)
    db.session.commit()

    return redirect("/permissions")

@app.route("/permissions")
@login_required
def permissions():

    perms = Permission.query.all()

    return render_template(
        "all_permissions.html",
        perms=perms
    )




if __name__ == "__main__":
    app.run(debug=True)