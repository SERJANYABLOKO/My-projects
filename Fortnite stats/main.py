import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем API ключ из .env файла
load_dotenv()


class FortniteStats:
    def __init__(self, api_key=None):
        """
        Инициализация с API ключом
        Можно получить бесплатный ключ на:
        - https://fortniteapi.io (1000 запросов в день бесплатно)
        - https://dash.fortnite-api.com
        """
        self.api_key = api_key or os.getenv('FORTNITE_API_KEY')
        if not self.api_key:
            print("⚠️ API ключ не найден!")
            print("Получите бесплатный ключ на https://fortniteapi.io")
            print("Создайте файл .env и добавьте: FORTNITE_API_KEY='ваш_ключ'")

        self.headers = {
            'Authorization': self.api_key
        }
        self.base_url = "https://fortniteapi.io/v1"

    def get_player_stats(self, username, platform="epic", time_window="season"):
        """
        Получение статистики игрока

        Parameters:
        - username: никнейм игрока
        - platform: 'epic', 'psn', 'xbl', 'kbm', 'gamepad', 'touch'
        - time_window: 'season' (текущий сезон), 'lifetime' (вся история)
        """
        if not self.api_key:
            return {"error": "API ключ не установлен"}

        try:
            # Сначала получаем account_id по имени
            lookup_url = f"{self.base_url}/lookup"
            params = {'username': username}
            response = requests.get(lookup_url, headers=self.headers, params=params)

            if response.status_code != 200:
                return {"error": f"Игрок не найден: {response.status_code}"}

            account_data = response.json()
            if not account_data.get('result'):
                return {"error": "Игрок не найден"}

            account_id = account_data['account_id']

            # Получаем статистику
            stats_url = f"{self.base_url}/stats"
            params = {
                'account': account_id,
                'platform': platform,
                'window': time_window
            }

            response = requests.get(stats_url, headers=self.headers, params=params)

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Ошибка API: {response.status_code}"}

        except requests.exceptions.RequestException as e:
            return {"error": f"Ошибка соединения: {str(e)}"}

    def display_stats(self, stats_data):
        """Красивый вывод статистики"""
        if 'error' in stats_data:
            print(f"❌ Ошибка: {stats_data['error']}")
            return

        print("\n" + "=" * 50)
        print("📊 СТАТИСТИКА FORTNITE")
        print("=" * 50)

        account = stats_data.get('account', {})
        print(f"👤 Игрок: {account.get('name', 'Неизвестно')}")
        print(f"🆔 ID: {account.get('id', 'Неизвестно')}")
        print(f"🎮 Платформа: {account.get('platform', 'Неизвестно')}")

        print("\n" + "-" * 30)
        print("🏆 ОБЩАЯ СТАТИСТИКА")
        print("-" * 30)

        global_stats = stats_data.get('global_stats', {})
        if global_stats:
            solo = global_stats.get('solo', {})
            duo = global_stats.get('duo', {})
            squad = global_stats.get('squad', {})
            ltm = global_stats.get('ltm', {})

            # Собираем общую статистику
            total_stats = {
                'Победы': 0,
                'Убийства': 0,
                'Матчей': 0,
                'Winrate': 0,
                'KD': 0
            }

            for mode in [solo, duo, squad, ltm]:
                if mode:
                    total_stats['Победы'] += mode.get('placetop1', 0)
                    total_stats['Убийства'] += mode.get('kills', 0)
                    total_stats['Матчей'] += mode.get('matches', 0)

            if total_stats['Матчей'] > 0:
                total_stats['Winrate'] = (total_stats['Победы'] / total_stats['Матчей']) * 100
                total_stats['KD'] = total_stats['Убийства'] / max(total_stats['Матчей'] - total_stats['Победы'], 1)

            print(f"🎯 Всего побед: {total_stats['Победы']:,}")
            print(f"⚔️ Всего убийств: {total_stats['Убийства']:,}")
            print(f"📈 Всего матчей: {total_stats['Матчей']:,}")
            print(f"📊 Винрейт: {total_stats['Winrate']:.2f}%")
            print(f"🎭 KD Ratio: {total_stats['KD']:.2f}")

        # Детальная статистика по режимам
        print("\n" + "-" * 30)
        print("🎮 СТАТИСТИКА ПО РЕЖИМАМ")
        print("-" * 30)

        modes = [
            ("Одиночные", solo),
            ("Парные", duo),
            ("Команды", squad),
            ("Временные", ltm)
        ]

        for mode_name, mode_data in modes:
            if mode_data and mode_data.get('matches', 0) > 0:
                wins = mode_data.get('placetop1', 0)
                kills = mode_data.get('kills', 0)
                matches = mode_data.get('matches', 0)
                deaths = max(matches - wins, 1)

                winrate = (wins / matches * 100) if matches > 0 else 0
                kd = kills / deaths if deaths > 0 else kills

                print(f"\n{mode_name}:")
                print(f"  Победы: {wins}")
                print(f"  Убийства: {kills}")
                print(f"  Матчей: {matches}")
                print(f"  Винрейт: {winrate:.1f}%")
                print(f"  KD: {kd:.2f}")

        # Информация о сезоне
        print("\n" + "-" * 30)
        print("📅 ИНФОРМАЦИЯ О СЕЗОНЕ")
        print("-" * 30)

        battle_pass = stats_data.get('battlePass', {})
        if battle_pass:
            print(f"Уровень: {battle_pass.get('level', 'N/A')}")
            print(f"Прогресс: {battle_pass.get('progress', 'N/A')}%")

        print(f"\n📊 Данные обновлены: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)


def main():
    """Главная функция программы"""
    print("📈 Fortnite Stats Viewer")
    print("=" * 50)

    # Инициализируем класс статистики
    stats_client = FortniteStats()

    while True:
        print("\n1. Показать статистику игрока")
        print("2. Выйти")

        choice = input("\nВыберите действие (1-2): ").strip()

        if choice == "1":
            username = input("Введите никнейм игрока: ").strip()

            if not username:
                print("⚠️ Пожалуйста, введите никнейм")
                continue

            platform = input("Платформа (epic/psn/xbl, по умолчанию epic): ").strip().lower()
            if not platform:
                platform = "epic"

            time_window = input("Период (season/lifetime, по умолчанию season): ").strip().lower()
            if not time_window:
                time_window = "season"

            print(f"\n🔍 Поиск статистики для {username}...")

            # Получаем статистику
            stats_data = stats_client.get_player_stats(username, platform, time_window)

            # Отображаем статистику
            stats_client.display_stats(stats_data)

            # Сохраняем в файл (опционально)
            save = input("\n💾 Сохранить в файл? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"fortnite_stats_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(stats_data, f, ensure_ascii=False, indent=2)
                print(f"✅ Статистика сохранена в {filename}")

        elif choice == "2":
            print("👋 Выход из программы...")
            break
        else:
            print("⚠️ Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()