from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from google.cloud.sql.connector import Connector
import sqlalchemy
import os
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

load_dotenv()

# initialize Connector object
connector = Connector()

# Python Connector database connection function
def getconn():
    conn = connector.connect(
        "your_cloud_run_function_id", # Cloud SQL Instance Connection Name
        "pymysql",
        user="ardlema",
        password="database_password",
        db="favourite_places",
        ip_type="PUBLIC"  # "private" for private IP
    )
    return conn

app = Flask(__name__)
CORS(app)


app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')

# Configure Flask-SQLAlchemy to use Python Connector
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:password@localhost/placeholder"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"creator": getconn}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#Modelo de base de datos
class Place(db.Model):
    __tablename__ = "favourite_places"

    # Clave primaria compuesta
    student = db.Column(db.String(255), primary_key=True)
    place = db.Column(db.String(255), primary_key=True)  # Ahora almacena el nombre del sitio
    coordinates = db.Column(db.String(50))  # Nueva columna para las coordenadas (latitud, longitud)
    
    # Otras columnas
    reason = db.Column(db.String(255))
    emoji = db.Column(db.String(10), nullable=True)
    activity = db.Column(db.String(100), nullable=True)
    memory = db.Column(db.String(255), nullable=True)
    companions = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)




@app.route('/')
def get_places():
    places = db.session.query(Place).all()
    return jsonify([
        {
            "student": place.student,
            "place": place.place,
            "coordinates": place.coordinates,
            "reason": place.reason,
            "emoji": place.emoji,
            "activity": place.activity,
            "memory": place.memory,
            "companions": place.companions,
            "image_url": place.image_url
        }
        for place in places
    ])


@app.route('/add', methods=['POST'])
def add_place():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.get_json()
    new_place = Place(
        student=data["student"],
        place=data["place"],  # Nombre del sitio
        coordinates=data["coordinates"],  # Latitud y longitud
        reason=data.get("reason"),
        emoji=data.get("emoji"),
        activity=data.get("activity"),
        memory=data.get("memory"),
        companions=data.get("companions"),
        image_url=data.get("image_url")
    )
    db.session.add(new_place)
    db.session.commit()
    return jsonify({"msg": "Place added"})

# initialize the app with the extension
if __name__ == '__main__':
    app.run()