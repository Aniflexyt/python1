import os
from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)
app.secret_key = "clave-super-secreta-del-ring"

# Tu URL exacta de Render (¡Intacta!)
DB_URL = "postgresql://torneo_dwdy_user:f3OpS5khsewskTq6FpdOA7cvG6tdWZp3@dpg-d8hmdbgjs32c73cr93eg-a.oregon-postgres.render.com/torneo_dwdy"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.route("/", methods=["GET"])
def inicio():
    # Solo muestra la pantalla de registro (con tu video de fondo y canción)
    return render_template("index.html")

@app.route("/juego", methods=["GET", "POST"])
def juego():
    if request.method == "POST":
        # --- MEJORA 1: El usuario envió el formulario inicial ---
        if "documento" in request.form:
            # Guardamos los datos en la sesión temporalmente
            session["documento"] = request.form.get("documento")
            session["nombre"] = request.form.get("nombre")
            session["correo"] = request.form.get("correo")
            session["programa"] = request.form.get("programa")
            session["ficha"] = request.form.get("ficha")
            
            # Lo mandamos directamente al Ring de boxeo
            return render_template("juego.html", nombre=session["nombre"])

        # --- MEJORA 2: El juego de boxeo terminó y nos envía el puntaje final ---
        elif "puntaje_final" in request.form:
            try:
                puntaje = int(request.form.get("puntaje_final", 0))
                nombre_jugador = session.get("nombre", "Luchador")
                
                # Guardamos en la base de datos de PostgreSQL (Tu lógica original)
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
                
                # Limpiamos los datos temporales
                session.clear()
                
                # Redirigimos al salón de la fama
                return redirect(url_for("ranking", msj=f"¡Combate finalizado! {nombre_jugador} obtuvo {puntaje} puntos."))
                
            except OperationalError as e:
                # Tu control de excepciones original
                return render_template("error.html", mensaje_error="No se pudo conectar a la base de datos para guardar tu récord.", detalle=str(e))
            except Exception as e:
                return render_template("error.html", mensaje_error="Error inesperado guardando el récord.", detalle=str(e))
    
    # Si alguien intenta entrar a /juego desde la barra de direcciones, lo devolvemos al inicio
    return redirect(url_for("inicio"))

@app.route("/ranking", methods=["GET"])
def ranking():
    mensaje = request.args.get("msj", "")
    jugadores = []
    
    # Tu consulta original a la base de datos para listar jugadores
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
