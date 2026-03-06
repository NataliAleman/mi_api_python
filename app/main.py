from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# CONEXION A MYSQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="rfid"
)

# -----------------------------
# RECIBIR UID DEL ESP32
# -----------------------------
@app.route("/api/rfid", methods=["POST"])
def recibir_rfid():

    data = request.get_json()
    # imprimir datos para depuración en consola
    app.logger.debug(f"Datos recibidos: {data}")

    if not data or "uid" not in data:
        return jsonify({"error": "UID no recibido"}), 400

    uid = data["uid"]

    cursor = db.cursor()

    sql = "INSERT INTO registros (uid) VALUES (%s)"
    val = (uid,)

    cursor.execute(sql, val)
    db.commit()

    cursor.close()

    return jsonify({
        "status": "ok",
        "uid": uid
    })


# -----------------------------
# VER REGISTROS
# -----------------------------
@app.route("/api/registros", methods=["GET"])
def ver_registros():

    cursor = db.cursor()

    cursor.execute("SELECT id, uid, fecha FROM registros ORDER BY id DESC")

    datos = cursor.fetchall()

    lista = []

    for row in datos:
        lista.append({
            "id": row[0],
            "uid": row[1],
            "fecha": str(row[2])
        })

    cursor.close()

    return jsonify(lista)


# -----------------------------
# INICIAR SERVIDOR
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)