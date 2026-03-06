from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///sms.db"
db = SQLAlchemy(app)
app.secret_key="Abdullahkikey"

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable = False)
    reg = db.Column(db.Integer, nullable = False, unique=True)
    phone = db.Column(db.String(12), unique=True)
    email = db.Column(db.String(30), nullable = False , unique=True)
    degree = db.Column(db.String(20), nullable = False)
    cnic = db.Column(db.String(20), nullable = False, unique=True)
    photo = db.Column(db.String(20), nullable=False)

# with app.app_context():
#     db.create_all()


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":
        name = request.form["username"]
        password = request.form["password"]
        if name == "admin123" and password == "1234":
            session["user_name"] = name
            return redirect("/dashboard")
        else:
            flash("Invalid Username or Password", "error")
            
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_name" not in session:
        return redirect("login")
    return render_template("dashboard.html")

@app.route("/add", methods=["GET", "POST"])
def add():

    if "user_name" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"]
        cnic = request.form["cnic"]
        phone = request.form["phone"]
        email = request.form["email"]
        degree = request.form["degree"]
        reg = request.form["reg"]

        photo = request.files.get("photo")
        filename = ""

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save("static/uploads/" + filename)

        data = Students(
            name=name,
            cnic=cnic,
            phone=phone,
            email=email,
            degree=degree,
            reg=reg,
            photo=filename
        )

        db.session.add(data)
        db.session.commit()

        flash("Student added successfully", "success")
        return redirect(url_for("records"))

    return render_template("add.html")

@app.route("/records", methods= ["GET","POST"])
def records():
    if "user_name" not in session:
        return redirect("login")
    records = Students.query.all()
    if request.method=="POST":
        if "delete" in request.form:
            id = request.form["delete"]
            found = Students.query.filter_by(id=id).first()
            db.session.delete(found)
            db.session.commit()
            return redirect("/records")
        if "name" in request.form:
            name = request.form["name"]
            search_pattern = f"%{name}%"
            records=Students.query.filter(Students.name.like(search_pattern)).all()
            if not records:
                error="No user found"
    return render_template("records.html", records=records)

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):

    if "user_name" not in session:
        return redirect(url_for("login"))

    student = Students.query.get_or_404(id)

    if request.method == "POST":

        student.name = request.form["name"]
        student.cnic = request.form["cnic"]
        student.phone = request.form["phone"]
        student.email = request.form["email"]
        student.degree = request.form["degree"]
        student.reg = request.form["reg"]

        photo = request.files.get("photo")

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save("static/uploads/" + filename)
            student.photo = filename

        db.session.commit()

        flash("Student updated successfully", "success")
        return redirect(url_for("records"))

    return render_template("update.html", student=student)


@app.route("/students", methods=["GET","POST"])
def show():
    show = Students.query.order_by(Students.reg.asc()).all()
    if request.method=="POST":
        show = []
        name = request.form["name"]
        search_pattern = f"%{name}%"
        show=Students.query.filter(Students.name.like(search_pattern)).all()
        if not show:
            error="No user found"
    return render_template("show.html",show=show)

@app.route("/stats")
def stats():

    if "user_name" not in session:
        return redirect(url_for("login"))

    total_students = Students.query.count()

    degree_stats = db.session.query(
        Students.degree,
        func.count(Students.id)
    ).group_by(Students.degree).all()

    latest_students = Students.query.order_by(Students.id.desc()).limit(5).all()

    return render_template(
        "stats.html",
        total_students=total_students,
        degree_stats=degree_stats,
        latest_students=latest_students
    )

@app.route("/logout")
def logout():
    session.pop("user_name", None)
    flash("Logged out successfully", "success")
    redirect(url_for("login"))

if (__name__) == "__main__":
    app.run(debug=True)