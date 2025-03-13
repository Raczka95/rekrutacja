from flask import Blueprint, render_template, request, redirect, url_for, flash
from blueprints.extensions import db
from blueprints.models import Historia, Kandydat
from datetime import datetime

historia_bp = Blueprint("historia_bp", __name__, template_folder="../templates/historia")

@historia_bp.route("/")
def lista_historia():
    historia = Historia.query.all()
    return render_template("historia.html", historia=historia)

@historia_bp.route('/dodaj', methods=['GET', 'POST'])
def dodaj_historia():
    if request.method == 'POST':
        kandydat_id = request.form['kandydat_id']
        data_zatrudnienia = request.form['data_zatrudnienia']
        stanowisko = request.form['stanowisko']

        if not kandydat_id or not data_zatrudnienia or not stanowisko:
            flash('Wszystkie pola są wymagane!', 'danger')
            return redirect(url_for('historia_bp.dodaj_historia'))

        nowa_historia = Historia(
            kandydat_id=kandydat_id,
            data_zatrudnienia=datetime.strptime(data_zatrudnienia, '%Y-%m-%d'),
            stanowisko=stanowisko
        )
        
        db.session.add(nowa_historia)
        db.session.commit()
        flash('Historia zatrudnienia została dodana!', 'success')

        return redirect(url_for('historia_bp.lista_historia'))

    kandydaci = Kandydat.query.all()
    return render_template('historia/dodaj.html', kandydaci=kandydaci)

