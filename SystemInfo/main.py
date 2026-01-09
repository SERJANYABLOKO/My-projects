#!/usr/bin/env python3
"""
Скрипт для отображения информации о системе
"""

import platform
import os
import sys
import socket
import psutil
import datetime
import cpuinfo
import json
from typing import Dict, Any


def get_system_info() -> Dict[str, Any]:
    """Сбор информации о системе"""
    info = {}

    # Основная информация о системе
    info['Система'] = {
        'Операционная система': platform.system(),
        'Версия ОС': platform.version(),
        'Архитектура': platform.architecture()[0],
        'Сеть': {
            'Имя хоста': socket.gethostname(),
            'IP адрес': socket.gethostbyname(socket.gethostname())
        }
    }

    # Информация о процессоре
    try:
        cpu_info = cpuinfo.get_cpu_info()
        info['Процессор'] = {
            'Модель': cpu_info.get('brand_raw', 'Неизвестно'),
            'Архитектура': cpu_info.get('arch', 'Неизвестно'),
            'Битность': f"{cpu_info.get('bits', 0)}-бит",
            'Количество ядер': psutil.cpu_count(logical=False),
            'Количество потоков': psutil.cpu_count(logical=True),
            'Частота': f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else 'Неизвестно'
        }
    except:
        info['Процессор'] = {'Модель': platform.processor()}

    # Информация о памяти
    mem = psutil.virtual_memory()
    info['Память'] = {
        'Всего': f"{mem.total / (1024 ** 3):.2f} GB",
        'Доступно': f"{mem.available / (1024 ** 3):.2f} GB",
        'Использовано': f"{mem.used / (1024 ** 3):.2f} GB",
        'Использование': f"{mem.percent}%"
    }

    # Информация о дисках
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                'Устройство': partition.device,
                'Точка монтирования': partition.mountpoint,
                'Файловая система': partition.fstype,
                'Всего': f"{usage.total / (1024 ** 3):.2f} GB",
                'Использовано': f"{usage.used / (1024 ** 3):.2f} GB",
                'Свободно': f"{usage.free / (1024 ** 3):.2f} GB",
                'Использование': f"{usage.percent}%"
            })
        except:
            continue

    info['Диски'] = disks

    # Информация о сети
    net_info = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                net_info.append({
                    'Интерфейс': iface,
                    'IP адрес': addr.address,
                    'Маска подсети': addr.netmask
                })

    info['Сетевые интерфейсы'] = net_info

    # Загрузка системы
    info['Загрузка'] = {
        'Время работы': str(datetime.timedelta(seconds=int(psutil.boot_time()))),
        'Загрузка CPU': f"{psutil.cpu_percent(interval=1)}%",
        'Процессы': len(psutil.pids())
    }

    # Информация о пользователе
    info['Пользователь'] = {
        'Имя пользователя': os.getlogin(),
        'Текущая директория': os.getcwd(),
        'Python версия': platform.python_version()
    }

    return info


def print_system_info(info: Dict[str, Any]):
    """Красивый вывод информации о системе"""
    print("=" * 60)
    print("ИНФОРМАЦИЯ О СИСТЕМЕ".center(60))
    print("=" * 60)
    print()

    for category, data in info.items():
        print(f"╔══ {category} {'═' * (50 - len(category))}")
        print()

        if isinstance(data, list):
            for item in data:
                for key, value in item.items():
                    print(f"  ▸ {key}: {value}")
                print()
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"  ▸ {key}:")
                    for subkey, subvalue in value.items():
                        print(f"      • {subkey}: {subvalue}")
                else:
                    print(f"  ▸ {key}: {value}")
            print()

        print(f"╚{'═' * 52}")
        print()


def save_to_file(info: Dict[str, Any], filename: str = "system_info.json"):
    """Сохранение информации в файл"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(f"\nИнформация сохранена в файл: {filename}")
    except Exception as e:
        print(f"\nОшибка при сохранении файла: {e}")


def main():
    """Основная функция"""
    try:
        print("Сбор информации о системе...")
        system_info = get_system_info()

        print_system_info(system_info)

        # Предложение сохранить в файл
        response = input("\nСохранить информацию в файл? (y/n): ").strip().lower()
        if response in ['y', 'д', 'yes', 'да']:
            filename = input("Имя файла (по умолчанию: system_info.json): ").strip()
            if not filename:
                filename = "system_info.json"
            save_to_file(system_info, filename)

    except KeyboardInterrupt:
        print("\n\nОперация прервана пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
        print("Убедитесь, что установлены необходимые библиотеки:")
        print("pip install psutil py-cpuinfo")
        sys.exit(1)


if __name__ == "__main__":
    main()