from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, URLField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Alternatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location_url = URLField('Cafe Location on Google Maps (URL)', validators=[URL(), DataRequired()])
    image = URLField('Cafe Image (URL)', validators=[URL(), DataRequired()])
    location = StringField('Location:: ', validators=[DataRequired()])
    wifi = SelectField('Wifi Availability',
                       choices=[("0", "✘"), ("1", "💪️")])
    power = SelectField('Power Socket Availability: ',
                        choices=[("0", "✘"), ("1", "🔌")])
    wc = SelectField('Toilet Availability: ',
                     choices=[("0", "Nope"), ("1", "Yes")])
    calls = SelectField('Can take calls:',
                        choices=[("0", "Nope"), ("1", "Yes")])
    seats = StringField('Number of seats:',
                        validators=[DataRequired()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route("/", methods=["GET", "DELETE"])
def home():
    all_cafes = db.session.query(Cafe).all()
    cafes = [cafe.to_dict() for cafe in all_cafes]
    return render_template("index.html", cafe_list=cafes)


def boolean_convert(to_convert):
    if to_convert == "1":
        return bool(to_convert)
    else:
        return 0


@app.route("/add", methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=request.form['cafe'],
            map_url=request.form["location_url"],
            img_url=request.form["image"],
            location=request.form["location"],
            seats=request.form["seats"],
            has_toilet=boolean_convert(request.form["wc"]),
            has_wifi=boolean_convert(request.form["wifi"]),
            has_sockets=boolean_convert(request.form["power"]),
            can_take_calls=boolean_convert(request.form["calls"]),
            coffee_price=f"£{request.form['coffee_price']}"
        )
        db.session.add(new_cafe)
        # db.session.rollback()
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("products.html", form=form)


@app.route("/report-closed/<int:index>")
def close_cafe(index):
    cafe_to_delete = db.session.query(Cafe).get(index)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
