from telebot import TeleBot

class StepsIndicator:
	"""Шаблон: шаги выполнения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def message_id(self) -> int | None:
		"""ID сообщения."""

		return self.__MessageID

	@property
	def text(self) -> str:
		"""Текущий текст сообщения."""

		Text = ""

		for Index in range(len(self.__Procedures)):
			Emoji = self.__Emoji[self.__Statuses[Index]]
			Text += Emoji + self.__Procedures[Index] + "\n"
			if self.__IsOnlyCurrent and Index == self.__Index: break

		return Text

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, bot: TeleBot, chat_id: int, procedures: list[str], parse_mode: str | None = None, only_current: bool = True):
		"""
		Шаблон: шаги выполнения.
			bot – бот Telegram;\n
			chat_id – ID чата;\n
			procedures – список описаний процедур;\n
			parse_mode – режим парсинга текста;\n
			only_current – указывает, нужно ли выводить только пройденные и текущий шаги.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__Bot = bot
		self.__ChatID = chat_id
		self.__Procedures = procedures
		self.__ParseMode = parse_mode
		self.__IsOnlyCurrent = only_current

		self.__Statuses = [0] * len(procedures)
		self.__MessageID = None
		self.__Index = 0

		self.__Emoji = {
			-1: "❌",
			0: "⏳",
			1: "✅"
		}

	def error(self):
		"""Помечает этап как неудачный."""

		self.__Statuses[self.__Index] = -1
		self.__Index += 1
		self.update()

	def next(self):
		"""Переходит к следующему этапу."""

		self.__Statuses[self.__Index] = 1
		self.__Index += 1
		self.update()

	def send(self):
		"""Отправляет базовое сообщение."""

		self.__MessageID = self.__Bot.send_message(text = self.text, chat_id = self.__ChatID, parse_mode = self.__ParseMode).id

	def update(self):
		"""Обновляет сообщение."""

		self.__Bot.edit_message_text(text = self.text, chat_id = self.__ChatID, message_id = self.__MessageID, parse_mode = self.__ParseMode)

	

		