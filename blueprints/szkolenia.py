from flask import Blueprint, render_template, request, redirect, url_for, flash
from blueprints.extensions import db  # Importowanie db z nowego pliku
from blueprints.models import Szkolenie

szkolenia_bp = Blueprint("szkolenia_bp", __name__, template_folder="../templates/szkolenia")

@szkolenia_bp.route("/")
def lista_szkolen():
    szkolenia = Szkolenie.query.all()
    return render_template("szkolenia_lista.html", szkolenia=szkolenia)

@szkolenia_bp.route("/dodaj", methods=["GET", "POST"])
def dodaj_szkolenie():
    if request.method == "POST":
        temat = request.form.get("temat")
        opis = request.form.get("opis")
        data = request.form.get("data")
        if temat and data:
            nowe_szkolenie = Szkolenie(temat=temat, opis=opis, data=data)
            db.session.add(nowe_szkolenie)
            db.session.commit()
            flash("Szkolenie zostało dodane!", "success")
            return redirect(url_for("szkolenia_bp.lista_szkolen"))
        flash("Wypełnij wszystkie wymagane pola.", "danger")
    return render_template("szkolenia_dodaj.html")
