from app import create_app
from models import db

app = create_app()

with app.app_context():
    db.drop_all()   # Remove todas as tabelas
    db.create_all() # Cria as tabelas do zero com as novas colunas
