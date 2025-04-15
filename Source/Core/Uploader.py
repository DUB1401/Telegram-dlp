from Source.Core.Storage import Storage
from Source.Core.YtDlp import YtDlp

from dublib.TelebotUtils.Users import UserData

class Uploader:
	"""Ступенчатый выгрузчик видео."""

	def __init__(self, downloader: YtDlp, storage: Storage):

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Downloader = downloader
		self.__Storage = storage

	def download_video(self, user: UserData, link: str, info: dict, quality: str):
		"""
		Запускает процесс скачивания видео с последующей выгрузкой.
			user – данные пользователя;\n
			link – ссылка на видео;\n
			video_id – идентификатор видео;\n
			info – словарь данных видео;\n
			quality – название качества видео.
		"""

		try:
			Resolutions = self.__Downloader.get_resolutions(info)
			if quality not in Resolutions.keys(): return
			FormatID = Resolutions[quality]

			if not user.get_property("option_storage"): return
			Recoding = user.get_property("option_recoding")
			Compression = user.get_property("option_compression")
			Site = user.get_property("site")
			Name = user.get_property("filename")
			VideoID = info["id"]

			FileData = self.__Storage.get_file_message_id(Site, VideoID, quality, Compression, Recoding)
			if None not in FileData: return

			Filename = self.__Downloader.download_video(link, f"Temp/{user.id}/{quality}", VideoID, FormatID, recoding = Recoding)
			if not Filename: return

			if not self.__Storage.upload_file(user.id, Site, Filename, quality, Compression, Recoding, name = Name, clear = False): return

			Result = self.__Storage.wait_file_uploading(Site, VideoID, quality, Compression, Recoding)
			if Result.code == 0: return

		except: pass