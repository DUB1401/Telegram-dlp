from . import ExtendedSupport

class Parameters:
	"""Контейнер параметров источника."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def proxy(self) -> str | None:
		"""Прокси-сервер."""

		return self.__Data["proxy"]
	
	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __CheckImportantParameters(self):
		"""Проверяет наличие обязательных параметров и задаёт их базовые значения в случае отсутствия."""

		ImportantParameters = {
			"proxy": None
		}

		for Key in ImportantParameters.keys():
			if Key not in self.__Data.keys(): self.__Data[Key] = ImportantParameters[Key]

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, data: dict):
		"""
		Контейнер параметров источника.
			data – словарь параметров.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Data = data

		self.__CheckImportantParameters()

	def __getitem__(self, key: str) -> any:
		"""
		Возвращает значение параметра.
			key – ключ параметра.
		"""

		return self.__Data[key]
		
class Configurator:
	"""Опциональные параметры источников контента."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseConfigs(self):
		"""Парсит конфигурации в объекты."""
		
		for Domain in [Element.value for Element in ExtendedSupport]:
			Buffer = dict()
			if Domain in self.__Data.keys(): Buffer = self.__Data[Domain]
			self.__Configs[Domain] = Parameters(Buffer)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, configs: dict):
		"""
		Опциональные параметры источников контента.
			configs – словарь конфигураций.
		"""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Data = configs.copy()

		self.__Configs: dict[str, Parameters] = dict()

		self.__ParseConfigs()

	def __getitem__(self, domain: ExtendedSupport | str) -> Parameters:
		"""Возвращает контейнер параметров источника."""

		if type(domain) == str: domain = ExtendedSupport(domain)
		
		return self.__Configs[domain.value]