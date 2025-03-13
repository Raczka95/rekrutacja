from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from blueprints.extensions import db
from blueprints.models import Kandydat, Spotkanie, Historia

# Tworzymy Blueprint
kandydaci_bp = Blueprint('kandydaci_bp', __name__, template_folder='../templates')

STATUSY = ["Zadzwonić", "Umówiony", "Zrezygnował", "Nie zdecydowany"]

@kandydaci_bp.route('/dodaj_kandydata', methods=['GET', 'POST'])
def dodaj_kandydata():
    if request.method == 'POST':
        imie = request.form.get('imie', '').strip()
        nazwisko = request.form.get('nazwisko', '').strip()
        email = request.form.get('email', '').strip().lower()
        telefon = request.form.get('telefon', '').strip()
        status = request.form.get('status', 'Nie zdecydowany')
        data_kontaktu = request.form.get('data_kontaktu')

        print(f"📌 Debug: Otrzymane dane: {imie} {nazwisko}, email: {email}, tel: {telefon}, status: {status}")

        # ✅ Sprawdzamy, czy e-mail już istnieje
        istnieje_kandydat = Kandydat.query.filter_by(email=email).first()
        if istnieje_kandydat:
            # ❌ Usuwamy wszystkie wcześniejsze komunikaty, aby wyświetlić tylko ten jeden
            session.pop('_flashes', None)
            flash(f"❌ Błąd: Kandydat z e-mailem {email} już istnieje!", "danger")
            print(f"❌ Debug: E-mail {email} już istnieje w bazie!")
            return redirect(url_for('kandydaci_bp.dodaj_kandydata'))

        if data_kontaktu:
            try:
                data_kontaktu = datetime.strptime(data_kontaktu, "%Y-%m-%d").date()
            except ValueError:
                flash("Nieprawidłowy format daty!", "danger")
                return redirect(url_for('kandydaci_bp.dodaj_kandydata'))
        else:
            data_kontaktu = None

        nowy_kandydat = Kandydat(
            imie=imie, 
            nazwisko=nazwisko, 
            email=email, 
            telefon=telefon,
            status=status,
            data_kontaktu=data_kontaktu
        )

        try:
            db.session.add(nowy_kandydat)
            db.session.commit()
            # ❌ Usuwamy wszystkie wcześniejsze komunikaty przed dodaniem nowego
            session.pop('_flashes', None)
            flash(f"✅ Kandydat {imie} {nazwisko} został dodany!", "success")
            print(f"✅ Debug: Dodano kandydata {imie} {nazwisko} do bazy.")
        except Exception as e:
            db.session.rollback()
            flash(f"Błąd zapisu do bazy: {e}", "danger")
            print(f"❌ Debug: Błąd bazy danych: {e}")

        return redirect(url_for('kandydaci_bp.lista_kandydatow'))

    return render_template('kandydaci_dodaj.html', statusy=STATUSY)







@kandydaci_bp.route('/zmien_status/<int:kandydat_id>', methods=['POST'])
def zmien_status(kandydat_id):
    kandydat = Kandydat.query.get_or_404(kandydat_id)
    nowy_status = request.form.get('status')

    if not nowy_status:
        flash('Nie wybrano statusu!', 'danger')
        return redirect(url_for('kandydaci_bp.lista_kandydatow'))

    kandydat.status = nowy_status

    # ✅ Jeśli kandydat jest "Nie zdecydowany", ustawiamy datę następnego kontaktu
    if nowy_status == "Nie zdecydowany":
        kandydat.data_kontaktu = datetime.utcnow().date() + timedelta(days=14)

    # ✅ Jeśli kandydat jest "Umówiony", dodajemy go do terminarza spotkań
    elif nowy_status == "Umówiony":
        if not kandydat.telefon:
            flash("Brak numeru telefonu! Nie można dodać spotkania.", "danger")
            return redirect(url_for('kandydaci_bp.lista_kandydatow'))

        spotkanie = Spotkanie(
            kandydat_id=kandydat.id,
            telefon=kandydat.telefon,  # ✅ Pobieramy telefon kandydata
            data=None,
            opis=f"Spotkanie rekrutacyjne dla {kandydat.imie} {kandydat.nazwisko}"
        )
        db.session.add(spotkanie)
    
    try:
        db.session.commit()
        flash(f'Status kandydata został zaktualizowany na "{nowy_status}"!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Błąd podczas aktualizacji: {e}', 'danger')

    return redirect(url_for('kandydaci_bp.lista_kandydatow'))








@kandydaci_bp.route('/edytuj_kandydata/<int:kandydat_id>', methods=['GET', 'POST'])
def edytuj_kandydata(kandydat_id):
    kandydat = Kandydat.query.get_or_404(kandydat_id)
    if request.method == 'POST':
        kandydat.imie = request.form.get('imie')
        kandydat.nazwisko = request.form.get('nazwisko')
        kandydat.email = request.form.get('email')
        kandydat.telefon = request.form.get('telefon')
        kandydat.status = request.form.get('status')
        kandydat.data_kontaktu = request.form.get('data_kontaktu')
        
        if kandydat.data_kontaktu:
            kandydat.data_kontaktu = datetime.strptime(kandydat.data_kontaktu, "%Y-%m-%d").date()
        
        db.session.commit()
        flash("Dane kandydata zostały zaktualizowane!", "success")
        return redirect(url_for('kandydaci_bp.lista_kandydatow'))
    return render_template('kandydaci_edytuj.html', kandydat=kandydat, statusy=STATUSY)

@kandydaci_bp.route('/usun_kandydata/<int:kandydat_id>', methods=['POST'])
def usun_kandydata(kandydat_id):
    kandydat = Kandydat.query.get_or_404(kandydat_id)
    db.session.delete(kandydat)
    db.session.commit()
    flash("Kandydat został usunięty.", "success")
    return redirect(url_for('kandydaci_bp.lista_kandydatow'))


@kandydaci_bp.route('/lista_kandydatow')
def lista_kandydatow():
    # ✅ Pobieramy tylko kandydatów, którzy NIE są umówieni
    kandydaci = Kandydat.query.filter(Kandydat.status != "Umówiony").all()
    dzisiaj = datetime.utcnow().date()

    kandydaci_z_akcjami = []
    kandydaci_do_kontaktu = []

    for kandydat in kandydaci:
        akcja_data = None
        if kandydat.status == "Nie zdecydowany" and kandydat.data_kontaktu:
            akcja_data = kandydat.data_kontaktu + timedelta(days=14)
        if akcja_data == dzisiaj:
            kandydaci_do_kontaktu.append(kandydat)
        kandydaci_z_akcjami.append({
            "kandydat": kandydat,
            "akcja_data": akcja_data
        })

    return render_template(
        'kandydaci_lista.html',
        kandydaci_z_akcjami=kandydaci_z_akcjami,
        kandydaci_do_kontaktu=kandydaci_do_kontaktu
    )
@kandydaci_bp.route('/przenies_do_historia/<int:kandydat_id>', methods=['POST'])
def przenies_do_historia(kandydat_id):
    # Pobierz kandydata z bazy
    kandydat = Kandydat.query.get_or_404(kandydat_id)
    
    # Utwórz nowy wpis w tabeli Historia
    nowa_historia = Historia(
        kandydat_id=kandydat.id,
        data_zatrudnienia=datetime.utcnow().date(),  # Aktualna data
        stanowisko=request.form.get('stanowisko', 'Nie podano')  # Opcjonalne pole stanowiska
    )
    
    try:
        # Dodaj do bazy i usuń kandydata z listy
        db.session.add(nowa_historia)
        db.session.delete(kandydat)
        db.session.commit()
        flash(f"Kandydat {kandydat.imie} {kandydat.nazwisko} został przeniesiony do Historii.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Błąd podczas przenoszenia do Historii: {e}", "danger")
    
    return redirect(url_for('kandydaci_bp.lista_kandydatow'))


