from threading import Thread
from telebot import TeleBot, apihelper
from time import sleep

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

		Text = self.__Title + "\n"

		for Index in range(len(self.__Procedures)):
			Emoji = self.__Emoji[self.__Statuses[Index]]
			Text += Emoji + " " + self.__Procedures[Index] + "\n"
			if self.__IsOnlyCurrent and Index == self.__Index: break

		Text += self.__Footer
		if "%s" in Text: Text = Text % self.__AnimationValue

		return Text

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __AnimateMessage(self, variants: list[str], interval: int, delay: int):
		"""
		Поочерёдно заменяет подстроку \"%s\" на один из вариантов через интервалы времени.
			variants – список вариантов для подстановки;\n
			interval – интервал обновления в секундах;\n
			delay – интервал отложенного запуска.
		"""

		VariantIndex = 0
		sleep(delay)
		
		while self.__Animation:

			try:
				sleep(interval)

				if self.__Animation:
					self.__AnimationValue = variants[VariantIndex]
					VariantIndex += 1
					self.update()

			except IndexError: VariantIndex = 0

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
		self.__End = False

		self.__Title = ""
		self.__Footer = ""

		self.__Animation = False
		self.__AnimationValue = ""
		self.__AnimationThread = None

		self.__Emoji = {
			-1: "❌",
			0: "⏳",
			1: "✅"
		}

	def error(self, stop: bool = True):
		"""
		Помечает этап как неудачный.
			stop – указывает, следует ли считать выполнение прерванным.
		"""

		if not self.__End:
			self.__Statuses[self.__Index] = -1
			if not stop: self.__Index += 1
			else: self.__End = True
			self.update()

	def next(self, text: str | None = None):
		"""
		Переходит к следующему этапу.
			text – новое описание этапа.
		"""

		if not self.__End:
			self.__Statuses[self.__Index] = 1
			if text: self.__Procedures[self.__Index] = text
			self.__Index += 1
			self.update()

	def send(self):
		"""Отправляет базовое сообщение."""

		if not self.__End: self.__MessageID = self.__Bot.send_message(text = self.text, chat_id = self.__ChatID, parse_mode = self.__ParseMode).id

	def set_footer(self, text: str | None, update: bool = False):
		"""
		Задаёт текст подписи под прогрессом.
			text – подпись;\n
			update – указывает, нужно ли обновить сообщение.
		"""

		self.__Footer = text or ""
		if update: self.update()

	def set_title(self, text: str | None, update: bool = False):
		"""
		Задаёт текст подписи над прогрессом.
			text – подпись;\n
			update – указывает, нужно ли обновить сообщение.
		"""

		self.__Title = text or ""
		if update: self.update()

	def start_animation(self, variants: list[str], interval: int, delay: int = 0):
		"""
		Запускает поочерёдную замену подстроки \"%s\" на один из вариантов через интервалы времени.
			variants – список вариантов для подстановки;\n
			interval – интервал обновления в секундах;\n
			delay – интервал отложенного запуска.
		"""

		self.__AnimationThread = Thread(target = self.__AnimateMessage, args = [variants, interval, delay])
		self.__Animation = True
		self.__AnimationThread.start()

	def stop_animation(self):
		"""Останавливает поочерёдную замену подстроки \"%s\" на один из вариантов через интервалы времени."""

		self.__Animation = False
		self.__AnimationValue = ""
		self.__AnimationThread = None

	def update(self):
		"""Обновляет сообщение."""

		try:
			if not self.__End: self.__Bot.edit_message_text(text = self.text, chat_id = self.__ChatID, message_id = self.__MessageID, parse_mode = self.__ParseMode)
		
		except apihelper.ApiException: pass