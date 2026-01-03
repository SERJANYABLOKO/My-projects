data = {
    "О планетах": {
        "текст": "Что если вода на Марсе это признак жизни?",
        "теги": [
            "Марс",
            "гипотезы"
        ]
    },
    "О чёрных дырах": {
        "текст": "Сингулярность на горизонте событий отсутствует",
        "теги": [
            "чёрные дыры",
            "факты"
        ]
    }
}

import os, json

class Database:
	def __init__(self, filename):
		self.filename = filename
		if not os.path.exists(self.filename):
			self.save_data({})

	def get_data(self):
		with open(f'{self.filename}', 'r', encoding='UTF-8') as file:
			return json.load(fp=file)

	def save_data(self, data):
		with open(f'{self.filename}', 'w', encoding='UTF-8') as file:
			json.dump(data, file, ensure_ascii=False, indent=4)

# db = Database('my.json')
# db.save_data(data)