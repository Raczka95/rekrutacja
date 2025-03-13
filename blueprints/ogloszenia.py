from flask import Blueprint, render_template, request, redirect, url_for, flash
from blueprints.extensions import db
from blueprints.models import Ogłoszenie
from datetime import datetime

ogloszenia_bp = Blueprint("ogloszenia_bp", __name__, template_folder="../templates/ogloszenia")

@ogloszenia_bp.route("/")
def lista_ogloszen() -> str:
    # Pobieramy wszystkie ogłoszenia; status jest obliczany w modelu.
    ogloszenia = Ogłoszenie.query.all()
    return render_template("lista.html", ogloszenia=ogloszenia)

@ogloszenia_bp.route("/dodaj", methods=["GET", "POST"])
def dodaj_ogloszenie() -> str:
    if request.method == "POST":
        tytul = request.form.get("tytul")
        opis = request.form.get("opis")
        platforma = request.form.get("platforma")
        link = request.form.get("link")
        data_publikacji = request.form.get("data_publikacji")
        data_wygasniecia = request.form.get("data_wygasniecia")

        if tytul and opis and platforma and link and data_publikacji and data_wygasniecia:
            try:
                nowe_ogloszenie = Ogłoszenie(
                    tytul=tytul,
                    opis=opis,
                    platforma=platforma,
                    link=link,
                    data_publikacji=datetime.strptime(data_publikacji, "%Y-%m-%d").date(),
                    data_wygasniecia=datetime.strptime(data_wygasniecia, "%Y-%m-%d").date()
                )
                db.session.add(nowe_ogloszenie)
                db.session.commit()
                flash("Ogłoszenie zostało dodane!", "success")
                return redirect(url_for("ogloszenia_bp.lista_ogloszen"))
            except Exception as e:
                db.session.rollback()
                flash("Wystąpił błąd podczas dodawania ogłoszenia.", "danger")
        else:
            flash("Wypełnij wszystkie pola.", "danger")
    return render_template("dodaj.html")
