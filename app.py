# Основные импорты
from flask import Flask, render_template, request
from flask_wtf import FlaskForm  # Для работы с формами
from wtforms import FileField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, InputRequired
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
import numpy as np
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Обязательно для Flask-WTF

# Папки для хранения файлов
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Форма с капчей
class ImageForm(FlaskForm):
    image = FileField('Изображение', validators=[DataRequired()])
    border_size = IntegerField('Размер рамки', validators=[InputRequired()])
    i_am_human = BooleanField('Я не робот', validators=[DataRequired(message='Подтвердите, что вы не робот')])
    submit = SubmitField('Обработать')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ImageForm()

    if form.validate_on_submit() and form.i_am_human.data:
        # Получаем данные из формы
        image_file = form.image.data
        border_size = form.border_size.data

        # Сохраняем исходное изображение
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)

        # Обрабатываем изображение
        result_image_path, histogram_path = process_image(image_path, border_size)

        return render_template('index.html', 
                               result_image=result_image_path,
                               histogram=histogram_path,
                               form=form)

    return render_template('index.html', form=form)

def process_image(image_path, border_size):
    # Открываем изображение
    image = Image.open(image_path)
    
    # Добавляем рамку
    width, height = image.size
    border_width = int(width * border_size / 100)
    result_image = ImageOps.expand(image, border=border_width, fill='black')
    
    # Сохраняем обработанное изображение
    result_image_path = os.path.join(RESULT_FOLDER, 'result.jpg')
    result_image.save(result_image_path)

    # Строим график распределения цветов для исходного изображения
    histogram_path = os.path.join(RESULT_FOLDER, 'histogram.png')
    plot_color_distribution(image, histogram_path)

    return '/' + result_image_path, '/' + histogram_path

def plot_color_distribution(image, save_path):
    # Преобразуем изображение в массив NumPy
    data = np.array(image)
    # Разделяем каналы RGB
    r = data[:, :, 0].flatten()
    g = data[:, :, 1].flatten()
    b = data[:, :, 2].flatten()

    # Строим гистограммы
    plt.figure(figsize=(10, 5))
    plt.hist(r, bins=256, alpha=0.5, color='red', label='Red')
    plt.hist(g, bins=256, alpha=0.5, color='green', label='Green')
    plt.hist(b, bins=256, alpha=0.5, color='blue', label='Blue')
    plt.title('Распределение цветов (RGB)')
    plt.xlabel('Интенсивность')
    plt.ylabel('Количество пикселей')
    plt.legend()
    plt.savefig(save_path)
    plt.close()

if __name__ == '__main__':
    app.run(debug=True)