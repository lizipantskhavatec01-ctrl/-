from app import app, db
from models import User, Subject

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(username='admin', email='admin@test.com', password='123', is_admin=True)
    db.session.add(admin)
    db.session.commit()

    print("ბაზა წარმატებით შეიქმნა static/uploads საქაღალდესთან ერთად!")