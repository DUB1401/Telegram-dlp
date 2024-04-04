from dublib.Methods import ReadJSON, WriteJSON
from telebot.types import User

import os

class UserData:
	"""Объектное представление пользователя."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#
	
	@property
	def compression(self) -> bool:
		"""Состояние: используется ли компрессия для этого пользователя."""

		return self.__Data["compression"]
	
	@property
	def downloading(self) -> bool:
		"""Состояние: загружает ли пользователь сейчас файл."""

		return self.__Data["downloading"]

	@property
	def id(self) -> int:
		"""ID пользователя."""

		return self.__UserID

	@property
	def language(self) -> str:
		"""Код используемого клиентом языка по стандарту ISO 639-1."""

		return self.__Data["language"]

	@property
	def premium(self) -> bool:
		"""Состояние: есть ли Premium-подписка у пользователя."""

		return self.__Data["premium"]

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, user_id: int, data: dict):
		"""Объектное представление пользователя."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# ID пользователя.
		self.__UserID = user_id
		# Словарное представление данных пользователя.
		self.__Data = data

class UsersManager:
	"""Менеджер пользователей."""

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CreateUser(self, UserInfo: User) -> UserData:
		"""Создаёт пользователя."""
		
		# Запись пользовательских данных.
		self.__Users[UserInfo.id] = {
			"premium": bool(UserInfo.is_premium),
			"language": UserInfo.language_code.split("_")[0], 
			"compression": True,
			"downloading": False
		}
		# Сохранение файла.
		self.__SaveUser(UserInfo.id)

		return UserData(UserInfo.id, self.__Users[UserInfo.id])

	def __LoadUsers(self):
		"""Загружает данные пользователей."""

		# Получение списка файлов в директории пользователей.
		Files = os.listdir("Data/Users")
		# Фильтрация только файлов формата JSON.
		Files = list(filter(lambda List: List.endswith(".json"), Files))

		# Для каждого файла.
		for File in Files:
			# Чтение файла.
			Bufer = ReadJSON(f"Data/Users/{File}")
			# ID пользователя.
			UserID = int(File.replace(".json", ""))
			# Запись пользовательских данных.
			self.__Users[UserID] = Bufer

	def __SaveUser(self, UserID: int):
		"""Сохраняет файл пользователя."""
		
		# Сохранение файла.
		WriteJSON(f"Data/Users/{UserID}.json", self.__Users[UserID])

	def __init__(self):
		"""Менеджер пользователей."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Словарь пользователей.
		self.__Users = dict()

		# Если директория пользователей не существует, создать её.
		if not os.path.exists("Data/Users"): os.makedirs("Data/Users")
		# Загрузка данных пользователей.
		self.__LoadUsers()

	def auth(self, user: User) -> UserData:
		"""
		Выполняет идентификацию пользователя. Возвращает объектное представление данных пользователя.
			user – данные пользователя.
		"""

		# Пользователь.
		User = self.get_user(user.id)

		# Если пользователь не идентифицирован.
		if User == None:
			# Создание нового пользователя.
			User = self.__CreateUser(user)

		else:
			# Обновление Premium-статуса пользователя.
			self.set_user_value(user.id, "premium", bool(user.is_premium))

		return User

	def get_user(self, user_id: int | str) -> UserData | None:
		"""
		Возвращает объект данных пользователя.
			user_id – ID пользователя.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Пользователь.
		User = None
		# Если пользователь уже зарегестрирован в системе, записать его данные.
		if user_id in self.__Users.keys(): User = UserData(user_id, self.__Users[user_id])
		
		return User

	def get_user_data(self, user_id: int | str) -> dict | None:
		"""
		Возвращает словарь данных пользователя.
			user_id – ID пользователя.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Пользователь.
		User = None
		# Если пользователь уже зарегистрирован в системе, записать его данные.
		if user_id in self.__Users.keys(): User = self.__Users[user_id]

		return User

	def set_user_value(self, user_id: int | str, key: str, value: any) -> bool:
		"""
		Устанавливает новое значение для параметра пользователя.
			user_id – ID пользователя;
			key – ключ в словаре данных пользователя;
			value – значение ключа.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = False

		# Если пользователь идентифицирован.
		if user_id in self.__Users.keys():

			# Если ключ существует.
			if key in self.__Users[user_id].keys():
				# Перезапись данных пользователя.
				self.__Users[user_id][key] = value
				# Сохранение файла.
				self.__SaveUser(user_id)
				# Состояние: успешно ли обновление.
				IsSuccess = True

			else:
				# Выброс исключения.
				raise KeyError(f"Unknown key \"{key}\" in user data dictionary.")

		return IsSuccess

	def update_user_data(self, user_id: int | str, data: dict) -> bool:
		"""
		Полностью перезаписывает данные пользователя. Возвращает False при ошибке идентификации пользователя.
			user_id – ID пользователя;
			data – словарь данных пользователя.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = True

		# Если передан словарь и пользователь идентифицирован.
		if type(data) == dict and user_id in self.__Users.keys():
			# Перезапись данных пользователя.
			self.__Users[user_id] = data
			# Сохранение файла.
			self.__SaveUser(user_id)

		elif type(data) != dict:
			# Переключение состояния.
			IsSuccess = False
			# Выброс исключения.
			raise TypeError("Expected dict() type of data.")

		else:
			# Переключение состояния.
			IsSuccess = False

		return IsSuccess

	def remove_user(self, user_id: int | str) -> bool:
		"""
		Удаляет пользователя из системы.
			user_id – ID пользователя.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = False

		# Если пользователь идентифицирован.
		if user_id in self.__Users.keys():
			# Удаление пользователя.
			del self.__Users[user_id]
			# Удаление файлов пользователя.
			if os.path.exists(f"Data/Users/{user_id}.json") == True: os.remove(f"Data/Users/{user_id}.json")
			# Переключение состояния.
			IsSuccess = True

		return IsSuccess