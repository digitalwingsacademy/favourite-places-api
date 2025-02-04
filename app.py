from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from google.cloud.sql.connector import Connector
import sqlalchemy
import os
from sqlalchemy import String, func
from sqlalchemy.orm import relationship

load_dotenv()

# Initialize Connector object
connector = Connector()

# Python Connector database connection function
def getconn():
    conn = connector.connect(
        os.environ.get("CLOUD_SQL_CONNECTION_NAME"),  # Nombre de la conexión de la instancia
        "pymysql",
        user=os.environ.get("CLOUD_SQL_USERNAME"),
        password=os.environ.get("CLOUD_SQL_PASSWORD"),
        db=os.environ.get("CLOUD_SQL_DATABASE_NAME"),
        ip_type="PUBLIC"  # Cambiar a "private" si se usa IP privada
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

# Modelo de base de datos
class Place(db.Model):
    __tablename__ = "favourite_places"

    student = db.Column(db.String(255), primary_key=True)
    place = db.Column(db.String(255), primary_key=True)
    coordinates = db.Column(db.String(50))

    reason = db.Column(db.String(255))
    emoji = db.Column(db.String(10), nullable=True)
    activity = db.Column(db.String(100), nullable=True)
    memory = db.Column(db.String(255), nullable=True)
    companions = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    # Relación con Likes
    place_likes = relationship('Like', backref='liked_place', cascade='all, delete-orphan')

class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    student_liking = db.Column(db.String(255), nullable=False)
    place_id = db.Column(db.String(255), db.ForeignKey('favourite_places.place', ondelete="CASCADE"), nullable=False)

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
        place=data["place"],
        coordinates=data["coordinates"],
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

@app.route('/like', methods=['POST'])
def like_place():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.get_json()
    student = data.get("student")
    place = data.get("place")

    # Verificar si el estudiante ya ha dado like a este sitio
    existing_like = Like.query.filter_by(student_liking=student, place_id=place).first()
    if existing_like:
        return jsonify({"msg": "¡Ya has dado like a este sitio!"}), 400

    # Si no ha dado like, agregarlo
    new_like = Like(student_liking=student, place_id=place)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({"msg": "Like agregado correctamente"})

@app.route('/likes', methods=['GET'])
def get_likes():
    likes = db.session.query(Like.place_id, func.count(Like.id).label("likes"))
    likes = likes.group_by(Like.place_id).all()

    return jsonify([
        {
            "place": like.place_id,
            "likes": like.likes
        }
        for like in likes
    ])

@app.route('/likes/<place>', methods=['GET'])
def get_likes_for_place(place):
    likes_count = db.session.query(func.count(Like.id)).filter(Like.place_id == place).scalar()
    return jsonify({
        "place": place,
        "likes": likes_count
    })

if __name__ == '__main__':
    app.run()
