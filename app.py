import os
from flask import Flask
from flask import render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

app = Flask(__name__, static_url_path='/static')

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://psql_wvkz_user:pQcWVFKFGaJwcXzXcjJGs9XAQNnslM4G@dpg-cri1nad6l47c73dsdt0g-a.oregon-postgres.render.com/psql_wvkz"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "secretkey123"

db = SQLAlchemy(app)

ENTRY_FEE=250

# Define the model
class Datas(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    mobilenumber = db.Column(db.String(15), unique=True, nullable=False)
    dept = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    events = db.Column(db.String, nullable=False)
    team_size = db.Column((db.Integer), nullable=False)
    teamname = db.Column(db.String(100), nullable=True)
    team_members = db.Column(db.String, nullable=True)
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
        events_str = ','.join(request.form.getlist('events'))
        teamname = request.form.get('teamname', '')
        team_size = int(request.form['team-size'])
        expected_amount = team_size * ENTRY_FEE
        
        # Check for existing mobile number and email
        existing_user = Datas.query.filter(
            (Datas.mobilenumber == mobilenumber) |
            (Datas.email == email)
        ).first()

        if existing_user:
            # Handle the case where mobile number or email already exists
            error_message = 'A user with this mobile number or email already exists.'
            return render_template('fail_redirect.html', error_message=error_message)
        
        # Prepare team members list
        team_members = []
        for i in range(2, team_size + 1):
            teammate_name = request.form.get(f'teammate{i-1}')
            if teammate_name:
                team_members.append(teammate_name)
        
        # Store registration data in the session
        registration_data = {
            'name': name,
            'mobilenumber': mobilenumber,
            'dept': dept,
            'college': college,
            'email': email,
            'events_str': events_str,
            'teamname': teamname,
            'team_size': team_size,
            'expected_amount': expected_amount,
            'team_members': ','.join(team_members)  # Store as comma-separated string
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
            events=registration_data['events_str'],
            team_size=registration_data['team_size'],
            teamname=registration_data.get('teamname'),
            expected_amount=registration_data['expected_amount'],
            transaction_id=transaction_id,
            screenshot=screenshot_binary,
            team_members=registration_data['team_members']
        )
        db.session.add(data)
        db.session.commit()
        return render_template('success_redirect.html')

    
    

@app.route('/datas')
def datas():
    all_datas = Datas.query.all()
    for record in all_datas:
        record.events = record.events.split(',') 
    return render_template('datas.html', datas=all_datas)

@app.route('/image/<int:data_id>')
def get_image(data_id):
    data = Datas.query.get(data_id)
    if data and data.screenshot:
        return app.response_class(
            response=data.screenshot,
            mimetype='image/jpeg',  # Adjust based on your image format (e.g., 'image/png')
            headers={"Content-Disposition": "inline; filename=image.jpg"}
        )
    return "Image not found", 404



@app.route('/technical')
def technical():
    return render_template("technical.html")

@app.route('/non-technical')
def non_technical():
    return render_template("non-technical.html")

@app.route('/register')
def register():
    return render_template("register.html")

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
