from flask import Flask, render_template
from blueprints.extensions import db, migrate
from blueprints.ogloszenia import ogloszenia_bp
from blueprints.kandydaci import kandydaci_bp
from blueprints.terminarz import terminarz_bp
from blueprints.szkolenia import szkolenia_bp
from blueprints.historia import historia_bp
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rekrutacja.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'test')
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

# Inicjalizacja rozszerzeń
db.init_app(app)
migrate.init_app(app, db)

# Rejestracja blueprintów
app.register_blueprint(ogloszenia_bp, url_prefix='/ogloszenia')
app.register_blueprint(kandydaci_bp, url_prefix='/kandydaci')
app.register_blueprint(terminarz_bp, url_prefix='/terminarz')
app.register_blueprint(szkolenia_bp, url_prefix='/szkolenia')
app.register_blueprint(historia_bp, url_prefix='/historia')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
