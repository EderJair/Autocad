from flask import Flask, request, render_template, send_from_directory
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    # Guardar el archivo subido
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Definir la ruta de salida
    output_filename = f"edited_{file.filename}"
    output_path = os.path.join(PROCESSED_FOLDER, output_filename)

    # Ejecutar el script externo
    try:
        subprocess.run(
            ["python", "script_ezdxf.py", input_path, output_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        return f"Error procesando el archivo: {e}", 500

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Archivo Procesado</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f4f4f9;
            }}
            .container {{
                text-align: center;
                background: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            h3 {{
                color: #4CAF50;
                margin-bottom: 20px;
            }}
            a {{
                text-decoration: none;
                color: white;
                background-color: #007BFF;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }}
            a:hover {{
                background-color: #0056b3;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h3>¡El archivo fue procesado correctamente!</h3>
            <p>Haz clic en el botón de abajo para descargar tu archivo editado:</p>
            <a href="/download/{output_filename}">Descargar archivo editado</a>
        </div>
    </body>
    </html>
    """

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('processed_files', filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
