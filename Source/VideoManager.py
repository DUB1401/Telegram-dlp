import subprocess
import json
import sys
import os

class VideoManager:
	
	def download(self, link: str, user_id: int | str) -> dict | None:
		# Результат выполнения.
		Result = None
		if not os.path.exists(f"Files/{user_id}"): os.makedirs(f"Files/{user_id}")
		# Определения исполняемых команд.
		Execs = {
			 "linux": f"yt-dlp/yt-dlp {link} -o Files/{user_id}/%(title)s.%(ext)s --dump-json --quiet --no-warnings",
			 "win32": f"yt-dlp\\yt-dlp.exe {link} -o Files\\{user_id}\\%(title)s.%(ext)s --dump-json --quiet --no-warnings"
		}
		# Скачивание видео.
		Result = subprocess.getoutput(Execs[sys.platform])
		# Если нет ошибки скачивания, спарсить дамп видео.
		if Result.startswith("ERROR") == False: Result = json.loads(Result)
		# Выполнение скачивания.
		ExitCode = os.system(Execs[sys.platform].replace("--dump-json ", ""))
		# Если скачивание неуспешно, обнулить дампирование.
		if ExitCode != 0: Result = None
		
		return Result
	
	def dump(self, filename: str, user_id: str, compression: bool, premium: bool = False) -> int:
		# Определения исполняемых команд.
		Execs = {
			 "linux": "python3." + str(sys.version_info[1]) + f" main.py dump \"{filename}\" {user_id}",
			 "win32": f"python main.py dump \"{filename}\" {user_id}"
		}
		# Расчёт лимита.
		Limit = 3800000000 if premium else 1900000000
		
		# Если размер файла позволительный.
		if os.path.getsize(filename) < Limit:
			# Выполнение загрузки.
			ExitCode = os.system(Execs[sys.platform] + (" -compress" if compression else ""))
		
		else:
			# Изменение кода.
			ExitCode = -1

		# Удаление файла.
		if os.path.exists(filename): os.remove(filename)
		
		return ExitCode