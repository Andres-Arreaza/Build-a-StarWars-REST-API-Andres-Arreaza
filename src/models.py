from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    favorite_planets = db.relationship('Planets', secondary='favorite_planets', backref='fans')
    favorite_people = db.relationship('People', secondary='favorite_people', backref='fans')


    def __repr__(self):
        return f"<User:(name: {self.name} - email: {self.email})>"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name
            # do not serialize the password, its a security breach
        }


# Tablas Intermedias
films_planets = db.Table('films_planets',
    db.Column('film_id', db.Integer, db.ForeignKey('films.id')),
    db.Column('planet_id', db.Integer, db.ForeignKey('planets.id'))
)

films_people = db.Table('films_people',
    db.Column('film_id', db.Integer, db.ForeignKey('films.id')),
    db.Column('people_id', db.Integer, db.ForeignKey('people.id'))
)

favorite_planets = db.Table('favorite_planets',
                           db.Column('planet_id', db.Integer, db.ForeignKey('planets.id')),
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

favorite_people = db.Table('favorite_people',
                           db.Column('people_id', db.Integer, db.ForeignKey('people.id')),
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

class Films(db.Model):
    __tablename__ = 'films'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25))
    episode_number = db.Column(db.Integer, unique=True)
    director = db.Column(db.String(50))
    productor = db.Column(db.String(50))
    release_date = db.Column(db.String(50))
    
    planets = db.relationship('Planets', secondary=films_planets, back_populates='films')
    people = db.relationship('People', secondary=films_people, back_populates='films')


class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(200))
    gender = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))
    hair_color = db.Column(db.String(50))
    height = db.Column(db.String(50))
    home_world = db.Column(db.Integer, db.ForeignKey('planets.id'))

    home_planet = db.relationship('Planets')
    films = db.relationship('Films', secondary=films_people, back_populates='people')

    def serialize(self):
        return {
            "id": self.id,
            "name":self.name,
            "description": self.description,
            "gender": self.gender,
            "eye_color": self.eye_color,
            "hair_color": self.hair_color,
            "height": self.height,
            "home_world": self.home_planet.name if self.home_planet else None
        }


class Planets(db.Model):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    terrain = db.Column(db.String(100))
    population = db.Column(db.Integer)
    climate = db.Column(db.String(50))
    gravity = db.Column(db.String(50))

    films = db.relationship('Films', secondary=films_planets, back_populates='planets')

    def __repr__(self):
        return f"<Planet:( id: {self.id}, name: {self.name})>"

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "terrain": self.terrain,
            "population": self.population,
            "climate": self.climate,
            "gravity": self.gravity
        }
