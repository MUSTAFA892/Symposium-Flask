import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

app = Flask(__name__, static_url_path='/static')

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://psql_ocv0_user:QvLMVrkaickfcjwBh6NimHrQGKo5uijB@dpg-crmopktumphs739idk60-a.oregon-postgres.render.com/psql_ocv0"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "secretkey123"

db = SQLAlchemy(app)

ENTRY_FEE = 250

# Define the model
class Datas(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    mobilenumber = db.Column(db.String(15), unique=True, nullable=False)
    dept = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    team_size = db.Column(db.Integer, nullable=False)
    teamname = db.Column(db.String(100), nullable=True)
    team_members = db.Column(db.JSON, nullable=True)
    expected_amount = db.Column(db.Integer, nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    screenshot = db.Column(db.LargeBinary, nullable=False)

    def __repr__(self):
        return f'<data {self.name}>'

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/registering', methods=['POST'])
def pass_data():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        mobilenumber = request.form['mobilenumber']
        dept = request.form['dept']
        college = request.form['college']
        email = request.form['email']
        teamname = request.form.get('teamname', '')
        team_size = int(request.form['team-size'])
        expected_amount = team_size * ENTRY_FEE
        
        # Check for existing mobile number and email
        existing_user = Datas.query.filter(
            (Datas.mobilenumber == mobilenumber) |
            (Datas.email == email)
        ).first()

        if existing_user:
            error_message = 'A user with this mobile number or email already exists.'
            return render_template('fail_redirect.html', error_message=error_message)

        # Prepare team members list as a list of dictionaries
        team_members = []
        for i in range(2, team_size + 1):
            teammate_name = request.form.get(f'teammate{i-1}-name')
            teammate_email = request.form.get(f'teammate{i-1}-email')
            teammate_phone = request.form.get(f'teammate{i-1}-phone')
            if teammate_name and teammate_email and teammate_phone:
                team_members.append({
                    teammate_name: [teammate_email, teammate_phone]
                })

        # Store registration data in the session
        registration_data = {
            'name': name,
            'mobilenumber': mobilenumber,
            'dept': dept,
            'college': college,
            'email': email,
            'teamname': teamname,
            'team_size': team_size,
            'expected_amount': expected_amount,
            'team_members': team_members
        }
        session['registration'] = registration_data

        return render_template("payment.html", expected_amount=expected_amount)

@app.route('/paying', methods=['POST'])
def store_data():
    transaction_id = request.form['transaction-id']
    screenshot = request.files['screenshot']

    screenshot_binary = None
    if screenshot:
        screenshot_binary = screenshot.read()

    registration_data = session.get('registration')
    if registration_data:
        data = Datas(
            name=registration_data['name'],
            mobilenumber=registration_data['mobilenumber'],
            dept=registration_data['dept'],
            college=registration_data['college'],
            email=registration_data['email'],
            team_size=registration_data['team_size'],
            teamname=registration_data.get('teamname'),
            expected_amount=registration_data['expected_amount'],
            transaction_id=transaction_id,
            screenshot=screenshot_binary,
            team_members=registration_data['team_members']
        )

        # Start a new transaction
        try:
            db.session.add(data)
            db.session.commit()
            session.pop('registration', None)  # Clear session data after successful registration
            return render_template('success_redirect.html')
        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            error_message = "Registration failed due to an error."
            return render_template('pay_redirect.html', error_message=error_message)

@app.route('/datas')
def datas():
    all_datas = Datas.query.all()
    return render_template('datas.html', datas=all_datas)

@app.route('/image/<int:data_id>')
def get_image(data_id):
    data = Datas.query.get(data_id)
    if data and data.screenshot:
        return app.response_class(
            response=data.screenshot,
            mimetype='image/jpeg',
            headers={"Content-Disposition": "inline; filename=image.jpg"}
        )
    return "Image not found", 404

@app.route('/technical')
def technical():
    return render_template("technical.html")

@app.route('/non-technical')
def non_technical():
    return render_template("non-technical.html")

# @app.route('/register')
# def register():
#     return render_template("register.html")

@app.route('/payment')
def payment():
    return render_template("payment.html")

@app.route('/fun')
def fun():
    return render_template("fun.html")

@app.route('/members')
def members():
    return render_template("members.html")

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
