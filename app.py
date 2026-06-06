import os
from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)
app.secret_key = "clave-super-secreta-del-ring"

# Tu URL de Render
DB_URL = "postgresql://torneo_dwdy_user:f3OpS5khsewskTq6FpdOA7cvG6tdWZp3@dpg-d8hmdbgjs32c73cr93eg-a.oregon-postgres.render.com/torneo_dwdy"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.route("/", methods=["GET"])
def inicio():
    return render_template("index.html")

@app.route("/juego", methods=["POST"])
def juego():
    # Recibimos los datos del formulario inicial y los guardamos en la sesión
    session["documento"] = request.form.get("documento")
    session["nombre"] = request.form.get("nombre")
    session["correo"] = request.form.get("correo")
    session["programa"] = request.form.get("programa")
    session["ficha"] = request.form.get("ficha")
    return render_template("juego.html", nombre=session["nombre"])

@app.route("/guardar", methods=["POST"])
def guardar():
    # Recibimos el puntaje final del juego de pelea
    puntaje = int(request.form.get("puntaje_final", 0))
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO jugadores (documento, nombre, correo, programa, ficha, puntaje) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (documento) 
            DO UPDATE SET puntaje = GREATEST(jugadores.puntaje, EXCLUDED.puntaje);
        """, (session.get("documento"), session.get("nombre"), session.get("correo"), 
              session.get("programa"), session.get("ficha"), puntaje))
        conn.commit()
        cur.close()
        conn.close()
        session.clear()
        return redirect(url_for("ranking"))
    except Exception as e:
        return render_template("error.html", mensaje_error="Error al guardar el récord.", detalle=str(e))

@app.route("/ranking", methods=["GET"])
def ranking():
    # Tu consulta original a la base de datos
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT nombre, puntaje, programa, ficha FROM jugadores ORDER BY puntaje DESC;")
    jugadores = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("ranking.html", jugadores=jugadores)

if __name__ == "__main__":
    app.run(debug=True)
