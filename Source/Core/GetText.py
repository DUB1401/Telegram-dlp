import gettext

class GetText:
	"""Абстракция обращений к PO файлам."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	METHOD = gettext.gettext
	DOMAIN = None
	LANGUAGES = None
	PATH = None

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def initialize(domain: str, languages: list[str] | str, path: str | None = None):
		"""
		Инициализирует.
			domain – домен перевода;\n
			languages – список требуемых языков;\n
			path – путь к каталогу с PO файлами.
		"""

		#---> Проверка переданных аргументов.
		#==========================================================================================#
		if type(languages) == str: languages = [languages]

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		GetText.DOMAIN = domain
		GetText.LANGUAGES = languages
		GetText.PATH = path or "Locales"

		try: GetText.METHOD = gettext.translation(GetText.DOMAIN, GetText.PATH, languages = GetText.LANGUAGES).gettext
		except FileNotFoundError: pass

	def gettext(message: str, languages: list[str] | str = None) -> str:
		"""
		Возвращает локализованную строку в контексте заданного языка.
			message – оригинальная строка.
		"""
		
		if languages:
			if type(languages) == str: languages = [languages]

			try: return gettext.translation(GetText.DOMAIN, GetText.PATH, languages = languages).gettext(message)
			except FileNotFoundError: return message

		else: return GetText.METHOD(message)
	
_ = GetText.gettext