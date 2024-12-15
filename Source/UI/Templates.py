from threading import Thread
from telebot import TeleBot, apihelper
from time import sleep

import random

class Animation:
	"""Текстовая анимация."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def delay(self) -> float:
		"Интервал отложенного старта."

		return self.__Delay

	@property
	def interval(self) -> float:
		"Базовый интервал анимации."

		return self.__Interval
	
	@property
	def length(self) -> int:
		"Количество элементов в анимации."

		return len(self.__Lines)
	
	@property
	def lines(self) -> list[tuple]:
		"Базовый интервал анимации."

		return self.__Lines

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Текстовая анимация."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Lines = list()
		self.__Interval = 0.0
		self.__Delay = 0.0

	def __getitem__(self, index: int) -> tuple[str, int]:
		"""
		Возвращает строку анимации.
			index – индекс строки.
		"""

		return self.__Lines[index]

	def add_lines(self, lines: str | list[str], interval: float | int | None = None):
		"""
		Добавляет строки в анимацию.
			lines – строка или список строк;\n
			interval – интервал ожидания.
		"""

		if type(lines) != list: lines = [lines]
		Interval = interval or self.__Interval
		for Line in lines: self.__Lines.append((Line, Interval))

	def set_delay(self, delay: float | int):
		"""
		Задаёт интервал отложенного старта.
			delay – интервал в секундах.
		"""

		self.__Delay = float(delay)

	def set_interval(self, interval: float | int):
		"""
		Задаёт базовый интервал анимации.
			interval – интервал в секундах.
		"""

		self.__Interval = float(interval)

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

	def __AnimateMessage(self, animations: list[Animation], primary: Animation | None):
		"""
		Поочерёдно заменяет подстроку \"%s\" на один из вариантов через интервалы времени.
			animations – анимация или список анимаций;\n
			primary – первая однократно проигрываемая анимация.
		"""

		CurrentAnimation = random.choice(animations)

		if primary:
			CurrentAnimation = primary
			primary = None

		CurrentAnimationLines = CurrentAnimation.lines
		AnimationIndex = 0
		sleep(CurrentAnimation.delay)
		
		while self.__Animation:

			try:
				sleep(CurrentAnimationLines[AnimationIndex][1])

				if self.__Animation:
					self.__AnimationValue = CurrentAnimationLines[AnimationIndex][0]
					AnimationIndex += 1
					self.update()

			except IndexError: 
				CurrentAnimation = random.choice(animations)
				CurrentAnimationLines = CurrentAnimation.lines
				AnimationIndex = 0

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
		
		#---> Генерация динамических атрибутов.
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

	def error(self, text: str | None = None, stop: bool = True):
		"""
		Помечает этап как неудачный.
			text – новое описание этапа;\n
			stop – указывает, следует ли считать выполнение прерванным.
		"""

		if not self.__End:
			self.__Statuses[self.__Index] = -1
			if text: self.__Procedures[self.__Index] = text

			if not stop:
				self.__Index += 1

			else:
				self.__End = True
				self.stop_animation()

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

	def start_animation(self, animation: Animation | list[Animation], primary: Animation | None = None):
		"""
		Запускает поочерёдную замену подстроки \"%s\" на один из вариантов через интервалы времени.
			animation – анимация или список анимаций;\n
			primary – первая однократно проигрываемая анимация.
		"""

		if type(animation) != list: animation = [animation]
		self.__AnimationThread = Thread(target = self.__AnimateMessage, args = [animation, primary])
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
			self.__Bot.edit_message_text(text = self.text, chat_id = self.__ChatID, message_id = self.__MessageID, parse_mode = self.__ParseMode)
		
		except apihelper.ApiException: pass