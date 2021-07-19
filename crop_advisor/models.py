from crop_advisor import db,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Approval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(40), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Approval('{self.username}', '{self.email}', '{self.image_file}')"
    
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(40), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.email}')"
    
class Cropname(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    crop=db.Column(db.String(30), nullable=False)
    
    def __repr__(self):
        return f"Cropname('{self.crop}')"
        
class CropPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop = db.Column(db.String(40), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"Cropname('{self.crop},'{self.price}')"
    
class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    subject=db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(150),nullable=False)
    
    def __repr__(self):
        return f"Messages('{self.email},'{self.subject}','{self.message}')"
    
        
db.create_all()
