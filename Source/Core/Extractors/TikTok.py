from .Base import BaseExtractor

class TikTok(BaseExtractor):

	def info(self) -> dict | None:
		"""Получает словарь данных видео."""

		Info = super().info()

		if type(Info) == dict: 
			Formats: list = Info["formats"]

			for Format in list(Formats):
				Format: str
				if Format["format_id"].endswith("-2"): Formats.remove(Format)

			Info["formats"] = Formats
			Info["formats"][0]["resolution"] = "480x720"

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