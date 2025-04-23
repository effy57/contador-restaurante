import os
from flask import Flask, request
import csv
import time

app = Flask(__name__)

# Lista para almacenar el conteo de ingresos por minuto
conteo_por_minuto = []
start_time = time.time()

@app.route('/webhook', methods=['POST'])
def webhook():
    global start_time
    # Extrae el mensaje que llega de WhatsApp
    message = request.form['Body']
    
    try:
        # Si el mensaje es un número, se registra el conteo
        num_personas = int(message)
        current_time = time.time()
        elapsed_time = current_time - start_time
        elapsed_minutes = int(elapsed_time // 60)
        
        # Agregar el número de personas al conteo correspondiente al minuto
        if len(conteo_por_minuto) <= elapsed_minutes:
            conteo_por_minuto.append(num_personas)
        else:
            conteo_por_minuto[elapsed_minutes] += num_personas
        
        # Responder a WhatsApp
        return f"Registrado: {num_personas} personas en el minuto {elapsed_minutes + 1}", 200
    except ValueError:
        # Si no es un número, responder con un mensaje de error
        return "Por favor, envíe un número para registrar el ingreso de personas.", 400

@app.route('/finalizar', methods=['POST'])
def finalizar():
    # Generar el CSV con los resultados
    with open('/tmp/consolidado.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Minuto', 'Personas'])
        for i, count in enumerate(conteo_por_minuto):
            writer.writerow([i + 1, count])

    # Enviar el archivo CSV como respuesta
    return "El consolidado ha sido generado.", 200

if __name__ == '_main_':
    # Asignar el puerto para Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
