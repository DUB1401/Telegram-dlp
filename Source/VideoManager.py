import subprocess
import json
import sys
import os

class VideoManager:

	def __init__(self, Settings: dict):
		self.__Settings = Settings.copy()
	
	def download(self, link: str, user_id: int | str, original_filename: bool) -> dict | None:
		# Результат выполнения.
		Result = None
		# Установка прокси.
		Proxy = " --proxy " + self.__Settings["proxy"] if self.__Settings["proxy"] else ""
		# Если каталог пользователя отсутствует, создать его.
		if not os.path.exists(f"Files/{user_id}"): os.makedirs(f"Files/{user_id}")
		# Определения исполняемых команд.
		Execs = {
			 "linux": "python3." + str(sys.version_info[1]) +  f" yt-dlp/yt-dlp \"{link}\" --dump-json --quiet --no-warnings --recode-video mp4{Proxy}",
			 "win32": f"yt-dlp\\yt-dlp.exe {link} --dump-json --quiet --no-warnings --recode-video mp4{Proxy}"
		}
		
		# Скачивание видео.
		Result = subprocess.getoutput(Execs[sys.platform])
		
		try:
			# Если нет ошибки скачивания, спарсить дамп видео.
			if not Result.startswith("ERROR"): Result = json.loads(Result)
			# Выбор имени файла: оригинальное или ID.
			Filename = Result["title"].strip() if original_filename else Result["id"]
			# Выполнение скачивания.
			print(Execs[sys.platform].replace("--dump-json ", "") + f" -o \"Files/{user_id}/{Filename}.mp4\"")
			ExitCode = os.system(Execs[sys.platform].replace("--dump-json ", "") + f" -o \"Files/{user_id}/{Filename}.mp4\"")
			# Если скачивание неуспешно, обнулить дампирование.
			if ExitCode != 0: Result = None
		
		except:
			# Обнуление результата.
			Result = None
		
		return Result
	
	def dump(self, filename: str, user_id: str, compression: bool, premium: bool = False) -> int:
		# Определения исполняемых команд.
		Execs = {
			 "linux": "python3." + str(sys.version_info[1]) + f" main.py dump \"Files/{user_id}/{filename}.mp4\" {user_id}",
			 "win32": f"python main.py dump \"Files\\{user_id}\\{filename}.mp4\" {user_id}"
		}
		# Расчёт лимита.
		Limit = 3800000000 if premium else 1900000000
		# Код завершения.
		ExitCode = 1
		
		try:
			
			# Если размер файла позволительный.
			if os.path.getsize(f"Files/{user_id}/{filename}.mp4") < Limit:
				# Выполнение загрузки.
				ExitCode = os.system(Execs[sys.platform] + (" -compress" if compression else ""))
		
			else:
				# Изменение кода.
				ExitCode = -1

			# Удаление файла.
			if os.path.exists(f"Files/{user_id}/{filename}.mp4"): os.remove(f"Files/{user_id}/{filename}.mp4")
			
		except: pass
		
		return ExitCode