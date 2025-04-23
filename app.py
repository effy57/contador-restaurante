import os
import time
import csv
from flask import Flask, request

app = Flask(__name__)

# Variables globales
conteo_por_minuto = []
start_time = time.time()

@app.route('/webhook', methods=['POST'])
def webhook():
    global start_time
    message = request.form.get('Body', '').strip().lower()
    
    try:
        if message == "finalizar":
            return finalizar()
        
        num_personas = int(message)
        current_time = time.time()
        elapsed_time = current_time - start_time
        minuto_actual = int(elapsed_time // 60)

        while len(conteo_por_minuto) <= minuto_actual:
            conteo_por_minuto.append(0)
        
        conteo_por_minuto[minuto_actual] += num_personas

        return f"✅ Registrado: {num_personas} persona(s) en el minuto {minuto_actual + 1}", 200
    except ValueError:
        return "Por favor envía un número entero o la palabra 'finalizar'.", 200

def finalizar():
    ruta_csv = "/tmp/consolidado.csv"
    with open(ruta_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Minuto', 'Personas'])
        for i, count in enumerate(conteo_por_minuto):
            writer.writerow([i + 1, count])
    
    respuesta = "\n".join([f"Min {i+1}: {c}" for i, c in enumerate(conteo_por_minuto)])
    return f"Consolidado por minuto:\n{respuesta}", 200


if __name__ == '_main_':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
