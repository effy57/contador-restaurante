from flask import Flask, request
from datetime import datetime
from collections import defaultdict
import csv
import os

app = Flask(__name__)

# Almacenamiento en memoria por número de usuario
usuarios = defaultdict(lambda: defaultdict(int))
ultimos_minutos = {}

@app.route("/webhook", methods=['POST'])
def webhook():
    from_number = request.form.get('From', '').replace("whatsapp:", "")
    body = request.form.get('Body', '').strip().upper()
    now = datetime.now()
    minuto_actual = now.strftime('%Y-%m-%d %H:%M')

    if body == 'FINALIZAR':
        return generar_consolidado(from_number)

    try:
        cantidad = int(body)
        minuto_anterior = ultimos_minutos.get(from_number)

        # Actualiza el registro
        usuarios[from_number][minuto_actual] += cantidad
        ultimos_minutos[from_number] = minuto_actual

        respuesta = f"✅ Registrado: {cantidad} personas\n"

        if minuto_anterior and minuto_anterior != minuto_actual:
            total_anterior = usuarios[from_number][minuto_anterior]
            respuesta = f"🕒 Total en {minuto_anterior}: {total_anterior} personas\n" + respuesta

        return responder(respuesta)

    except ValueError:
        return responder("Por favor, envía solo un número entero o FINALIZAR.")


def generar_consolidado(numero):
    registros = usuarios[numero]
    if not registros:
        return responder("No hay datos registrados.")

    nombre_archivo = f"consolidado_{numero.replace('+', '')}.csv"
    ruta = os.path.join("/tmp", nombre_archivo)

    with open(ruta, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Minuto', 'Cantidad'])
        for minuto, cantidad in sorted(registros.items()):
            writer.writerow([minuto, cantidad])

    mensaje = "Consolidado generado en CSV.\n"
    for minuto, cantidad in sorted(registros.items()):
        mensaje += f"{minuto} — {cantidad} personas\n"

    mensaje += "\n(Nota: el archivo CSV está guardado en el servidor /tmp. Render elimina esto al reiniciar. Para descarga automática se requiere integración adicional.)"

    return responder(mensaje)

def responder(mensaje):
    return f"<?xml version='1.0' encoding='UTF-8'?><Response><Message>{mensaje}</Message></Response>", 200, {'Content-Type': 'application/xml'}

if _name_ == '_main_':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
