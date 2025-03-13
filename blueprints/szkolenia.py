from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from typing import List
from blueprints.extensions import db
from blueprints.models import Szkolenie, Kandydat, Spotkanie, Uczestnictwo  # Zakładamy, że Kandydat/Spotkanie są dostępne

szkolenia_bp = Blueprint("szkolenia_bp", __name__, template_folder="../templates/szkolenia")

@szkolenia_bp.route("/")
def lista_szkolen() -> str:
    # Pobieramy szkolenia, sortujemy rosnąco według daty
    szkolenia: List[Szkolenie] = Szkolenie.query.order_by(Szkolenie.data.asc()).all()
    return render_template("szkolenia_lista.html", szkolenia=szkolenia)

@szkolenia_bp.route("/dodaj", methods=["GET", "POST"])
def dodaj_szkolenie() -> str:
    # Pobieramy tylko kandydatów, którzy są w terminarzu i nie mają przypisanego szkolenia (uczestnictwa)
    kandydaci: List[Kandydat] = Kandydat.query.filter(
        Kandydat.spotkania.any(),
        ~Kandydat.uczestnictwa.any()
    ).all()
    
    if request.method == "POST":
        nazwa = request.form.get("nazwa")
        data_str = request.form.get("data")  # Format: "2025-03-15T14:30"
        prowadzacy = request.form.get("prowadzacy")
        miejsce = request.form.get("miejsce")
        kandydat_ids = request.form.getlist("kandydat_ids")  # Wielokrotny wybór kandydatów

        if nazwa and data_str:
            try:
                data = datetime.strptime(data_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Nieprawidłowy format daty i godziny!", "danger")
                return redirect(url_for("szkolenia_bp.dodaj_szkolenie"))
            
            nowe_szkolenie = Szkolenie(
                nazwa=nazwa,
                data=data,
                prowadzacy=prowadzacy,
                miejsce=miejsce,
                decyzja=""
            )
            # Dodajemy wybranych kandydatów do szkolenia poprzez tworzenie obiektu Uczestnictwo
            for cid in kandydat_ids:
                kand = Kandydat.query.get(cid)
                if kand:
                    uczestnictwo = Uczestnictwo(kandydat=kand)
                    nowe_szkolenie.uczestnictwa.append(uczestnictwo)
            try:
                db.session.add(nowe_szkolenie)
                db.session.commit()
                flash("Szkolenie zostało dodane!", "success")
                return redirect(url_for("szkolenia_bp.lista_szkolen"))
            except Exception as e:
                db.session.rollback()
                flash(f"Błąd zapisu do bazy: {e}", "danger")
        else:
            flash("Wypełnij wymagane pola: nazwa i data.", "danger")
    return render_template("szkolenia_dodaj.html", kandydaci=kandydaci)




@szkolenia_bp.route("/edytuj/<int:id>", methods=["GET", "POST"])
def edytuj_szkolenie(id: int) -> str:
    szkolenie = Szkolenie.query.get_or_404(id)
    from blueprints.models import Kandydat
    kandydaci: List[Kandydat] = Kandydat.query.all()
    
    if request.method == "POST":
        szkolenie.nazwa = request.form.get("nazwa")
        szkolenie.opis = request.form.get("opis")
        data_str = request.form.get("data")
        szkolenie.prowadzacy = request.form.get("prowadzacy")
        szkolenie.miejsce = request.form.get("miejsce")
        szkolenie.kandydat_id = request.form.get("kandydat_id")
        
        if data_str:
            try:
                szkolenie.data = datetime.strptime(data_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Nieprawidłowy format daty i godziny!", "danger")
                return redirect(url_for("szkolenia_bp.edytuj_szkolenie", id=id))
        
        try:
            db.session.commit()
            flash("Szkolenie zostało zaktualizowane!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Błąd podczas aktualizacji: {e}", "danger")
        return redirect(url_for("szkolenia_bp.lista_szkolen"))
    
    return render_template("szkolenia_edytuj.html", szkolenie=szkolenie, kandydaci=kandydaci)

@szkolenia_bp.route("/usun/<int:id>", methods=["POST"])
def usun_szkolenie(id: int) -> str:
    szkolenie = Szkolenie.query.get_or_404(id)
    try:
        db.session.delete(szkolenie)
        db.session.commit()
        flash("Szkolenie zostało usunięte!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Błąd podczas usuwania: {e}", "danger")
    return redirect(url_for("szkolenia_bp.lista_szkolen"))

@szkolenia_bp.route("/decyzja/<int:id>/<string:decyzja>", methods=["POST"]) 
def decyzja_szkolenie(id: int, decyzja: str) -> str:
    # Możliwe wartości: "zatrudnij" lub "historia"
    szkolenie = Szkolenie.query.get_or_404(id)
    if decyzja not in ["zatrudnij", "historia"]:
        flash("Nieprawidłowa decyzja!", "danger")
        return redirect(url_for("szkolenia_bp.lista_szkolen"))
    szkolenie.decyzja = decyzja
    try:
        db.session.commit()
        flash("Decyzja została zaktualizowana!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Błąd przy aktualizacji decyzji: {e}", "danger")
    return redirect(url_for("szkolenia_bp.lista_szkolen"))

@szkolenia_bp.route("/kalendarz", endpoint="kalendarz_szkolen")
def kalendarz_szkolen() -> str:
    szkolenia = Szkolenie.query.order_by(Szkolenie.data.asc()).all()
    return render_template("szkolenia_kalendarz.html", szkolenia=szkolenia)

@szkolenia_bp.route("/szczegoly/<int:id>")
def szczegoly_szkolenia(id: int) -> str:
    szkolenie = Szkolenie.query.get_or_404(id)
    return render_template("szkolenia_szczegoly.html", szkolenie=szkolenie)

@szkolenia_bp.route("/usun_uczestnika/<int:szkolenie_id>/<int:kandydat_id>", methods=["POST"])
def usun_uczestnika(szkolenie_id: int, kandydat_id: int) -> str:
    szkolenie = Szkolenie.query.get_or_404(szkolenie_id)
    kandydat = Kandydat.query.get_or_404(kandydat_id)
    if kandydat in szkolenie.kandydaci:
        szkolenie.kandydaci.remove(kandydat)
        # Aktualizujemy status kandydata, aby nie pojawiał się w terminarzu
        kandydat.status = "Do szkolenia"
        # Usuwamy rekord spotkania, jeśli taki istnieje
        spotkanie = Spotkanie.query.filter_by(kandydat_id=kandydat.id).first()
        if spotkanie:
            db.session.delete(spotkanie)
        try:
            db.session.commit()
            flash(f"Kandydat {kandydat.imie} {kandydat.nazwisko} został usunięty ze szkolenia.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Błąd podczas usuwania kandydata: {e}", "danger")
    return redirect(url_for("szkolenia_bp.szczegoly_szkolenia", id=szkolenie_id))

@szkolenia_bp.route("/decyzja_uczestnictwo/<int:szkolenie_id>/<int:kandydat_id>/<string:decyzja>", methods=["POST"])
def decyzja_uczestnictwo(szkolenie_id: int, kandydat_id: int, decyzja: str) -> str:
    # Sprawdzamy, czy decyzja jest jedną z dozwolonych opcji
    if decyzja not in ["zatrudnij", "historia"]:
        flash("Nieprawidłowa decyzja!", "danger")
        return redirect(url_for("szkolenia_bp.szczegoly_szkolenia", id=szkolenie_id))
    
    uczestnictwo = Uczestnictwo.query.filter_by(szkolenie_id=szkolenie_id, kandydat_id=kandydat_id).first_or_404()
    uczestnictwo.decyzja = decyzja
    try:
        db.session.commit()
        flash("Decyzja uczestnictwa została zaktualizowana.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Błąd podczas aktualizacji decyzji: {e}", "danger")
    return redirect(url_for("szkolenia_bp.szczegoly_szkolenia", id=szkolenie_id))


