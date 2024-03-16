import subprocess
import json
import sys
import os

class VideoManager:
	
	def download(self, link: str, user_id: int | str) -> dict | None:
		# ��������� ����������.
		Result = None
		if not os.path.exists(f"Files/{user_id}"): os.makedirs(f"Files/{user_id}")
		# ����������� ����������� ������.
		Execs = {
			 "linux": f"yt-dlp/yt-dlp {link} -o Files/{user_id}/%(title)s.%(ext)s --dump-json --quiet --no-warnings",
			 "win32": f"yt-dlp\\yt-dlp.exe {link} -o Files\\{user_id}\\%(title)s.%(ext)s --dump-json --quiet --no-warnings"
		}
		# ���������� �����.
		Result = subprocess.getoutput(Execs[sys.platform])
		# ���� ��� ������ ����������, �������� ���� �����.
		if Result.startswith("ERROR") == False: Result = json.loads(Result)
		# ���������� ����������.
		ExitCode = os.system(Execs[sys.platform].replace("--dump-json ", ""))
		# ���� ���������� ���������, �������� ������������.
		if ExitCode != 0: Result = None
		
		return Result
	
	def dump(self, filename: str, user_id: str, compression: bool, premium: bool = False) -> int:
		# ����������� ����������� ������.
		Execs = {
			 "linux": "python3." + str(sys.version_info[1]) + f" main.py dump \"{filename}\" {user_id}",
			 "win32": f"python main.py dump \"{filename}\" {user_id}"
		}
		# ������ ������.
		Limit = 3800000000 if premium else 1900000000
		
		# ���� ������ ����� ��������������.
		if os.path.getsize(filename) < Limit:
			# ���������� ��������.
			ExitCode = os.system(Execs[sys.platform] + (" -compress" if compression else ""))
		
		else:
			# ��������� ����.
			ExitCode = -1

		# �������� �����.
		if os.path.exists(filename): os.remove(filename)
		
		return ExitCode