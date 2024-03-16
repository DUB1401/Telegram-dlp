from telethon.sync import TelegramClient
from Source.MediaCore import MediaCore

import os

class Registrator:
	
	def __init__(self):
		
		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Временный клиент.
		self.Client = None
		# Хеш клиента.
		self.Hash = None

	def login(self, PhoneNumber: str, ApiID: int | str, ApiHash: str, Code: str | None = None) -> int:
		# Состояние: код завершения.
		ExitCode = 1
		# Инициализация медиа-ядра.
		MediaCoreObject = MediaCore()
		
		try:
	
			# Если клиент не инициализирован.
			if self.Client == None:
				# Создание клиента и подключение.
				self.Client = TelegramClient("Account", int(ApiID), ApiHash, system_version = "4.16.30-vxCUSTOM")
				self.Client.connect()
		
			# Если код указан, выполнить с ним авторизацию.
			if Code != None: self.Client.sign_in(PhoneNumber, Code, phone_code_hash = self.Hash)
			
			# Если аккаунт не авторизован.
			if self.Client.is_user_authorized() == False:
				# Отправка кода 2FA.
				self.Hash = self.Client.sign_in(PhoneNumber).phone_code_hash
				# Изменение кода.
				ExitCode = -1
				
			else:
				# Сохранение сессии.
				MediaCoreObject.set_session("Account.session", ApiID, ApiHash)
				# Отключение и обнуление клиента и хэша.
				self.Client.disconnect()
				self.Client = None
				self.Hash = None
				# Если файл сессии остался, удалить.
				if os.path.exists("Account.session"): os.remove("Account.session")
				# Изменение кода.
				ExitCode = 0
			
		except: pass
			
		return ExitCode