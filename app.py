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

def calcular_mano(mano):
    valor = sum(mano)
    ases = mano.count(11)
    while valor > 21 and ases:
        valor -= 10
        ases -= 1
    return valor

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session["datos"] = {
            "doc": request.form["documento"],
            "nombre": request.form["nombre"],
            "programa": request.form["programa"],
            "ficha": request.form["ficha"]
        }
        deck = [2,3,4,5,6,7,8,9,10,10,10,10,11] * 4
        random.shuffle(deck)
        session["mano_jugador"] = [deck.pop(), deck.pop()]
        session["deck"] = deck
        return redirect(url_for("juego"))
    return render_template("index.html")

@app.route("/juego")
def juego():
    valor = calcular_mano(session["mano_jugador"])
    return render_template("juego.html", jugador=valor, mano=session["mano_jugador"])

@app.route("/hit")
def hit():
    session["mano_jugador"].append(session["deck"].pop())
    if calcular_mano(session["mano_jugador"]) > 21:
        return redirect(url_for("resultado", ganaste="False"))
    return redirect(url_for("juego"))

@app.route("/stand")
def stand():
    return redirect(url_for("resultado", ganaste="True"))

@app.route("/resultado/<ganaste>")
def resultado(ganaste):
    puntaje = 100 if ganaste == "True" else 0
    datos = session.get("datos")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # INSERT en PostgreSQL
        cur.execute("""
            INSERT INTO jugadores (documento, nombre, programa, ficha, puntaje) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (documento) DO UPDATE SET puntaje = GREATEST(jugadores.puntaje, EXCLUDED.puntaje);
        """, (datos['doc'], datos['nombre'], datos['programa'], datos['ficha'], puntaje))
        conn.commit()
        cur.close()
        conn.close()
    except OperationalError as e:
        # Control de excepciones requerido por el taller
        return render_template("error.html", mensaje_error="Error al guardar tu puntaje.", detalle=str(e))
    
    return render_template("resultado.html", mensaje="¡Ganaste!" if ganaste=="True" else "Perdiste")

@app.route("/ranking")
def ranking():
    # RUTA NUEVA: Consulta los puntajes
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nombre, puntaje, programa, ficha FROM jugadores ORDER BY puntaje DESC;")
        lista_jugadores = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("ranking.html", jugadores=lista_jugadores)
    except OperationalError as e:
        return render_template("error.html", mensaje_error="Error al consultar el ranking.", detalle=str(e))

if __name__ == "__main__":
    app.run(debug=True)
