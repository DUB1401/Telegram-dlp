from Source.Core.Storage import Storage

from dublib.Methods.Filesystem import RemoveDirectoryContent

import urllib.request
import subprocess
import json
import sys
import os

class YtDlp:
	"""Абстракция управления библиотекой yt-dlp."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def version(self) -> str:
		"""Версия библиотеки yt-dlp по умолчанию."""

		return "2024.10.07"

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

			if format["format_id"] == "download": IsWatermarked = True

		return IsWatermarked

	def __FilterInfo(self, info: dict) -> dict:
		"""
		Оставляет только основные форматы видео.
			info – словарь описания видео.
		"""

		Buffer = info.copy()
		Buffer["formats"] = list()
		
		for Format in info["formats"]:
			ChecksStatus = True

			if Format["ext"] == "mhtml": ChecksStatus = False
			elif Format["format_id"].startswith("dash_sep-"): ChecksStatus = False

			if ChecksStatus: Buffer["formats"].append(Format)

		return Buffer

	def __GetFilename(self, directory: str) -> str | None:
		"""
		Возвращает название файла.
			directory – директория загрузки пользователя.
		"""

		Filename = None
		Files = os.listdir(directory)
		if len(Files): Filename = Files[0]
		
		return Filename

	def __CheckLib(self, update: bool):
		"""
		Проверяет, загружена и обновлена ли библиотека.
			update – указывает, нужно ли обновлять библиотеку.
		"""

		if not os.path.exists("yt-dlp/yt-dlp"):
			urllib.request.urlretrieve(f"https://github.com/yt-dlp/yt-dlp/releases/download/{self.version}/yt-dlp", "yt-dlp/yt-dlp")
			os.system("chmod u+x yt-dlp/yt-dlp")

		elif update:
			os.system("yt-dlp/yt-dlp -U")

	def __PrettyFormatName(self, name: str, watermarked: bool = False) -> str:
		"""
		Делает название формата более привлекательным и округляет.
			name – название формата.
		"""

		SupportedResolutions = [144, 240, 360, 480, 720, 1080, 2560, 3840, 7680]

		PrettyName = None
		
		if name not in ["audio only"]:

			if name and "x" in name:
				PrettyName = name
				Width = int(PrettyName.split("x")[0].rstrip("p"))
				Width = min(SupportedResolutions, key = lambda SupportedResolution: abs(SupportedResolution - Width))
				if Width == 720: PrettyName = "HD"
				elif Width == 1080: PrettyName = "Full HD"
				elif Width == 2560: PrettyName = "2K"
				elif Width == 3840: PrettyName = "4K"
				elif Width == 7680: PrettyName = "8K"
				else: PrettyName = f"{Width}p"

			if PrettyName and watermarked: PrettyName += "w"

		return PrettyName

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
	# >>>>> СПЕЦИФИЧЕСКИЕ МЕТОДЫ СКАЧИВАНИЯ АУДИО <<<<< #
	#==========================================================================================#

	def __instagram_audio(self, link: str, path: str, recoding: bool = True) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			path – путь к файлу;
			recoding – указывает, нужно ли перекодировать файл в M4A.
		"""

		IsSuccess = False
		Recoding = "--recode m4a" if recoding else ""
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {path} --extract-audio {Recoding} --cookies yt-dlp/instagram.cookies {self.__Proxy}"
		ExitCode = os.system(Command)
		if ExitCode == 0: IsSuccess = True

		return IsSuccess
	
	def __tiktok_audio(self, link: str, path: str, recoding: bool = True) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			path – путь к файлу;
			recoding – указывает, нужно ли перекодировать файл в M4A.
		"""

		IsSuccess = False
		Recoding = "--recode m4a" if recoding else ""
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {path} --extract-audio {Recoding} {self.__Proxy} -f 'b[url!^=\"https://www.tiktok.com/\"]'"
		ExitCode = os.system(Command)

		if ExitCode == 0:
			IsSuccess = True

		elif self.__Proxy:
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {path} --extract-audio {Recoding} -f 'b[url!^=\"https://www.tiktok.com/\"]'"
			ExitCode = os.system(Command)
			if ExitCode == 0: IsSuccess = True

		if ExitCode != 0:
			Extractor = "--extractor-args \"tiktok:api_hostname=api31-normal-useast2a.tiktokv.com;app_info=7370097943049078561\""
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {path} --extract-audio {Recoding} {self.__Proxy} -f 'b[url!^=\"https://www.tiktok.com/\"]' {Extractor}"
			ExitCode = os.system(Command)
			if ExitCode == 0: IsSuccess = True

		return IsSuccess
	
	def __youtube_audio(self, link: str, path: str, recoding: bool = True) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			path – путь к файлу;
			recoding – указывает, нужно ли перекодировать файл в M4A.
		"""

		IsSuccess = False
		Recoding = "--recode m4a" if recoding else ""
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {path} --extract-audio {Recoding}"
		ExitCode = os.system(Command)
		if ExitCode == 0: IsSuccess = True

		return IsSuccess

	#==========================================================================================#
	# >>>>> СПЕЦИФИЧЕСКИЕ МЕТОДЫ СКАЧИВАНИЯ ВИДЕО <<<<< #
	#==========================================================================================#

	def __instagram_video(self, link: str, path: str, format_id: str, recoding: bool = True) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			path – путь к файлу;
			format_id – идентификатор формата загружаемого видео;
			recoding – указывает, нужно ли перекодировать файл в MP4.
		"""

		IsSuccess = False
		Recoding = "--recode mp4" if recoding else ""
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id}+bestaudio {Recoding} -o {path} --cookies yt-dlp/instagram.cookies  {self.__Proxy}"
		ExitCode = os.system(Command)
		if ExitCode in [0, 256]: IsSuccess = True

		return IsSuccess
	
	def __tiktok_video(self, link: str, path: str, format_id: str, recoding: bool = True) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			path – путь к файлу;
			format_id – идентификатор формата загружаемого видео;
			recoding – указывает, нужно ли перекодировать файл в MP4.
		"""

		IsSuccess = False
		Recoding = "--recode mp4" if recoding else ""
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id} {Recoding} -o {path} {self.__Proxy} -f {format_id}"
		ExitCode = os.system(Command)

		if ExitCode == 0:
			IsSuccess = True

		elif self.__Proxy:
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id} {Recoding} -o {path} -f {format_id}"
			ExitCode = os.system(Command)
			if ExitCode == 0: IsSuccess = True

		if ExitCode != 0:
			Extractor = "--extractor-args \"tiktok:api_hostname=api31-normal-useast2a.tiktokv.com;app_info=7370097943049078561\""
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id} {Recoding} -o {path} {self.__Proxy} -f {format_id} {Extractor}"
			ExitCode = os.system(Command)
			if ExitCode == 0: IsSuccess = True

		return IsSuccess
	
	def __youtube_video(self, link: str, path: str, format_id: str, recoding: bool = True) -> bool:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			path – путь к файлу;
			format_id – идентификатор формата загружаемого видео;
			recoding – указывает, нужно ли перекодировать файл в MP4.
		"""

		IsSuccess = False
		Recoding = "--recode mp4" if recoding else ""
		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id}+bestaudio {Recoding} -o {path}"
		ExitCode = os.system(Command)
		if ExitCode in [0, 256]: IsSuccess = True

		return IsSuccess

	#==========================================================================================#
	# >>>>> СПЕЦИФИЧЕСКИЕ МЕТОДЫ ПОЛУЧЕНИЯ ДАННЫХ <<<<< #
	#==========================================================================================#

	def __instagram_info(self, link: str) -> dict | None:
		"""
		Получает описание видео.
			link – ссылка на видео.
		"""

		Info = None

		for Try in range(2):
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download --cookies yt-dlp/instagram.cookies {self.__Proxy}",
			Dump = subprocess.getoutput(Command)
			
			if not Dump.startswith("ERROR"):
				if "\n" in Dump: Dump = Dump.split("\n")[0]
				Info = json.loads(Dump)
			
			if Info: break
			elif Try == 0 and "instagram" in self.__Modules.keys() and self.__Modules["instagram"]["cookies_generator"]: os.system(self.__Modules["instagram"]["cookies_generator"])

		return Info
	
	def __tiktok_info(self, link: str) -> dict | None:
		"""
		Получает описание видео.
			link – ссылка на видео.
		"""

		Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download {self.__Proxy}",
		Dump = subprocess.getoutput(Command)
		Info = None 

		if not Dump.startswith("ERROR"):
			Info = json.loads(Dump)

		elif self.__Proxy:
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download",
			Dump = subprocess.getoutput(Command)
			if not Dump.startswith("ERROR"): Info = json.loads(Dump)
		
		if not Info:
			Extractor = "--extractor-args \"tiktok:api_hostname=api31-normal-useast2a.tiktokv.com;app_info=7370097943049078561\""
			Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download {self.__Proxy} {Extractor}",
			Dump = subprocess.getoutput(Command)
			if not Dump.startswith("ERROR"): Info = json.loads(Dump)

		if type(Info) == dict: 
			Formats = Info["formats"]

			for Format in list(Formats):
				if Format["format_id"].endswith("-2"): Formats.remove(Format)

			Info["formats"] = Formats
			Info["formats"][0]["resolution"] = "480x720"

		return Info

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, storage: Storage, lib_path: str, proxy: str | None = None, modules: dict | None = None, update: bool = False):
		"""
		Абстракция управления библиотекой yt-dlp.
			storage – хранилище данных;\n
			lib_path – путь к исполняемому файлу библиотеки;\n
			proxy – данные прокси-сервера;\n
			modules – словарь опций модуля.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__LibPath = lib_path
		self.__Proxy = f"--proxy {proxy}" if proxy else ""
		self.__Storage = storage
		self.__Modules = modules or dict()

		self.__CheckLib(update)
	
	def download_audio(self, link: str, directory: str, filename: str, recoding: bool = True) -> str | None:
		"""
		Скачивает аудиодорожку и перекодирует её в формат m4a.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла;
			recoding – указывает, нужно ли перекодировать файл в M4A.
		"""

		if not os.path.exists(directory): os.makedirs(directory)
		else: RemoveDirectoryContent(directory)
		Domain = self.__Storage.parse_site_name(link)
		IsSuccess = False
		Recoding = "--recode m4a" if recoding else ""
		Path = f"\"{directory}/{filename}.%(ext)s\""

		try:
			if Domain == "instagram.com": IsSuccess = self.__instagram_audio(link, Path, recoding)
			elif Domain == "tiktok.com": IsSuccess = self.__tiktok_audio(link, Path, recoding)
			elif Domain == "youtube.com": IsSuccess = self.__youtube_audio(link, Path, recoding)

			else:
				Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" -o {Path} --extract-audio {Recoding} {self.__Proxy}"
				if os.system(Command) == 0: IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)
		
		if IsSuccess: return self.__GetFilename(directory)
	
	def download_video(self, link: str, directory: str, filename: str, format_id: str, recoding: bool = True) -> str | None:
		"""
		Скачивает видео.
			link – ссылка на видео;
			directory – директория загрузки;
			filename – имя файла;
			format_id – идентификатор формата загружаемого видео;
			recoding – указывает, нужно ли перекодировать файл в MP4.
		"""
		
		if not os.path.exists(directory): os.makedirs(directory)
		else: RemoveDirectoryContent(directory)
		Domain = self.__Storage.parse_site_name(link)
		IsSuccess = False
		Recoding = "--recode mp4" if recoding else ""
		Path = f"\"{directory}{filename}.%(ext)s\""
		
		try:

			if Domain == "instagram.com": IsSuccess = self.__instagram_video(link, Path, format_id, recoding)
			elif Domain == "tiktok.com": IsSuccess = self.__tiktok_video(link, Path, format_id, recoding)
			elif Domain in ["youtube.com", "vk.com"]: IsSuccess = self.__youtube_video(link, Path, format_id, recoding)

			else:
				Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --format {format_id} {Recoding} -o {Path} {self.__Proxy}"
				if os.system(Command) == 0: IsSuccess = True

		except Exception as ExceptionData: print(ExceptionData)
		
		if IsSuccess: return self.__GetFilename(directory)

	def get_info(self, link: str) -> dict | None:
		"""
		Получает описание видео.
			link – ссылка на видео.
		"""

		Domain = self.__Storage.parse_site_name(link)
		Info = None
		
		try:

			if Domain == "instagram.com": Info = self.__instagram_info(link)
			elif Domain == "tiktok.com": Info = self.__tiktok_info(link)
				
			else: 
				Command = f"python3.{sys.version_info[1]} {self.__LibPath} \"{link}\" --dump-json --quiet --no-warnings --skip-download {self.__Proxy}",
				Dump = subprocess.getoutput(Command)
				if not Dump.startswith("ERROR"): Info = json.loads(Dump)

			if Info: Info = self.__FilterInfo(Info)
	
		except Exception as ExceptionData: print(ExceptionData)
		
		# from dublib.Methods.JSON import WriteJSON
		# WriteJSON("test.json", Info)

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