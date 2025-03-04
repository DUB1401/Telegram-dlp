from ..Configurator import Parameters

import subprocess
import json
import sys
import os

class BaseExtractor:
	"""Базовый модуль поддержки источника."""

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GetYtDlpOutput(self, parameters: list[str] = list()) -> str:
		"""
		Возвращает вывод команды, адресованной yt-dlp.
			parameters – список дополнительных параметров.
		"""

		AdditionalParameters = " ".join(parameters)
		Command = f"python3.{sys.version_info[1]} yt-dlp/yt-dlp \"{self._Link}\" {self._Proxy} {self._Cookies} {AdditionalParameters}" 

		return subprocess.getoutput(Command)
	
	def _UseCookies(self):
		"""Включает использование файла куков в базовых методах."""

		Domain = type(self).__name__.lower()
		if Domain != "baseextractor": self._Cookies = f"--cookies yt-dlp/{Domain}.cookies"

	def _ExecuteYtDlpCommand(self, parameters: list[str] = list()) -> int:
		"""
		Выполняет команду при помощи yt-dlp. Возвращает код завершения процесса.
			parameters – список дополнительных параметров.
		"""

		AdditionalParameters = " ".join(parameters)
		Command = f"python3.{sys.version_info[1]} yt-dlp/yt-dlp \"{self._Link}\" {self._Proxy} {self._Cookies} {AdditionalParameters}" 

		return os.system(Command)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, link: str, config: Parameters | None, recoding: bool = True):
		"""
		Базовый модуль поддержки источника.
			link – ссылка на видео;\n
			config – набор параметров источника;\n
			recoding – включает перекодирование файлов в популярные форматы.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self._Link = link
		self._Config = config or Parameters(dict())
		self._Recoding = recoding

		self._Proxy = f"--proxy {self._Config.proxy}" if self._Config.proxy else ""
		self._Cookies = ""

		self._PostInitMethod()

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def audio(self, path: str) -> bool:
		"""
		Получает аудиодорожку из видеоролика. Возвращает состояние успеха.
			path – путь для сохранения файла.
		"""

		Parameters = [
			f"-o \"{path}\"",
			"--extract-audio"
		]
		if self._Recoding: Parameters.append("--recode m4a")

		return not bool(self._ExecuteYtDlpCommand(Parameters))

	def info(self) -> dict | None:
		"""Получает словарь данных видео."""

		Parameters = [
			"--dump-json",
			"--quiet",
			"--no-warnings",
			"--skip-download"
		]
		Info = None
		Dump = self._GetYtDlpOutput(Parameters)
		if not Dump.startswith("ERROR"): Info = json.loads(Dump)

		return Info

	def video(self, path: str, format_id: str) -> bool:
		"""
		Скачивает видеоролик. Возвращает состояние успеха.
			path – путь для сохранения файла;\n
			format – идентификатор формата.
		"""

		Parameters = [
			f"-o \"{path}\"",
			f"--format {format_id}"
		]
		if self._Recoding: Parameters.append("--recode mp4")

		return not bool(self._ExecuteYtDlpCommand(Parameters))