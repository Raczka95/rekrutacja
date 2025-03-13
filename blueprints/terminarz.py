from flask import Blueprint, render_template, request, redirect, url_for, flash
from blueprints.extensions import db  # Importowanie db z nowego pliku
from blueprints.models import Spotkanie, Kandydat, Szkolenie, Historia
from datetime import datetime

terminarz_bp = Blueprint("terminarz_bp", __name__, template_folder="../templates")

@terminarz_bp.route("/")
def lista_spotkan():
    sortowanie = request.args.get("sortowanie", "data")  # Domyślnie sortuj według daty
    kierunek = request.args.get("kierunek", "asc")  # Domyślnie rosnąco

    # Pobieramy spotkania, sortując według daty
    spotkania = Spotkanie.query.order_by(
        Spotkanie.data.asc() if kierunek == "asc" else Spotkanie.data.desc()
    ).all()

    # Filtrowanie po kandydatach, jeśli jest zapytanie
    kandydat_filter = request.args.get("kandydat", "").strip()
    if kandydat_filter:
        spotkania = [
            s for s in spotkania
            if kandydat_filter.lower() in f"{s.kandydat.imie} {s.kandydat.nazwisko}".lower()
        ]

    return render_template(
        "terminarz/terminarz_lista.html",
        spotkania=spotkania,
        sortowanie=sortowanie,
        kierunek=kierunek,
        kandydat_filter=kandydat_filter,
    )

@terminarz_bp.route("/dodaj", methods=["GET", "POST"])
def dodaj_spotkanie():
    kandydaci = Kandydat.query.all()
    
    if request.method == "POST":
        kandydat_id = request.form.get("kandydat_id")
        data = request.form.get("data")
        opis = request.form.get("opis")

        kandydat = Kandydat.query.get(kandydat_id)  # 🔴 Pobranie obiektu kandydata
        if not kandydat:
            flash("Wybrany kandydat nie istnieje.", "danger")
            return redirect(url_for("terminarz_bp.lista_spotkan"))

        if kandydat_id and data:
            try:
                data = datetime.strptime(data, "%Y-%m-%dT%H:%M")

                nowe_spotkanie = Spotkanie(
                    kandydat_id=kandydat_id, 
                    telefon=kandydat.telefon,  # 🔴 Pobranie numeru telefonu
                    data=data, 
                    opis=opis
                )
                db.session.add(nowe_spotkanie)
                db.session.commit()

                flash("Spotkanie zostało dodane!", "success")
                return redirect(url_for("terminarz_bp.lista_spotkan"))

            except ValueError:
                flash("Nieprawidłowy format daty! Użyj pola wyboru daty.", "danger")

        else:
            flash("Wypełnij wszystkie wymagane pola.", "danger")

    return render_template("terminarz/terminarz_dodaj.html", kandydaci=kandydaci)


@terminarz_bp.route("/edytuj/<int:id>", methods=["GET", "POST"])
def edytuj_spotkanie(id):
    spotkanie = Spotkanie.query.get_or_404(id)
    kandydaci = Kandydat.query.all()

    if request.method == "POST":
        spotkanie.kandydat_id = request.form.get("kandydat_id")
        
        # ✅ Sprawdzamy, czy użytkownik podał datę
        data_str = request.form.get("data")
        if data_str:
            spotkanie.data = datetime.strptime(data_str, "%Y-%m-%dT%H:%M")
        else:
            spotkanie.data = None  # ✅ Pozostaw pustą datę, jeśli nie podano

        spotkanie.opis = request.form.get("opis")
        db.session.commit()
        flash("Spotkanie zostało zaktualizowane!", "success")
        return redirect(url_for("terminarz_bp.lista_spotkan"))

    return render_template("terminarz/terminarz_edytuj.html", spotkanie=spotkanie, kandydaci=kandydaci)


@terminarz_bp.route("/usun/<int:id>", methods=["POST"])
def usun_spotkanie(id):
    spotkanie = Spotkanie.query.get_or_404(id)
    db.session.delete(spotkanie)
    db.session.commit()
    flash("Spotkanie zostało usunięte!", "success")
    return redirect(url_for("terminarz_bp.lista_spotkan"))

@terminarz_bp.route("/przenies/<int:spotkanie_id>/<string:cel>", methods=["POST"])
def przenies_kandydata(spotkanie_id, cel):
    spotkanie = Spotkanie.query.get_or_404(spotkanie_id)
    kandydat = Kandydat.query.get_or_404(spotkanie.kandydat_id)

    if cel == "szkolenie":
        nowe_szkolenie = Szkolenie(
            temat=f"Szkolenie dla {kandydat.imie} {kandydat.nazwisko}",
            opis="Nowy kandydat na szkoleniu",
            data=datetime.utcnow()
        )
        db.session.add(nowe_szkolenie)

    elif cel == "historia":
        nowa_historia = Historia(
            kandydat_id=kandydat.id,
            data_zatrudnienia=datetime.utcnow().date(),
            stanowisko="Nowy pracownik"
        )
        db.session.add(nowa_historia)

    elif cel == "kandydaci":
        kandydat.status = "Nie zdecydowany"
        db.session.add(kandydat)

    # Usuwamy spotkanie po przeniesieniu
    db.session.delete(spotkanie)

    try:
        db.session.commit()
        flash(f"Kandydat {kandydat.imie} {kandydat.nazwisko} został przeniesiony do {cel}!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Błąd podczas przenoszenia: {e}", "danger")

    return redirect(url_for("terminarz_bp.lista_spotkan"))
