from Source.Core import ExtendedSupport

from dublib.Methods.Filesystem import RemoveDirectoryContent
from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.Engine.Bus import ExecutionStatus
from dublib.Methods.Data import Zerotify

from urllib.parse import urlparse, parse_qs, urlencode
from time import sleep
import base64
import sys
import os

class Storage:
	"""Хранилище данных медиа-файлов."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __RemoveQueryParameter(self, url: str, key: str) -> str:
		"""
		Удаляет параметр запроса из ссылки.
			url – ссылка;\n
			key – ключ параметра.
		"""

		Parts = urlparse(url)
		Query = parse_qs(Parts.query)
		Query.pop(key, None)
		NewQuery = urlencode(Query, doseq = True)
		NewURL = Parts._replace(query = NewQuery).geturl()
		
		return NewURL

	def __StringToFilename(self, filename: str) -> str:
		"""
		Преобразует строку в допустимое имя файла.
			filename – строка.
		"""

		filename = filename.replace("\0", "")
		filename = filename.replace("\\", "")
		filename = filename.replace("/", "")
		filename = filename[:48]
		
		return filename

	def __SearchFormat(self, data: dict, quality: str, compression: bool, recoding: bool, watermarked: bool) -> int | None:
		"""
		Возвращает индекс формата.
			data – данные видео;
			quality – качество видео;
			compression – использовалось ли сжатие;
			recoding – перекодирован ли файл;
			watermarked – включает поиск среди видео с водяным знаком.
		"""

		FormatIndex = None
		Key = "watermarked" if watermarked else "video"

		for Index in range(len(data[Key])):

			if data[Key][Index]["quality"] == quality and data[Key][Index]["compression"] == compression and data[Key][Index]["recoding"] == recoding:
				FormatIndex = Index
				break

		return FormatIndex

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, directory: str):
		"""
		Хранилище данных медиа-файлов.
			directory – путь к директории хранения.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__StorageDirectory = directory
		self.__Venv = os.path.exists(".venv")

	def check_for_playlist(self, site: str, link: str) -> bool:
		"""
		Проверяет, ведёт ли ссылка на плейлист.
			site – домен обрабатываемого сайта;\n
			link – ссылка.
		"""

		IsPlaylist = False

		match site:

			case "youtube":
				if "/playlist?list" in link: IsPlaylist = True

		return IsPlaylist

	def check_link(self, site: str, link: str) -> str:
		"""
		Проверяет, нужно ли ссылке преобразования для корректной загрузке и выполняет эту процедуру.
			site – домен обрабатываемого сайта;\n
			link – ссылка.
		"""

		match site:
		
			case "instagram":

				if "/s/" in link:
					Buffer = link.split("?")[0].split("/")[-1]
					
					if not Buffer.isdigit():
						link = "https://www.instagram.com/stories/highlights/" + str(base64.b64decode(Buffer)).split(":")[-1].rstrip("'")

				link = self.__RemoveQueryParameter(link, "igsh")

			case "youtube":
				if "&list=" in link: link = self.__RemoveQueryParameter(link, "list")

		return link

	def get_file_message_id(self, site: str, id: str, quality: str, compression: bool, recoding: bool, watermarked: bool = False) -> list[int | None]:
		"""
		Возвращает идентификаторы чата и сообщения с файлом.
			site – название сайта;
			id – идентификатор видео;
			quality – качество;
			compression – использовалось ли сжатие при загрузке;
			recoding – указывает, перекодирован ли файл;
			watermarked – указывает, что видео имеет водяной знак.
		"""

		ChatID = None
		MessageID = None
		Key = "watermarked" if watermarked else "video"
		Path = f"{self.__StorageDirectory}/Files/{site}"

		if os.path.exists(f"{Path}/{id}.json"):
			File = ReadJSON(f"{Path}/{id}.json")

			if quality == "audio":

				if recoding: 
					ChatID = File["recoded_audio"]["chat_id"]
					MessageID = File["recoded_audio"]["message_id"]

				else:
					ChatID = File["audio"]["chat_id"]
					MessageID = File["audio"]["message_id"]

			else:
				FormatIndex = self.__SearchFormat(File, quality, compression, recoding, watermarked)

				if FormatIndex != None:
					ChatID = File[Key][FormatIndex]["chat_id"]
					MessageID = File[Key][FormatIndex]["message_id"]

		return [ChatID, MessageID]

	def get_filesize_from_info(self, site: str, video_id: str, format_id: str) -> int | None:
		"""
		Возвращает примерный размер видео в MB.
			site – название сайта;
			id – идентификатор видео.
		"""

		Info = self.get_info(site, video_id)
		
		Size = None
		if not Info: return

		for Format in Info["formats"]:
			Format: dict

			if Format["format_id"] == format_id:

				if "filesize" in Format.keys():
					Size = Zerotify(Format["filesize"])

					if Size: 
						Size /= 1024 * 1000
						Size = int(Size)

					break

				elif "filesize_approx" in Format.keys():
					Size = Zerotify(Format["filesize_approx"])

					if Size: 
						Size /= 1024 * 1000
						Size = int(Size)

					break

		return Size
 
	def get_info(self, site: str, id: str | None) -> dict | None:
		"""
		Вовзаращает сохранённые данные видео, если поддерживается.
			site – название сайта;
			id – идентификатор видео.
		"""

		Info = None

		if id:
			Path = f"{self.__StorageDirectory}/Info/{site}/{id}.json"
			if os.path.exists(Path): Info = ReadJSON(Path)

		return Info

	def parse_site_name(self, link: str) -> str | None:
		"""
		Получает название сайта из ссылки.
			link – ссылка.
		"""

		Site = None

		try:
			Site = urlparse(link).hostname.replace("www.", "")

			if Site.endswith(".com"): Site = Site[:-4]
			if Site.startswith("m."): Site = Site[2:]

			if Site == "youtu.be": Site = "youtube"
			if Site == "vt.tiktok" or Site == "vm.tiktok": Site = "tiktok"
			if "pornhub" in Site: Site = "pornhub"
			if Site == "vkvideo.ru": Site = "vk"
			if Site == "rutube.ru": Site = "rutube"
			
		except: pass
		
		return Site
	
	def parse_video_id(self, site: str, link: str) -> str | None:
		"""
		Получает идентификатор видео из ссылки, если сохранение данных видео из источника поддерживается.
			site – название сайта;
			link – ссылка.
		"""

		VideoID = None

		if site == "instagram":

			if "/reel/" in link:
				VideoID = link.split("?")[0].rstrip("/").split("/")[-1]

		if site == "youtube":

			if "youtube.com" in link and "/shorts/" in link:
				VideoID = link.split("/shorts/")[-1].split("?")[0]

			elif "youtube.com" in link:
				Query = urlparse(link).query
				Query = parse_qs(Query)
				if "v" in Query.keys(): VideoID = Query["v"][0]

			elif "youtu.be" in link:
				VideoID = link.split("?")[0].split("/")[-1]

		if site == "tiktok":
			Buffer = link.split("?")[0].split("/")[-1]
			if Buffer.isdigit(): VideoID = Buffer

			if not VideoID:
				VideoID = link.rstrip("/").split("/")[-1]

		if site == "vk":
			
			if "video" in link:
				Query = urlparse(link).query
				Query = parse_qs(Query)
				if "z" in Query.keys(): VideoID = Query["z"][0].replace("video", "").split("/")[0]

			elif "clip" in link:
				VideoID = link.split("?")[0].split("/")[-1].replace("clip", "")
			
		if site == "rutube":
			URL = link.split("?")[0]
			URL = URL.rstrip("/")
			VideoID = URL.split("/")[-1]

		return VideoID

	def register_file(self, site: str, id: str, quality: str | None, compression: bool, recoding: bool, watermarked: bool, message_id: int, chat_id: int):
		"""
		Добавляет видео из источника с расширенной поддержкой в хранилище.
			site – название сайта;
			id – идентификатор видео;
			quality – качество;
			compression – использовалось ли сжатие при загрузке;
			recoding – указывает, перекодирован ли файл;
			watermarked – содержит ли видео водяной знак;
			message_id – идентификатор сообщения с файлом;
			chat_id – идентификатор чата с сообщением.
		"""

		if site not in [Support.value for Support in ExtendedSupport]: return

		Path = f"{self.__StorageDirectory}/Files/{site}"
		if not os.path.exists(Path): os.makedirs(Path)
		File = {
			"video": [],
			"watermarked": [],
			"audio": {
				"message_id": None,
				"chat_id": None
			},
			"recoded_audio": {
				"message_id": None,
				"chat_id": None
			}
		}

		if os.path.exists(f"{Path}/{id}.json"): File = ReadJSON(f"{Path}/{id}.json")

		if quality == "audio":

			if recoding: 
				File["recoded_audio"]["message_id"] = message_id
				File["recoded_audio"]["chat_id"] = chat_id

			else:
				File["audio"]["message_id"] = message_id
				File["audio"]["chat_id"] = chat_id

		elif watermarked and self.__SearchFormat(File, quality, compression, recoding, watermarked) == None:
			Format = {
				"quality": quality,
				"compression": compression,
				"recoding": recoding,
				"message_id": message_id,
				"chat_id": chat_id
			}
			File["watermarked"].append(Format)

		elif self.__SearchFormat(File, quality, compression, recoding, watermarked) == None:
			Format = {
				"quality": quality,
				"compression": compression,
				"recoding": recoding,
				"message_id": message_id,
				"chat_id": chat_id
			}
			File["video"].append(Format)

		WriteJSON(f"{Path}/{id}.json", File)

	def save_info(self, site: str, id: str | None, info: dict):
		"""
		Сохраняет данные видео, если поддерживается.
			site – название сайта;
			id – идентификатор видео;
			info – словарь данных.
		"""

		if id:
			SaveDirectory = f"{self.__StorageDirectory}/Info/{site}"
			if not os.path.exists(SaveDirectory): os.makedirs(SaveDirectory)
			WriteJSON(f"{SaveDirectory}/{id}.json", info)

	def upload_file(self, user_id: int, site: str, filename: str, quality: str, compression: bool, recoding: bool, watermarked: bool = False, name: str | None = None, clear: bool = True) -> bool:
		"""
		Выгружает файл в Telegram.
			user_id – идентификатор пользователя;\n
			site – название сайта;\n
			filename – название файла;\n
			quality – качество видео;\n
			compression – указывает, нужно ли использовать сжатие;\n
			recoding – указывает, перекодирован ли файл;\n
			watermarked – указывает, имеет ли видео водяной знак;\n
			name – новое название файла;\n
			clear – очищать ли директорию.
		"""

		IsSuccess = False
		PythonMinorVersion = sys.version_info[1]
		compression = "-c" if compression else ""
		recoding = "-r" if recoding else ""
		watermarked = "-w" if watermarked else ""
		Venv = ". .venv/bin/activate &&" if self.__Venv else ""
		Filetype = filename.split(".")[-1]
		name = f"--name \"{self.__StringToFilename(name)}.{Filetype}\"" if name else ""
		Result = os.system(f"{Venv} python3.{PythonMinorVersion} main.py upload --user {user_id} --site {site} --file {filename} --quality \"{quality}\" {name} {compression} {recoding} {watermarked}")
		if Result == 0: IsSuccess = True

		Folder = f"Temp/{user_id}/{quality}"

		if clear and os.path.exists(Folder):
			RemoveDirectoryContent(Folder)
			os.rmdir(Folder)

		return IsSuccess
	
	def wait_file_uploading(self, site: str, id: str, quality: str, compression: bool, recoding: bool, watermarked: bool = False, timeout: int = 10) -> ExecutionStatus:
		"""
		Ждёт загрузки файла и возвращает идентификатор сообщения с ним.
			site – название сайта;
			id – идентификатор видео;
			quality – качество;
			compression – использовалось ли сжатие при загрузке;
			recoding – указывает, перекодирован ли файл;
			watermarked – имеет ли видео водяной знак;
			timeout – время ожидания в секундах.
		"""

		Try = 0
		Status = ExecutionStatus()
		Status.code = -1

		while Try < timeout and Status.code != 0:
			Try += 1
			Result = self.get_file_message_id(site, id, quality, compression, recoding, watermarked)

			if not Result[0]:
				sleep(1)

			else:
				Status.code = 0
				Status["chat_id"] = Result[0]
				Status["message_id"] = Result[1]	

		return Status