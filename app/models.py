from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    matricule = db.Column(db.String(15), unique=True, nullable=False)
    fonction = db.Column(db.String(150), nullable=False)
    prenom = db.Column(db.String(150), nullable=False)
    shift = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    profile_image = db.Column(db.String(150), nullable=True)
    password = db.Column(db.String(200), nullable=False)
    # Ensure this is a boolean field
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)  # New field
    last_update = db.Column(db.DateTime, default=datetime.utcnow)
    # New column for approval
    is_approved = db.Column(db.Boolean, default=False)
    tasks = db.relationship('Todo', backref='user',
                            lazy=True, cascade="all, delete-orphan")
    is_pending = db.Column(db.Boolean, default=True)

    def update_last_seen(self):
        self.last_update = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

    def get_id(self):
        return str(self.id)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Consider if this should be nullable
    content = db.Column(db.String(200), nullable=True)
    shift = db.Column(db.String(50))
    poste = db.Column(db.String(50))
    navire = db.Column(db.String(50))
    grue = db.Column(db.String(50))
    marchandise = db.Column(db.String(50))
    nb_cs_pcs = db.Column(db.String(50))
    unite = db.Column(db.String(50))
    raclage = db.Column(db.String(50))
    comentaire = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key relationship to User model
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Track if the task is validated
    is_validated = db.Column(db.Boolean, default=False)
    # Name of the admin who validated it
    validated_by = db.Column(db.String(150), nullable=True)
    # Track task status
    status = db.Column(db.String(50), default='pending')
    remark = db.Column(db.String(255), nullable=True)
    Escale = db.Column(db.String(15), nullable=True)  # Make nullable

    def __repr__(self):
        return f'<Task {self.id}>'
