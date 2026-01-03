import turtle
from PIL import Image
import numpy as np
import colorsys
import os


class ImageDrawer:
    def __init__(self, image_path="img.png", scale=1.0, speed=0, dot_size=1):
        """
        Инициализация рисовальщика изображений

        Args:
            image_path: путь к изображению (по умолчанию "img.png")
            scale: масштаб (0.0 - 1.0)
            speed: скорость рисования (0 - максимальная)
            dot_size: размер точки для точечного рисунка
        """
        self.image_path = image_path
        self.scale = max(0.1, min(1.0, scale))
        self.speed = speed
        self.dot_size = max(1, dot_size)

        # Проверяем существование файла
        self.check_and_find_image()

        # Загружаем изображение
        self.load_image()

        # Настраиваем Turtle
        self.setup_turtle()

    def check_and_find_image(self):
        """Проверяем существование файла и ищем альтернативы"""
        # Если файл существует, используем его
        if os.path.exists(self.image_path):
            print(f"Найден файл: {self.image_path}")
            return

        # Ищем файлы с похожими именами
        possible_files = ["img.png", "image.png", "picture.png", "test.png", "demo.png"]

        for filename in possible_files:
            if os.path.exists(filename):
                self.image_path = filename
                print(f"Найден файл: {filename}")
                return

        # Если файл не найден, создаем тестовое изображение
        print("Файл img.png не найден. Создаем тестовое изображение...")
        self.create_test_image("img.png")

    def create_test_image(self, filename):
        """Создание тестового изображения если файл не найден"""
        from PIL import Image, ImageDraw

        # Создаем красивое тестовое изображение
        img = Image.new('RGB', (300, 300), color='white')
        draw = ImageDraw.Draw(img)

        # Рисуем градиентный фон
        for y in range(300):
            color = int(y / 300 * 255)
            draw.line([(0, y), (300, y)], fill=(color, 255 - color, 128))

        # Рисуем фигуры
        draw.rectangle([50, 50, 250, 250], fill=None, outline='red', width=3)
        draw.ellipse([70, 70, 230, 230], fill='blue')
        draw.polygon([150, 90, 210, 210, 90, 210], fill='green')

        # Рисуем текст
        draw.text((100, 140), "TURTLE", fill='yellow', stroke_width=2, stroke_fill='black')

        img.save(filename)
        self.image_path = filename
        print(f"Создано тестовое изображение: {filename}")

    def load_image(self):
        """Загрузка и обработка изображения"""
        try:
            img = Image.open(self.image_path)
            # Конвертируем в RGB если нужно
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Уменьшаем размер для ускорения рисования
            new_width = int(img.width * self.scale)
            new_height = int(img.height * self.scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Конвертируем в numpy массив
            self.image_array = np.array(img)
            self.height, self.width, _ = self.image_array.shape

            print(f"Изображение загружено: {self.width}x{self.height} пикселей")

        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            raise

    def setup_turtle(self):
        """Настройка графического окна и черепашки"""
        self.screen = turtle.Screen()
        self.screen.title(f"Image to Turtle Drawing - {os.path.basename(self.image_path)}")
        self.screen.colormode(255)

        self.t = turtle.Turtle()
        self.t.speed(self.speed)
        self.t.hideturtle()

        # Рассчитываем размеры экрана
        screen_width = min(1920, self.width * 2 + 100)
        screen_height = min(1080, self.height * 2 + 100)
        self.screen.setup(screen_width, screen_height)

        # Показываем информацию об изображении
        self.show_info()

    def show_info(self):
        """Показываем информацию об изображении"""
        info_turtle = turtle.Turtle()
        info_turtle.hideturtle()
        info_turtle.penup()
        info_turtle.goto(0, -self.height // 2 - 80)
        info_turtle.write(
            f"Изображение: {self.width}x{self.height} | Файл: {os.path.basename(self.image_path)}",
            align="center",
            font=("Arial", 10, "normal")
        )

    def draw_pixel_by_pixel(self):
        """Рисование изображения по пикселям (точечный рисунок)"""
        # Начинаем с верхнего левого угла
        start_x = -self.width // 2
        start_y = self.height // 2

        # Создаем отдельную черепашку для отображения прогресса
        progress_turtle = turtle.Turtle()
        progress_turtle.hideturtle()
        progress_turtle.penup()
        progress_turtle.goto(0, -self.height // 2 - 60)

        for y in range(self.height):
            for x in range(self.width):
                # Получаем цвет пикселя
                r, g, b = self.image_array[y, x][:3]

                # Поднимаем черепашку
                self.t.penup()

                # Перемещаемся к позиции пикселя
                pos_x = start_x + x
                pos_y = start_y - y
                self.t.goto(pos_x, pos_y)

                # Устанавливаем цвет и рисуем точку
                self.t.pendown()
                self.t.pencolor(r, g, b)
                self.t.dot(self.dot_size)

            # Обновляем прогресс каждые 10 строк
            if y % 10 == 0:
                progress = (y / self.height) * 100
                progress_turtle.clear()
                progress_turtle.write(f"Прогресс: {progress:.1f}%", align="center", font=("Arial", 12, "bold"))

        progress_turtle.clear()
        progress_turtle.write("Рисование завершено!", align="center", font=("Arial", 12, "bold"))
        print("Рисование завершено!")

    def draw_with_lines(self, step=2):
        """
        Рисование изображения линиями (более быстро)

        Args:
            step: шаг между точками (больше = быстрее, но менее детально)
        """
        step = max(1, step)

        # Начинаем с верхнего левого угла
        start_x = -self.width // 2
        start_y = self.height // 2

        # Создаем отдельную черепашку для отображения прогресса
        progress_turtle = turtle.Turtle()
        progress_turtle.hideturtle()
        progress_turtle.penup()
        progress_turtle.goto(0, -self.height // 2 - 60)

        for y in range(0, self.height, step):
            self.t.penup()
            prev_color = None

            for x in range(self.width):
                # Получаем цвет пикселя
                r, g, b = self.image_array[y, x][:3]
                current_color = (r, g, b)

                # Если цвет изменился или это первый пиксель в строке
                if current_color != prev_color or x == 0:
                    # Поднимаем перо и перемещаемся
                    self.t.penup()
                    pos_x = start_x + x
                    pos_y = start_y - y
                    self.t.goto(pos_x, pos_y)

                    # Устанавливаем цвет и опускаем перо
                    self.t.pencolor(r, g, b)
                    self.t.pendown()

                    prev_color = current_color

                # Рисуем линию к следующей точке
                if x < self.width - 1:
                    next_x = start_x + x + 1
                    self.t.goto(next_x, pos_y)

            # Обновляем прогресс
            if y % 20 == 0:
                progress = (y / self.height) * 100
                progress_turtle.clear()
                progress_turtle.write(f"Прогресс: {progress:.1f}%", align="center", font=("Arial", 12, "bold"))

        progress_turtle.clear()
        progress_turtle.write("Рисование завершено!", align="center", font=("Arial", 12, "bold"))
        print("Рисование завершено!")

    def draw_ascii_art(self, chars=" .:-=+*#%@", char_size=10):
        """
        Рисование ASCII арт версии изображения

        Args:
            chars: символы для градаций серого
            char_size: размер символа
        """
        # Конвертируем в оттенки серого
        gray_image = Image.open(self.image_path).convert('L')
        gray_image = gray_image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        gray_array = np.array(gray_image)

        # Начинаем с верхнего левого угла
        start_x = -self.width * char_size // 4
        start_y = self.height * char_size // 4

        # Создаем отдельную черепашку для отображения прогресса
        progress_turtle = turtle.Turtle()
        progress_turtle.hideturtle()
        progress_turtle.penup()
        progress_turtle.goto(0, -self.height // 2 - 60)

        self.t.penup()

        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                # Получаем яркость
                brightness = gray_array[y, x]

                # Выбираем символ на основе яркости
                char_index = int(brightness / 255 * (len(chars) - 1))
                char = chars[char_index]

                # Перемещаемся и рисуем символ
                pos_x = start_x + x * char_size // 2
                pos_y = start_y - y * char_size // 2
                self.t.goto(pos_x, pos_y)

                # Устанавливаем цвет на основе оригинального изображения
                if len(self.image_array[y, x]) >= 3:
                    r, g, b = self.image_array[y, x][:3]
                    self.t.pencolor(r, g, b)

                self.t.write(char, align="center", font=("Courier", char_size))

            # Обновляем прогресс
            if y % 20 == 0:
                progress = (y / self.height) * 100
                progress_turtle.clear()
                progress_turtle.write(f"Прогресс: {progress:.1f}%", align="center", font=("Arial", 12, "bold"))

        progress_turtle.clear()
        progress_turtle.write("ASCII арт создан!", align="center", font=("Arial", 12, "bold"))
        print("ASCII арт создан!")

    def run(self, mode='pixel'):
        """
        Запуск рисования

        Args:
            mode: метод рисования ('pixel', 'line', 'ascii')
        """
        print(f"Начинаем рисование в режиме: {mode}")
        print(f"Используется файл: {self.image_path}")

        if mode == 'pixel':
            self.draw_pixel_by_pixel()
        elif mode == 'line':
            self.draw_with_lines(step=2)
        elif mode == 'ascii':
            self.draw_ascii_art()
        else:
            print(f"Неизвестный режим: {mode}. Используется режим 'pixel'.")
            self.draw_pixel_by_pixel()

        # Завершение
        self.show_completion_message()

        turtle.done()

    def show_completion_message(self):
        """Показываем сообщение о завершении"""
        completion_turtle = turtle.Turtle()
        completion_turtle.hideturtle()
        completion_turtle.penup()
        completion_turtle.goto(0, -self.height // 2 - 40)
        completion_turtle.write(
            "Рисование завершено! Закройте окно.",
            align="center",
            font=("Arial", 14, "bold")
        )


def main():
    """Главная функция с меню выбора"""
    print("=" * 50)
    print("ПРОГРАММА ПЕРЕРИСОВКИ ИЗОБРАЖЕНИЙ НА TURTLE")
    print("=" * 50)

    # Проверяем, существует ли файл img.png
    default_image = "img.png"

    if not os.path.exists(default_image):
        print(f"Файл {default_image} не найден.")
        choice = input("Создать тестовое изображение? (y/n): ").lower()
        if choice == 'y':
            print("Создаем тестовое изображение...")
            drawer = ImageDrawer()
        else:
            alt_path = input("Введите путь к другому изображению: ").strip()
            default_image = alt_path if alt_path else "img.png"

    # Настройки
    try:
        print("\nНастройки рисования:")
        scale = float(input("Масштаб (0.1 - 1.0) [по умолчанию: 0.3]: ") or "0.3")
        dot_size = int(input("Размер точки [по умолчанию: 2]: ") or "2")
        speed = int(input("Скорость (0-10) [по умолчанию: 0]: ") or "0")

        print("\nВыберите режим рисования:")
        print("1. Точечный рисунок (пиксель за пикселем) - наиболее детальный")
        print("2. Линиями (быстрее) - хороший баланс")
        print("3. ASCII арт - стильный вариант")

        mode_choice = input("Ваш выбор (1-3) [по умолчанию: 1]: ") or "1"

        modes = {'1': 'pixel', '2': 'line', '3': 'ascii'}
        mode = modes.get(mode_choice, 'pixel')

        # Создаем и запускаем рисовальщик
        drawer = ImageDrawer(
            image_path=default_image,
            scale=scale,
            speed=speed,
            dot_size=dot_size
        )

        drawer.run(mode=mode)

    except ValueError as e:
        print(f"Ошибка ввода: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def quick_start():
    """Быстрый запуск с параметрами по умолчанию"""
    print("=" * 50)
    print("БЫСТРЫЙ СТАРТ - ИСПОЛЬЗУЮТСЯ ПАРАМЕТРЫ ПО УМОЛЧАНИЮ")
    print("=" * 50)

    try:
        # Используем параметры по умолчанию
        drawer = ImageDrawer(
            image_path="img.png",
            scale=0.3,
            speed=0,
            dot_size=2
        )

        # Используем режим линиями (наиболее сбалансированный)
        drawer.run(mode='line')

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    # Проверяем зависимости
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        print("=" * 50)
        print("УСТАНОВКА НЕОБХОДИМЫХ БИБЛИОТЕК")
        print("=" * 50)
        print("Запустите следующую команду в терминале:")
        print("pip install pillow numpy")
        print("=" * 50)
        exit(1)

    # Проверяем аргументы командной строки
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            quick_start()
        elif sys.argv[1] == "--help":
            print("Использование:")
            print("  python image_to_turtle.py          - интерактивный режим")
            print("  python image_to_turtle.py --quick  - быстрый старт с параметрами по умолчанию")
            print("  python image_to_turtle.py --help   - справка")
            print("\nПрограмма автоматически ищет файл img.png в текущей директории.")
            print("Если файл не найден, будет создано тестовое изображение.")
        else:
            main()
    else:
        main()