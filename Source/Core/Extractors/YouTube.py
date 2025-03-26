from .Base import BaseExtractor

class YouTube(BaseExtractor):

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._UseCookies()

	def audio(self, path: str) -> bool:
		"""
		Получает аудиодорожку из видеоролика. Возвращает состояние успеха.
			path – путь для сохранения файла.
		"""

		Parameters = [
			f"-o \"{path}\"",
			"--format ba[ext=m4a]/ba[ext=mp4]/bestaudio"
		]
		if self._Recoding: Parameters.append("--recode m4a")

		return not bool(self._ExecuteYtDlpCommand(Parameters))

	def video(self, path: str, format_id: str) -> bool:
		"""
		Скачивает видеоролик. Возвращает состояние успеха.
			path – путь для сохранения файла;\n
			format – идентификатор формата.
		"""

		Parameters = [
			f"-o \"{path}\"",
			f"--format {format_id}+ba[ext=m4a]/ba[ext=mp4]/bestaudio"
		]
		if self._Recoding: Parameters.append("--recode mp4")

		return not bool(self._ExecuteYtDlpCommand(Parameters))