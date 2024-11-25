from urllib.parse import urlparse, parse_qs, urlencode
from dublib.Methods.JSON import ReadJSON, WriteJSON
from dublib.Engine.Bus import ExecutionStatus
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

	def __init__(self, directory: str, venv: bool = True):
		"""
		Хранилище данных медиа-файлов.
			directory – путь к директории хранения;
			venv – указывает, используется ли вирутальная среда Python.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		self.__StorageDirectory = directory
		self.__Venv = venv

	def check_for_playlist(self, site: str, link: str) -> bool:
		"""
		Проверяет, ведёт ли ссылка на плейлист.
			site – домен обрабатываемого сайта;\n
			link – ссылка.
		"""

		IsPlaylist = False

		match site:

			case "youtube.com":
				if "/playlist?list" in link: IsPlaylist = True

		return IsPlaylist

	def check_link(self, site: str, link: str) -> str:
		"""
		Проверяет, нужно ли ссылке преобразования для корректной загрузке и выполняет эту процедуру.
			site – домен обрабатываемого сайта;\n
			link – ссылка.
		"""

		match site:
		
			case "instagram.com":

				if "/s/" in link:
					Buffer = link.split("?")[0].split("/")[-1]
					
					if not Buffer.isdigit():
						link = "https://www.instagram.com/stories/highlights/" + str(base64.b64decode(Buffer)).split(":")[-1].rstrip("'")

			case "youtube.com":
				if "&list=" in link: link = self.__RemoveQueryParameter(link, "list")

		return link

	def get_file_message_id(self, site: str, id: str, quality: str, compression: bool, recoding: bool, watermarked: bool = False) -> list[int, None]:
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

	def parse_site_name(self, link: str) -> str:
		"""
		Получает название сайта из ссылки.
			link – ссылка.
		"""

		Site = None

		try:
			Site = urlparse(link).hostname.replace("www.", "")
			if Site == "youtu.be": Site = "youtube.com"
			if Site == "vt.tiktok.com": Site = "tiktok.com"
			if Site == "vm.tiktok.com": Site = "tiktok.com"
			if "pornhub.com" in Site: Site = "pornhub.com"
			
		except: pass
		
		return Site
	
	def parse_video_id(self, site: str, link: str) -> str | None:
		"""
		Получает идентификатор видео из ссылки, если сохранение данных видео из источника поддерживается.
			site – название сайта;
			link – ссылка.
		"""

		VideoID = None

		if site == "instagram.com":

			if "/reel/" in link:
				VideoID = link.split("?")[0].rstrip("/").split("/")[-1]

		if site == "youtube.com":

			if "youtube.com" in link and "/shorts/" in link:
				VideoID = link.split("/shorts/")[-1].split("?")[0]

			elif "youtube.com" in link:
				Query = urlparse(link).query
				Query = parse_qs(Query)
				if "v" in Query.keys(): VideoID = Query["v"][0]

			elif "youtu.be" in link:
				VideoID = link.split("?")[0].split("/")[-1]

		if site == "tiktok.com":
			Buffer = link.split("?")[0].split("/")[-1]
			if Buffer.isdigit(): VideoID = Buffer

		if site == "vk.com":
			
			if "video" in link:
				Query = urlparse(link).query
				Query = parse_qs(Query)
				if "z" in Query.keys(): VideoID = Query["z"][0].replace("video", "").split("/")[0]

			elif "clip" in link:
				VideoID = link.split("?")[0].split("/")[-1].replace("clip", "")
			
		return VideoID

	def register_file(self, site: str, id: str, quality: str | None, compression: bool, recoding: bool, watermarked: bool, message_id: int, chat_id: int):
		"""
		Добавляет видео в хранилище.
			site – название сайта;
			id – идентификатор видео;
			quality – качество;
			compression – использовалось ли сжатие при загрузке;
			recoding – указывает, перекодирован ли файл;
			watermarked – содержит ли видео водяной знак;
			message_id – идентификатор сообщения с файлом;
			chat_id – идентификатор чата с сообщением.
		"""

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

	def upload_file(self, user_id: int, site: str, filename: str, quality: str, compression: bool, recoding: bool, watermarked: bool = False, name: str | None = None) -> bool:
		"""
		Выгружает файл в Telegram.
			user_id – идентификатор пользователя;
			site – название сайта;
			filename – название файла;
			quality – качество видео;
			compression – указывает, нужно ли использовать сжатие;
			recoding – указывает, перекодирован ли файл;
			watermarked – указывает, имеет ли видео водяной знак;
			name – новое название файла.
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
		Status = ExecutionStatus(-1)

		while Try < timeout and Status.code != 0:
			Try += 1
			Result = self.get_file_message_id(site, id, quality, compression, recoding, watermarked)

			if not Result[0]:
				sleep(1)

			else:
				Status = ExecutionStatus(0)
				Status["chat_id"] = Result[0]
				Status["message_id"] = Result[1]	

		return Status