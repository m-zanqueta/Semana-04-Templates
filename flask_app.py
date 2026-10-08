from app import create_app, db
from app.models import User, Role, SentEmail

app = create_app()

with app.app_context():
    db.create_all()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, SentEmail=SentEmail)

if __name__ == '__main__':
    app.run(debug=True)