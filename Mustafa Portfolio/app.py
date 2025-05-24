from flask import Flask, session, request, render_template, flash, redirect, url_for
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from models import db, Project
# route for the add project
import os
from werkzeug.utils import secure_filename



# Create the app for the flask to run
app = Flask(__name__)

# secrit key for the flash message
app.secret_key = "jabsaomer123"

# Data base related codes

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# initialize the database creation
db.init_app(app)


'''Route for the home page rendering'''

@app.route("/")
def home():
    projects = Project.query.all()
    return render_template("index.html", projects = projects)



'''route for the contact form submission action'''

@app.route("/submit", methods = ["POST"])
def submit():
    # Collect the data from the form
    name = request.form.get("name")
    email = request.form.get("email")    
    message = request.form.get("message")

    # Create the subject and the body

    subject = "New email submission => Mustafa-Portfolio"
    body = f"Name: {name}\nEmail: {email}:\nMessage: {message}"

    # Now we have to specify the smtp details

    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "jabsa2020@gmail.com"
    smtp_password = "aqlq bove thbd gjjl"
    sender_email = smtp_username
    receiver_email = "jabsa2020@gmail.com"
    # Now we have to create the message

    msg = MIMEMultipart()
    msg["From"] =  sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Now as we have all the details, we will try to send the email

    try:
        # we will access the server first

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        flash(f"Thanks Mr.{name}, Your message was sent successfully, we will get back to you")
        return redirect(url_for("home")+ "#contact")
    except Exception as e:
        print(f"Error occured: {e}")
        flash("Sorry, there was something wrong occured, try again later!!")
        return redirect(url_for("home")+ "#contact")



# Admin login code

# simple credencials initially

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# route for the login page

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            flash("login sucessful!")
            return redirect(url_for("admin"))
        else:
            flash("Invalid user name or password")
            return redirect(url_for("login"))

    return render_template("login.html")

# Route for the admin page

@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        flash("Please log in to access this page.")
        return redirect(url_for("login"))
    projects = Project.query.all()
    return render_template("admin.html", projects=projects)



# Folder where uploaded images will be stored
UPLOADED_FOLDER = 'static/uploads'
os.makedirs(UPLOADED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOADED_FOLDER

# route for project creation and update on the website
@app.route('/add_project', methods=["POST"])
def add_project():
    if not session.get("admin_logged_in"):
        flash("Unauthorized, Please log in.")
        return redirect(url_for("login"))
    
    # get form data
    title = request.form.get("title")
    description = request.form.get("description")
    technologies = request.form.get("technologies")
    project_link = request.form.get("project_link")

    # Handle the image upload
    image = request.files.get("image")
    if not image:
        flash("image upload failed")
        return redirect(url_for("admin"))
    
    # Secure the filename
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    # Create a new project object
    new_project = Project(
        title=title,
        description=description,
        technologies=technologies,
        image_filename=filename,
        project_link=project_link
    )

    # Save to the data base

    db.session.add(new_project)
    db.session.commit()

    flash("project added successfully!")
    return redirect(url_for("admin"))
# Delete project rout
@app.route("/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    if not session.get("admin_logged_in"):
        flash("Please log in to perform this action.")
        return redirect(url_for("login"))

    project = Project.query.get_or_404(project_id)

    # Delete image file if exists
    if project.image_filename:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], project.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(project)
    db.session.commit()
    flash("Project deleted successfully.")
    return redirect(url_for("admin"))

# edit project route

@app.route("/edit/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    if not session.get("admin_logged_in"):
        flash("Please log in to perform this action.")
        return redirect(url_for("login"))

    project = Project.query.get_or_404(project_id)

    if request.method == "POST":
        # Get updated data from the form
        project.title = request.form.get("title")
        project.description = request.form.get("description")
        project.technologies = request.form.get("technologies")
        project.project_link = request.form.get("project_link")

        # Check if a new image is uploaded
        image = request.files.get("image")
        if image and image.filename:
            # Delete the old image if exists
            if project.image_filename:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], project.image_filename)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Save new image
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            # Update image filename in the database
            project.image_filename = filename

        db.session.commit()
        flash("Project updated successfully!")
        return redirect(url_for("admin"))

    return render_template("edit.html", project=project)


# language shifting route
@app.route("/ar")
def arabic_home():
    projects = Project.query.all()
    return render_template("arabic-index.html", projects=projects)



# START RUNNING THE APP

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database created successfully!")
    app.run(debug=True)