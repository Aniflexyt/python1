import os
from flask import Flask, render_template, request, session, redirect, url_for
import random
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)
app.secret_key = "clave-super-secreta-del-ring"

# Tu base de datos de Render
DB_URL = "postgresql://torneo_dwdy_user:f3OpS5khsewskTq6FpdOA7cvG6tdWZp3@dpg-d8hmdbgjs32c73cr93eg-a.oregon-postgres.render.com/torneo_dwdy"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.route("/", methods=["GET"])
def inicio():
    # Solo muestra la pantalla de registro
    return render_template("index.html")

@app.route("/juego", methods=["GET", "POST"])
def juego():
    if request.method == "POST":
        # CASO 1: Viene del formulario de registro inicial
        if "documento" in request.form:
            session["documento"] = request.form.get("documento")
            session["nombre"] = request.form.get("nombre")
            session["correo"] = request.form.get("correo")
            session["programa"] = request.form.get("programa")
            session["ficha"] = request.form.get("ficha")
            
            # Iniciamos el juego de adivinar el número
            session["numero"] = random.randint(1, 100)
            session["veces"] = 0
            return render_template("juego.html", nombre=session["nombre"], mensaje="¡Que suene la campana! Adivina el número del 1 al 100.")

        # CASO 2: Está enviando un intento (golpe) en el juego
        elif "intento" in request.form:
            try:
                intento = int(request.form["intento"])
                numero = session.get("numero", 50)
                session["veces"] += 1

                if intento < numero:
                    return render_template("juego.html", nombre=session.get("nombre"), mensaje="¡Fallaste! El número es MAYOR. (Gancho abajo)")
                elif intento > numero:
                    return render_template("juego.html", nombre=session.get("nombre"), mensaje="¡Fallaste! El número es MENOR. (Jab arriba)")
                else:
                    # ¡GANÓ EL JUEGO! Calculamos el puntaje
                    puntaje = max(100 - (session["veces"] * 5), 10)
                    nombre_jugador = session.get("nombre")
                    
                    # Guardamos en PostgreSQL
                    try:
                        conn = get_db_connection()
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO jugadores (documento, nombre, correo, programa, ficha, puntaje) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (documento) 
                            DO UPDATE SET puntaje = GREATEST(jugadores.puntaje, EXCLUDED.puntaje);
                        """, (session.get("documento"), nombre_jugador, session.get("correo"), session.get("programa"), session.get("ficha"), puntaje))
                        conn.commit()
                        cur.close()
                        conn.close()
                    except OperationalError as e:
                        # Cumpliendo el punto 4 del taller: Captura de excepción
                        return render_template("error.html", mensaje_error="No se pudo conectar al servidor para guardar tu récord.", detalle=str(e))
                    
                    # Si todo sale bien, limpia la sesión y manda a la tabla de posiciones
                    session.clear()
                    return redirect(url_for("ranking", msj=f"¡Nocaut! {nombre_jugador} ganaste con {puntaje} puntos."))
            except ValueError:
                return render_template("juego.html", nombre=session.get("nombre"), mensaje="Por favor ingresa un número válido.")
    
    # Si alguien intenta entrar a /juego directamente desde la URL, lo devolvemos al inicio
    return redirect(url_for("inicio"))

@app.route("/ranking", methods=["GET"])
def ranking():
    mensaje = request.args.get("msj", "")
    jugadores = []
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT nombre, puntaje, programa, ficha FROM jugadores ORDER BY puntaje DESC;")
        jugadores = cur.fetchall()
        cur.close()
        conn.close()
    except OperationalError as e:
        return render_template("error.html", mensaje_error="Fallo al consultar la tabla de posiciones.", detalle=str(e))
    
    return render_template("ranking.html", jugadores=jugadores, mensaje=mensaje)

if __name__ == "__main__":
    app.run(debug=True)
