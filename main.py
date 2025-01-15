from flask import Flask, request, render_template_string
import cv2
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def resize_maze(image, target_size=64):
    resized_image = cv2.resize(image, (target_size, target_size), interpolation=cv2.INTER_NEAREST)
    return resized_image


def add_start_and_end(maze):
    rows = len(maze)
    cols = len(maze[0])

    for i in range(cols):
        if maze[1][i] == '.':
            maze[0] = maze[0][:i] + 'S' + maze[0][i + 1:]
            break

    for i in range(cols):
        if maze[rows - 2][i] == '.':
            maze[-1] = maze[-1][:i] + 'W' + maze[-1][i + 1:]
            break

    return maze


def trim_outer_walls(maze):
    maze = [row.strip('#') for row in maze if '#' in row]

    if maze:
        maze[0] = maze[0].replace('.', 'S', 1)
        maze[-1] = maze[-1].replace('.', 'W', 1)

    return maze


def process_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    resized_img = resize_maze(img, target_size=64)
    _, binary_img = cv2.threshold(resized_img, 127, 255, cv2.THRESH_BINARY)

    rows, cols = binary_img.shape
    labirynth = []
    for i in range(rows):
        row = []
        for j in range(cols):
            if binary_img[i, j] == 0:
                row.append('#')
            else:
                row.append('.')
        labirynth.append(row)

    labirynth = [['#'] * (cols + 2)] + [['#'] + row + ['#'] for row in labirynth] + [['#'] * (cols + 2)]
    trimmed_labirynth = trim_outer_walls(["".join(row) for row in labirynth])
    return "\n".join(trimmed_labirynth)


@app.route('/')
def home():
    return "Witaj w aplikacji Labirynt! Skorzystaj z endpointu /upload-form, aby przesłać obraz labiryntu."


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/upload-form', methods=['GET', 'POST'])
def upload_form():
    if request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            return render_template_string('''
                <!doctype html>
                <title>Błąd przesyłania</title>
                <h1>Nie wybrano pliku. Spróbuj ponownie.</h1>
                <a href="/upload-form">Powrót</a>
            ''')

        file = request.files['file']
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            labirynth_text = process_image(filepath)
            os.remove(filepath)
            return render_template_string('''
                <!doctype html>
                <title>Labirynt</title>
                <h1>Przetworzony Labirynt:</h1>
                <pre>{{ labirynth }}</pre>
                <a href="/upload-form">Prześlij inny obraz</a>
            ''', labirynth=labirynth_text)
        except Exception as e:
            os.remove(filepath)
            return render_template_string('''
                <!doctype html>
                <title>Błąd</title>
                <h1>Wystąpił błąd podczas przetwarzania obrazu:</h1>
                <p>{{ error }}</p>
                <a href="/upload-form">Powrót</a>
            ''', error=str(e))

    return '''
        <!doctype html>
        <title>Upload Labirynth</title>
        <h1>Prześlij obraz labiryntu</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Prześlij">
        </form>
    '''


if __name__ == '__main__':
    app.run(debug=True)
