from blueprints.extensions import db  # Importowanie db z nowego pliku

class Ogłoszenie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tytul = db.Column(db.String(120), nullable=False)
    opis = db.Column(db.Text, nullable=False)
    platforma = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    data_publikacji = db.Column(db.Date, nullable=False)
    data_wygasniecia = db.Column(db.Date, nullable=False)
    data_utworzenia = db.Column(db.DateTime, default=db.func.now())

class Kandydat(db.Model):
    __tablename__ = 'kandydaci'
    id = db.Column(db.Integer, primary_key=True)
    imie = db.Column(db.String(100), nullable=False)
    nazwisko = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefon = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    data_kontaktu = db.Column(db.Date, nullable=True)
    historia = db.relationship('Historia', back_populates='kandydat', cascade="all, delete-orphan")


class Spotkanie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kandydat_id = db.Column(db.Integer, db.ForeignKey('kandydaci.id'), nullable=False)
    telefon = db.Column(db.String(20), nullable=False)  # 🔴 Nowe pole - numer telefonu
    data = db.Column(db.DateTime, nullable=True)
    opis = db.Column(db.Text)

    kandydat = db.relationship('Kandydat', backref='spotkania')


class Szkolenie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temat = db.Column(db.String(120), nullable=False)
    opis = db.Column(db.Text)
    data = db.Column(db.DateTime, nullable=False)


class Historia(db.Model):
    __tablename__ = 'historia'
    id = db.Column(db.Integer, primary_key=True)
    kandydat_id = db.Column(db.Integer, db.ForeignKey('kandydaci.id', ondelete='CASCADE'), nullable=False)
    data_zatrudnienia = db.Column(db.Date, nullable=False)
    stanowisko = db.Column(db.String(100), nullable=False)

    kandydat = db.relationship('Kandydat', back_populates='historia')
