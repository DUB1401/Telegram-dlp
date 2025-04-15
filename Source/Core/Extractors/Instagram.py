from .Base import BaseExtractor

import json
import os

class Instagram(BaseExtractor):

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
			"--extract-audio"
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
				"--skip-download"
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
			"--no-playlist"
		]

		if self._Recoding:
			Encoder = "libopenh264"
			if self._Config.check_key("libx264") and self._Config["libx264"]: Encoder = "libx264"

			RecodeCommand = [
				"ffmpeg",
				"-i", f"\'{path}\'",
				"-c:v", Encoder,
				"-preset", "ultrafast",
				"-c:a", "aac",
				"-b:a", "128k",
				"-movflags", "+faststart",
				f"\'{path}.mp4\'"
			]

			CleanCommand = [
				"&&",
				"rm", f"\'{path}\'",
				"&&",
				"mv", f"\'{path}.mp4\'", f"\'{path}\'"
			]

			Command = " ".join(RecodeCommand + CleanCommand)
			Parameters.append(f"--exec \"{Command}\"")

		return not bool(self._ExecuteYtDlpCommand(Parameters))