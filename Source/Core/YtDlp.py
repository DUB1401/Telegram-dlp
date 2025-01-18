from Source.Core.Extractors.Base import BaseExtractor
from Source.Core.Configurator import Configurator
from Source.Core.Storage import Storage
from .Extractors import *

from dublib.Methods.Filesystem import RemoveDirectoryContent

import urllib.request
import os

class YtDlp:
	"""Абстракция управления библиотекой yt-dlp."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def version(self) -> str:
		"""Версия библиотеки yt-dlp по умолчанию."""

		return "2025.01.15"

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

		if domain == ExtendedSupport.TikTok.name:

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

	def __CheckLib(self):
		"""Проверяет, загружена и обновлена ли библиотека."""

		if not os.path.exists("yt-dlp/yt-dlp"):
			urllib.request.urlretrieve(f"https://github.com/yt-dlp/yt-dlp/releases/download/{self.version}/yt-dlp", "yt-dlp/yt-dlp")
			os.system("chmod u+x yt-dlp/yt-dlp")

		elif self.__Settings["lib_autoupdate"]:
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
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, storage: Storage, settings: dict):
		"""
		Абстракция управления библиотекой yt-dlp.
			storage – хранилище данных;\n
			settings – словарь настроек.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Storage = storage
		self.__Settings = settings.copy()

		self.__Configurator = Configurator(self.__Settings["configs"])

		self.__CheckLib()
	
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
		Path = f"{directory}/{filename}.%(ext)s"
		IsSuccess = False
		SourceType = None
		
		try: SourceType = ExtendedSupport(Domain)
		except: pass

		Config = self.__Configurator.get_config(SourceType)

		try:

			if SourceType in EXTRACTORS.keys():
				Extractor: BaseExtractor = EXTRACTORS[SourceType](link, Config, recoding)
				IsSuccess = Extractor.audio(Path)

			else: IsSuccess = BaseExtractor(link, Config, recoding).audio(Path)

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
		Path = f"{directory}{filename}.%(ext)s"
		IsSuccess = False
		SourceType = None

		try: SourceType = ExtendedSupport(Domain)
		except: pass

		Config = self.__Configurator.get_config(SourceType)
		
		try:

			if SourceType in EXTRACTORS.keys():
				Extractor: BaseExtractor = EXTRACTORS[SourceType](link, Config, recoding)
				IsSuccess = Extractor.video(Path, format_id)

			else: IsSuccess = BaseExtractor(link, Config, recoding).video(Path, format_id)

		except Exception as ExceptionData: print(ExceptionData)
		
		if IsSuccess: return self.__GetFilename(directory)

	def get_info(self, link: str) -> dict | None:
		"""
		Получает описание видео.
			link – ссылка на видео.
		"""

		Domain = self.__Storage.parse_site_name(link)
		SourceType = None
		Info = None

		try: SourceType = ExtendedSupport(Domain)
		except: pass

		Config = self.__Configurator.get_config(SourceType)
		
		try:

			if SourceType in EXTRACTORS.keys():
				Extractor: BaseExtractor = EXTRACTORS[SourceType](link, Config)
				Info = Extractor.info()

			else: Info = BaseExtractor(link, Config).info()

			if Info: Info = self.__FilterInfo(Info)
	
		except Exception as ExceptionData: print(ExceptionData)

		# from dublib.Methods.Filesystem import WriteJSON
		# WriteJSON("Test.json", Info)

		return Info

	def get_resolutions(self, info: dict, pretty: bool = True) -> dict[str, str]:
		"""
		Возвращает словарь определений разрешений, где клюём является ширина кадра, а значением – ID формата.
			info – словарное представления описания видео;
			pretty – указывает, нужно ли преобразовывать словарь разрешений в красивый вид.
		"""

		Resolutions = dict()

		for Format in info["formats"]:
			Watermarked = self.__CheckWatermark(info["extractor"], Format)

			if Format["resolution"] or Watermarked:

				if Format["resolution"] not in Resolutions.values():
					Name = Format["resolution"]
					if pretty: Name = self.__PrettyFormatName(Name, Watermarked)
					if Name != None: Resolutions[Name] = Format["format_id"]

		Resolutions = self.__SortResolutions(Resolutions)
		
		return Resolutions