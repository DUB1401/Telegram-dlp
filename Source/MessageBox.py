from dublib.Methods import ReadJSON
from telebot import TeleBot

class MessageBox:
	"""
	Контейнер сообщений Telegram.
	"""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#
	
	@property
	def compression(self) -> bool:
		"""Код базового языка интерфейса по стандарту ISO 639-1."""

		return self.__Data["base-language"]

	def __PutData(self, Message: str, Data: dict) -> str:
		"""
		Подставляет на выделенные места данные.
			Message – текст сообщения со слотами для подстановки;
			Data – словарь подстанавливаемых значений.
		"""

		# Для каждого параметра.
		for Key in Data.keys():
			# Слот.
			Slot = "{" + str(Key) + "}"
			
			# Если сообщение содержит слот.
			if Slot in Message:
				# Выполнение подстановки.
				Message = Message.replace(Slot, str(Data[Key]))

		return Message

	def __init__(self, path: str = "Source/Messages.json", bot: TeleBot | None = None):
		"""
		Контейнер сообщений Telegram.
			path – путь к файлу с сообщениями;
			bot – экземпляр бота.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Данные сообщений.
		self.__Data = ReadJSON(path)
		# Код базового языка.
		self.__BaseLanguage = self.__Data["base-language"]
		# Экземпляр бота.
		self.__Bot = bot

	def get(self, key: str, header: str | None = None, data: dict | None = None, language: str | None = None) -> str:
		"""
		Возвращает текст сообщения.
			key – ключ для получения текста из описательного файла;
			header – идентификатор заголовка;
			data – словарь подстанавливаемых значений;
			language – код языка по стандарту ISO 639-1.
		"""

		# Языки заголовка текста.
		TextLanguage = self.__BaseLanguage
		HeaderLanguage = self.__BaseLanguage

		# Если язык текста определён и в нём есть нужная секция, выбрать язык перевода текста.
		if language in self.__Data["messages"].keys() and key in self.__Data["messages"][language].keys(): TextLanguage = language
		# Если язык заголовка определён и в нём есть нужная секция, выбрать язык перевода заголовка.
		if language in self.__Data["headers"].keys() and key in self.__Data["headers"][language].keys(): HeaderLanguage = language

		# Текст сообщения.
		Message = self.__Data["messages"][TextLanguage][key]
		# Если указан заголовок, добавить его.
		if header != None: Message = self.__Data["headers"][HeaderLanguage][header] + "\n\n" + Message
		# Если переданы данные для подстановки, подставить.
		if data != None: Message = self.__PutData(Message, data)

		return Message

	def send(self, target: int | str, key: str, header: str | None = None, data: dict | None = None):
		"""
		Отправляет сообщение в чат.
			target – ID пользователя или чата;
			key – ключ для получения текста из описательного файла;
			header – идентификатор заголовка;
			data – словарь подстанавливаемых значений.
		"""

		# Если бот инициализирован.
		if self.__Bot != None:
			# Отправка сообщения.
			self.__Bot.send_message(
				chat_id = target,
				text = self.get(key, header, data),
				parse_mode = "MarkdownV2",
				disable_web_page_preview = True
			)

		else:
			# Выброс исключения.
			raise Exception("Bot not initialized into MessageBox object.")