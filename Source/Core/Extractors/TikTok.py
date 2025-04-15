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


		if self._Config.check_key("fake_hd") and self._Config["fake_hd"]:
			IsHD = False
			Mini = dict()
			for Format in Info["formats"]: 
				if "width" in Format.keys() and Format["width"] == 576: Mini = Format

				if "width" in Format.keys() and Format["width"] == 720: 
					IsHD = True
					break

			if not IsHD and Mini:
				Mini["resolution"] = "720x1280"
				Info["formats"].append(Mini)

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