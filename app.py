import os
import random
from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)
app.secret_key = "clave-super-secreta-del-casino"

DB_URL = "postgresql://torneo_dwdy_user:f3OpS5khsewskTq6FpdOA7cvG6tdWZp3@dpg-d8hmdbgjs32c73cr93eg-a.oregon-postgres.render.com/torneo_dwdy"

def get_db_connection():
    return psycopg2.connect(DB_URL)

# Función para calcular valor de la mano
def calcular_mano(mano):
    valor = sum(mano)
    # Ajustar ases si es necesario
    ases = mano.count(11)
    while valor > 21 and ases:
        valor -= 10
        ases -= 1
    return valor

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Guardar datos iniciales del jugador
        session["datos"] = {
            "doc": request.form["documento"],
            "nombre": request.form["nombre"],
            "programa": request.form["programa"],
            "ficha": request.form["ficha"]
        }
        # Iniciar juego
        deck = [2,3,4,5,6,7,8,9,10,10,10,10,11] * 4
        random.shuffle(deck)
        session["mano_jugador"] = [deck.pop(), deck.pop()]
        session["mano_dealer"] = [deck.pop(), deck.pop()]
        session["deck"] = deck
        return redirect(url_for("juego"))
    return render_template("index.html")

@app.route("/juego")
def juego():
    jugador = calcular_mano(session["mano_jugador"])
    return render_template("juego.html", jugador=jugador, mano=session["mano_jugador"])

@app.route("/hit")
def hit():
    session["mano_jugador"].append(session["deck"].pop())
    if calcular_mano(session["mano_jugador"]) > 21:
        return redirect(url_for("resultado", ganaste=False))
    return redirect(url_for("juego"))

@app.route("/stand")
def stand():
    # Lógica simple del dealer
    dealer = session["mano_jugador"] # Solo como placeholder
    # ... aquí iría la lógica del dealer ...
    return redirect(url_for("resultado", ganaste=True))

@app.route("/resultado/<ganaste>")
def resultado(ganaste):
    puntaje = 100 if ganaste == "True" else 0
    # GUARDAR EN POSTGRESQL (aquí aplicas tu INSERT INTO)
    return render_template("resultado.html", mensaje="¡Ganaste!" if ganaste=="True" else "Perdiste")

if __name__ == "__main__":
    app.run(debug=True)
