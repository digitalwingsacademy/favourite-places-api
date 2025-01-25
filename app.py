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

#Modelo de base de datos
class Place(db.Model):
    __tablename__ = "favourite_places"

    # Clave primaria compuesta
    student = db.Column(db.String(255), primary_key=True)
    place = db.Column(db.String(255), primary_key=True)
    coordinates = db.Column(db.String(50))

    # Otras columnas
    reason = db.Column(db.String(255))
    emoji = db.Column(db.String(10), nullable=True)
    activity = db.Column(db.String(100), nullable=True)
    memory = db.Column(db.String(255), nullable=True)
    companions = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    # Relación con Likes (ajustando el backref)
    place_likes = db.relationship(
        'Like',
        backref='liked_place',  # Renombramos el backref para evitar conflictos
        primaryjoin="and_(Place.student == foreign(Like.student), Place.place == foreign(Like.place))",
        cascade='all, delete-orphan'
    )

class Like(db.Model):
    __tablename__ = "likes"

    # Clave primaria y columnas
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student = db.Column(db.String(255), nullable=False)  # Clave foránea (student)
    place = db.Column(db.String(255), nullable=False)  # Clave foránea (place)
    ip_address = db.Column(db.String(50), nullable=False)  # Dirección IP

    # Relación explícita con Place mediante claves foráneas
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['student', 'place'],  # Columnas en Like
            ['favourite_places.student', 'favourite_places.place'],  # Columnas en Place
            ondelete="CASCADE"
        ),
    )

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


@app.route('/like', methods=['POST'])
def like_place():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    data = request.get_json()
    user_ip = request.remote_addr  # Capturar la dirección IP del cliente

    new_like = Like(
        student=data["student"],
        place=data["place"],
        ip_address=user_ip
    )

    try:
        db.session.add(new_like)
        db.session.commit()
        return jsonify({"msg": "Like added"})
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return jsonify({"msg": "You have already liked this place"}), 400


@app.route('/likes', methods=['GET'])
def get_likes():
    likes = db.session.query(Like.student, Like.place, db.func.count(Like.id).label("likes"))
    likes = likes.group_by(Like.student, Like.place).all()

    return jsonify([
        {
            "student": like.student,
            "place": like.place,
            "likes": like.likes
        }
        for like in likes
    ])


@app.route('/likes/<student>/<place>', methods=['GET'])
def get_likes_for_place(student, place):
    likes_count = db.session.query(db.func.count(Like.id)).filter(
        Like.student == student, Like.place == place
    ).scalar()

    return jsonify({
        "student": student,
        "place": place,
        "likes": likes_count
    })

# initialize the app with the extension
if __name__ == '__main__':
    app.run()