from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from typing import Any, List
from blueprints.extensions import db
from blueprints.models import Spotkanie, Kandydat, Szkolenie, Historia

terminarz_bp = Blueprint("terminarz_bp", __name__, template_folder="../templates")

@terminarz_bp.route("/")
def lista_spotkan() -> str:
    sortowanie: str = request.args.get("sortowanie", "data")
    kierunek: str = request.args.get("kierunek", "asc")

    # Pobieramy spotkania i sortujemy według daty
    spotkania: List[Spotkanie] = Spotkanie.query.order_by(
        Spotkanie.data.asc() if kierunek == "asc" else Spotkanie.data.desc()
    ).all()

    # Filtrowanie po kandydatach, jeśli podano zapytanie
    kandydat_filter: str = request.args.get("kandydat", "").strip()
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
def dodaj_spotkanie() -> str:
    kandydaci = Kandydat.query.all()
    
    if request.method == "POST":
        kandydat_id = request.form.get("kandydat_id")
        data_str = request.form.get("data")
        opis = request.form.get("opis")
        
        kandydat = Kandydat.query.get(kandydat_id)
        if not kandydat:
            flash("Wybrany kandydat nie istnieje.", "danger")
            return redirect(url_for("terminarz_bp.lista_spotkan"))

        if kandydat_id and data_str:
            try:
                data = datetime.strptime(data_str, "%Y-%m-%dT%H:%M")
                nowe_spotkanie = Spotkanie(
                    kandydat_id=kandydat_id, 
                    telefon=kandydat.telefon,
                    data=data, 
                    opis=opis
                )
                db.session.add(nowe_spotkanie)
                db.session.commit()
                flash("Spotkanie zostało dodane!", "success")
                return redirect(url_for("terminarz_bp.lista_spotkan"))
            except ValueError:
                flash("Nieprawidłowy format daty! Użyj pola wyboru daty.", "danger")
            except Exception as e:
                db.session.rollback()
                flash(f"Błąd zapisu do bazy: {e}", "danger")
        else:
            flash("Wypełnij wszystkie wymagane pola.", "danger")

    return render_template("terminarz/terminarz_dodaj.html", kandydaci=kandydaci)

@terminarz_bp.route("/edytuj/<int:id>", methods=["GET", "POST"])
def edytuj_spotkanie(id: int) -> str:
    spotkanie = Spotkanie.query.get_or_404(id)
    kandydaci = Kandydat.query.all()
    if request.method == "POST":
        spotkanie.kandydat_id = request.form.get("kandydat_id")
        data_str = request.form.get("data")
        if data_str:
            try:
                spotkanie.data = datetime.strptime(data_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Nieprawidłowy format daty!", "danger")
                return redirect(url_for("terminarz_bp.edytuj_spotkanie", id=id))
        else:
            spotkanie.data = None
        # Pobranie nowej wartości opisu
        new_opis = request.form.get("opis")
        print("DEBUG: Nowy opis:", new_opis)  # Debug - sprawdź, czy wartość jest pobierana
        spotkanie.opis = new_opis
        try:
            db.session.commit()
            flash("Spotkanie zostało zaktualizowane!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Błąd podczas aktualizacji: {e}", "danger")
        return redirect(url_for("terminarz_bp.lista_spotkan"))
    return render_template("terminarz/terminarz_edytuj.html", spotkanie=spotkanie, kandydaci=kandydaci)


@terminarz_bp.route("/usun/<int:id>", methods=["POST"])
def usun_spotkanie(id: int) -> str:
    spotkanie = Spotkanie.query.get_or_404(id)
    try:
        db.session.delete(spotkanie)
        db.session.commit()
        flash("Spotkanie zostało usunięte!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Błąd podczas usuwania: {e}", "danger")
    return redirect(url_for("terminarz_bp.lista_spotkan"))

@terminarz_bp.route("/przenies/<int:spotkanie_id>/<string:cel>", methods=["POST"])
def przenies_kandydata(spotkanie_id: int, cel: str) -> str:
    spotkanie = Spotkanie.query.get_or_404(spotkanie_id)
    kandydat = Kandydat.query.get_or_404(spotkanie.kandydat_id)

    if cel == "szkolenie":
        # Zamiast tworzyć nowe szkolenie automatycznie,
        # przekierowujemy do widoku, w którym można wybrać istniejące szkolenie
        return redirect(url_for("terminarz_bp.przenies_do_szkolenia", kandydat_id=kandydat.id))
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

@terminarz_bp.route("/przenies_do_szkolenia", methods=["GET", "POST"])
def przenies_do_szkolenia():
    from blueprints.models import Kandydat, Szkolenie, Uczestnictwo  # lokalny import
    kandydat_id = request.args.get("kandydat_id")
    kandydat = Kandydat.query.get_or_404(kandydat_id)
    szkolenia = Szkolenie.query.order_by(Szkolenie.data.asc()).all()
    if request.method == "POST":
        szkolenie_id = request.form.get("szkolenie_id")
        szkolenie = Szkolenie.query.get_or_404(szkolenie_id)
        # Sprawdzamy, czy kandydat nie jest już zapisany do szkolenia
        if not any(u.kandydat_id == kandydat.id for u in szkolenie.uczestnictwa):
            nowe_uczestnictwo = Uczestnictwo(szkolenie_id=szkolenie.id, kandydat_id=kandydat.id)
            szkolenie.uczestnictwa.append(nowe_uczestnictwo)
            kandydat.status = "Zaplanowany na szkolenie"
        try:
            db.session.commit()
            flash("Kandydat został dopisany do szkolenia.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Błąd podczas dopisywania do szkolenia: {e}", "danger")
        return redirect(url_for('terminarz_bp.lista_spotkan'))
    return render_template("przenies_do_szkolenia.html", kandydat=kandydat, szkolenia=szkolenia)

