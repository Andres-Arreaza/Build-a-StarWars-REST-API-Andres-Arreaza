"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Films, People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
def get_users():
    usuarios = User.query.all()
    usuarioslist = [usuario.serialize() for usuario in usuarios]

    return jsonify(usuarioslist),200

@app.route('/users/favorites')
def get_user_favorites():
    current_user_id = 1
    user = User.query.get(current_user_id)
    favorite_planets = user.favorite_planets
    favorite_people = user.favorite_people

    return jsonify({
        "planets" : [planet.serialize() for planet in favorite_planets],
        "people": [people.serialize() for people in favorite_people]
    }),200

@app.route('/favorite/planet/<int:id>', methods=['POST', 'DELETE'])
def manage_favorite_planet(id):
    current_user_id = 1
    user = User.query.get(current_user_id)
    planet = Planets.query.get(id)
    if not planet:
        return jsonify({"msg": "Planeta no encontrado"}),404
    if request.method == 'POST':
        if planet in user.favorite_planets:
            return jsonify({"msg": "Este planeta ya se encuentra como favorito"}),202
        
        user.favorite_planets.append(planet)
        db.session.commit()
        return jsonify({"msg": "Planet added successfully"}),200
    
    if request.method == 'DELETE':
        if not planet in user.favorite_planets:
            return jsonify({"msg": "Este planeta no se encuentra como favorito"}),202
        
        user.favorite_planets.remove(planet)
        db.session.commit()
        return jsonify({"msg": "Planet removed successfully"}),201
    
@app.route('/favorite/people/<int:id>', methods=['POST', 'DELETE'])
def manage_favorite_people(id):
    current_user_id = 1
    user = User.query.get(current_user_id)
    people = People.query.get(id)

    if not people:
        return jsonify({"msg": "Personaje no encontrado"}),404
    
    if request.method == 'POST':
        if people in user.favorite_people:
            return jsonify({"msg": "Este Personaje ya se encuentra como favorito"}),202
        
        user.favorite_people.append(people)
        db.session.commit()
        return jsonify({"msg": "People added successfully"}),200
        
    if request.method == 'DELETE':
        
        if not people in user.favorite_people:
            return jsonify({"msg": "Este personaje no se encuentra como favorito"}),202
        
        user.favorite_people.remove(people)
        db.session.commit()
        return jsonify({"msg": "People removed successfully"}),201

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    result= [people.serialize() for people in people]
    return jsonify(result),200

@app.route('/people/<int:id>', methods=['GET'])
def get_people_by_id(id):
    people = People.query.filter_by(id=id).first()

    return jsonify(people.serialize()),200


@app.route('/planets', methods=['GET'])
def get_planets():
    planetas = Planets.query.all()
    serialized_planets = [planeta.serialize() for planeta in planetas]
    return jsonify(serialized_planets), 200


@app.route('/planets/<int:id>', methods=['GET'])
def get_planet_by_id(id):
    planeta = Planets.query.get_or_404(id)

    if planeta:
        return jsonify(planeta.serialize()), 200
    
    return jsonify({"msg": "Planet not found"}),404



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
