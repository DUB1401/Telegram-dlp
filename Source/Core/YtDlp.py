import subprocess
import json
import sys
import os

class YtDlp:
	"""Абстракция управления библиотекой yt-dlp."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckWatermark(self, domain: str, format: dict) -> bool:
		"""
		Проверяет, содержит ли формат водяной знак.
			domain – домен сайта-источника;
			format – формат.
		"""

		IsWatermarked = False

		if domain == "tiktok.com":

			if format["format_note"] == "watermarked": IsWatermarked = True

		return IsWatermarked

	def __FilterInfo(self, info: dict) -> dict:
		"""
		Оставляет только основные форматы видео.
			info – словарь описания видео.
		"""

		Buffer = info.copy()
		Buffer["formats"] = list()
		
		for Format in info["formats"]:
			if Format["ext"] == "mp4": Buffer["formats"].append(Format)

		return Buffer

	def __PrettyFormatName(self, name: str, watermarked: bool = False) -> str:
		"""
		Делает название формата более привлекательным и округляет.
			name – название формата.
		"""

		SupportedResolutions = [144, 240, 360, 480, 720, 1080, 2560, 3840, 7680]

		if name != "audio only":

			if name and "x" in name:
				Width = int(name.split("x")[0].rstrip("p"))
				Width = min(SupportedResolutions, key = lambda SupportedResolution: abs(SupportedResolution - Width))
				if Width == 720: name = "HD"
				elif Width == 1080: name = "Full HD"
				elif Width == 2560: name = "2K"
				elif Width == 3840: name = "4K"
				elif Width == 7680: name = "8K"
				else: name = f"{Width}p"

			else: name = "null"

			if watermarked:
				name += "w"

		else:
			name = None

		return name

	def __SortResolutions(self, resolutions: dict) -> dict:
		"""
		Сортирует разрешения в определённом порядке.
			resolutions – словарь разрешений.
		"""
		
		Order = ["144p", "240p", "360p", "480p", "HD", "Full HD", "2K", "4K", "8K"]
		BaseResolutions = [Key for Key in resolutions if Key in Order]
		ExtraResolutions = [Key for Key in resolutions if Key not in Order]
		BaseResolutions = sorted(BaseResolutions, key = lambda Resolution: Order.index(Resolution))
		Resolutions = BaseResolutions + ExtraResolutions
		resolutions = {Key: resolutions[Key] for Key in Resolutions}
		
		return resolutions
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, lib_path: str | None = None, proxy: str | None = None):
		"""
		Абстракция управления библиотекой yt-dlp.
			lib_path – путь к исполняемому файлу библиотеки;
			proxy – данные прокси-сервера.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__LibPath = lib_path or "yt-dlp"
		self.__Proxy = f"--proxy {proxy}" if proxy else ""
	
	def download_audio(self, link: str, directory: str, filename: str) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла.
		"""

		IsSuccess = False
		if not os.path.exists(directory): os.makedirs(directory)
		
		try:
			Cookies = ""
			if "instagram.com" in link: Cookies = "--cookies yt-dlp/instagram.cookies"
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" {Cookies} -o {directory}{filename} --extract-audio --recode m4a {self.__Proxy}"
			if os.system(Command) == 0: IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)
		
		return IsSuccess
	
	def download_video(self, link: str, directory: str, filename: str, format_id: str) -> bool:
		"""
		Скачивает видео.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла;
			format_id – идентификатор формата загружаемого видео.
		"""
		
		IsSuccess = False
		if not os.path.exists(directory): os.makedirs(directory)
		
		try:
			Bestaudio = ""
			Cookies = ""
			if "youtube.com" in link or "youtu.be" in link or "instagram.com" in link: Bestaudio = "+bestaudio"
			if "instagram.com" in link: Cookies = "--cookies yt-dlp/instagram.cookies"
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id}{Bestaudio} --recode mp4 {self.__Proxy} {Cookies} -o {directory}{filename}"
			if os.system(Command) == 0: IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)
		
		return IsSuccess

	def get_info(self, link: str) -> dict | None:
		"""
		Получает описание видео.
			link – ссылка на видео.
		"""

		Info = None
		
		try:
			Cookies = ""
			if "instagram.com" in link: Cookies = "--cookies yt-dlp/instagram.cookies"
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download {Cookies} {self.__Proxy}",
			Dump = subprocess.getoutput(Command)

			if not Dump.startswith("ERROR"):
				Info = json.loads(Dump)
				self.__FilterInfo(Info)
	
		except Exception as ExceptionData: print(ExceptionData)
		
		return Info

	def get_resolutions(self, info: dict, pretty: bool = True) -> dict:
		"""
		Возвращает словарь определений разрешений, где клюём является ширина кадра, а значением – ID формата.
			info – словарное представления описания видео;
			pretty – указывает, нужно ли преобразовывать словарь разрешений в красивый вид.
		"""

		Resolutions = dict()

		for Format in info["formats"]:
			Watermarked = self.__CheckWatermark(info["webpage_url_domain"], Format)

			if Format["resolution"] or Watermarked:

				if Format["resolution"] not in Resolutions.values():
					Name = Format["resolution"]
					if pretty: Name = self.__PrettyFormatName(Name, Watermarked)
					if Name != None: Resolutions[Name] = Format["format_id"]

		Resolutions = self.__SortResolutions(Resolutions)

		return Resolutions