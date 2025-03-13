from blueprints.extensions import db  # Importowanie db z nowego pliku
from datetime import datetime

szkolenie_kandydaci = db.Table(
    'szkolenie_kandydaci',
    db.Column('szkolenie_id', db.Integer, db.ForeignKey('szkolenie.id'), primary_key=True),
    db.Column('kandydat_id', db.Integer, db.ForeignKey('kandydaci.id'), primary_key=True)
)

class Ogłoszenie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tytul = db.Column(db.String(255), nullable=False)
    opis = db.Column(db.Text, nullable=False)
    platforma = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False)
    data_publikacji = db.Column(db.Date, nullable=False)
    data_wygasniecia = db.Column(db.Date, nullable=False)
    data_utworzenia = db.Column(db.DateTime, default=datetime.utcnow)  # NOWE: data utworzenia wpisu

    @property
    def status(self) -> str:
        if self.data_wygasniecia:
            days_remaining = (self.data_wygasniecia - datetime.utcnow().date()).days
            return f"{days_remaining} dni do końca" if days_remaining >= 0 else "Wygasło"
        return "Brak daty wygaśnięcia"

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
    
    uczestnictwa = db.relationship("Uczestnictwo", back_populates="kandydat")



class Spotkanie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kandydat_id = db.Column(db.Integer, db.ForeignKey('kandydaci.id'), nullable=False)
    telefon = db.Column(db.String(20), nullable=False)  # 🔴 Nowe pole - numer telefonu
    data = db.Column(db.DateTime, nullable=True)
    opis = db.Column(db.Text)

    kandydat = db.relationship('Kandydat', backref='spotkania')


class Szkolenie(db.Model):
    __tablename__ = 'szkolenie'
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(255), nullable=False)
    opis = db.Column(db.Text)
    data = db.Column(db.DateTime, nullable=False)
    prowadzacy = db.Column(db.String(255))
    miejsce = db.Column(db.String(255))
    # Usunięto pole decyzja – decyzja będzie przechowywana indywidualnie dla uczestnictwa

    uczestnictwa = db.relationship("Uczestnictwo", back_populates="szkolenie", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f'<Szkolenie {self.nazwa} on {self.data}>'




class Historia(db.Model):
    __tablename__ = 'historia'
    id = db.Column(db.Integer, primary_key=True)
    kandydat_id = db.Column(db.Integer, db.ForeignKey('kandydaci.id', ondelete='CASCADE'), nullable=False)
    data_zatrudnienia = db.Column(db.Date, nullable=False)
    stanowisko = db.Column(db.String(100), nullable=False)

    kandydat = db.relationship('Kandydat', back_populates='historia')

class Uczestnictwo(db.Model):
    __tablename__ = 'uczestnictwo'
    szkolenie_id = db.Column(db.Integer, db.ForeignKey('szkolenie.id'), primary_key=True)
    kandydat_id = db.Column(db.Integer, db.ForeignKey('kandydaci.id'), primary_key=True)
    decyzja = db.Column(db.String(50), default="")  # np. "", "zatrudnij", "historia"

    # Relacje
    szkolenie = db.relationship("Szkolenie", back_populates="uczestnictwa")
    kandydat = db.relationship("Kandydat", back_populates="uczestnictwa")

