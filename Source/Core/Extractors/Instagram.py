from .Base import BaseExtractor

import json
import os

class Instagram(BaseExtractor):

	def audio(self, path: str) -> bool:
		"""
		Получает аудиодорожку из видеоролика. Возвращает состояние успеха.
			path – путь для сохранения файла.
		"""

		Parameters = [
			f"-o \"{path}\"",
			"--extract-audio",
			"--cookies yt-dlp/instagram.cookies"
		]
		if self._Recoding: Parameters.append("--recode m4a")

		return not bool(self._ExecuteYtDlpCommand(Parameters))

	def info(self) -> dict | None:
		"""Получает словарь данных видео."""

		Info = None

		for Try in range(2):
			Parameters = [
				"--dump-json",
				"--quiet",
				"--no-warnings",
				"--skip-download",
				"--cookies yt-dlp/instagram.cookies"
			]
			Dump = self._GetYtDlpOutput(Parameters)
			
			if not Dump.startswith("ERROR"):
				if "\n" in Dump: Dump = Dump.split("\n")[0]
				Info = json.loads(Dump)
			
			if Info: break
			elif Try == 0 and self._Config.check_key("cookies_generator"): os.system(self._Config["cookies_generator"])

		return Info

	def video(self, path: str, format_id: str) -> bool:
		"""
		Скачивает видеоролик. Возвращает состояние успеха.
			path – путь для сохранения файла;\n
			format – идентификатор формата.
		"""

		Parameters = [
			f"-o \"{path}\"",
			f"--format {format_id}+bestaudio",
			"--cookies yt-dlp/instagram.cookies"
		]
		if self._Recoding: Parameters.append("--recode mp4")

		return not bool(self._ExecuteYtDlpCommand(Parameters))