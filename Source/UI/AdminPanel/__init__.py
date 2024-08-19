from .InlineKeyboards import InlineKeyboards
from .ReplyKeyboards import ReplyKeyboards
from .Mailer import Mailer

from dublib.TelebotUtils import UserData, UsersManager
from telebot import TeleBot, types

import enum

#==========================================================================================#
# >>>>> СТРУКТУРЫ <<<<< #
#==========================================================================================#

class Decorators:
	"""Наборы декораторов."""

	def __init__(self):
		"""Наборы декораторов."""

		pass

	def commands(self, bot: TeleBot, users: UsersManager, password: str):
		"""
		Набор декораторов: команды.
			bot – экземпляр бота;\n
			users – менеджер пользователей;\n
			password – пароль администратора.
		"""

		@bot.message_handler(commands = ["admin"])
		def CommandAdmin(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_property("mailing_caption", None, force = False)
			User.set_property("mailing_content", [], force = False)
			User.set_property("button_label", None, force = False)
			User.set_property("button_link", None, force = False)
			User.set_property("sampling", None, force = False)
			User.set_property("mailing", False, force = False)
			MessageWords = Message.text.split(" ")

			if not User.has_permissions("admin") and len(MessageWords) == 2:
				User.add_permissions("admin")

				if MessageWords[1] == password:
					bot.send_message(
						chat_id = Message.chat.id,
						text = "Пароль принят. Доступ разрешён.",
						reply_markup = ReplyKeyboards().admin()
					)

				else:
					bot.send_message(
						chat_id = Message.chat.id,
						text = "Неверный пароль."
					)

			else:

				if User.has_permissions("admin"):
					bot.send_message(
						chat_id = Message.chat.id,
						text = "Доступ разрешён.",
						reply_markup = ReplyKeyboards().admin()
					)

				else:
					bot.send_message(
						chat_id = Message.chat.id,
						text = "Доступ запрещён."
					)

	def inline_keyboards(self, bot: TeleBot = None, users: UsersManager = None):
		"""
		Набор декораторов: Inline-кнопки.
			bot – экземпляр бота;\n
			users – менеджер пользователей.
		"""

		@bot.callback_query_handler(func = lambda Callback: Callback.data.startswith("sampling"))
		def InlineButton(Call: types.CallbackQuery):
			User = users.auth(Call.from_user)
			if Call.data.endswith("all"): User.set_property("sampling", None)
			if Call.data.endswith("last"): User.set_property("sampling", 1000)
			bot.answer_callback_query(Call.id)
			bot.delete_message(
				chat_id = User.id,
				message_id = Call.message.id
			)

			if not Call.data.endswith("cancel"): bot.send_message(
				chat_id = User.id,
				text = "Выборка установлена.",
				reply_markup = ReplyKeyboards().mailing(User)
			)
				
			else:
				User.set_expected_type(None)

	def photo(self, bot: TeleBot, users: UsersManager):
		"""
		Набор декораторов: фото.
			bot – экземпляр бота;\n
			users – менеджер пользователей.
		"""

		@bot.message_handler(content_types = ["photo"])
		def Photo(Message: types.Message):
			User = users.auth(Message.from_user)

			if User.has_permissions("admin") and User.expected_type == "message":
				if Message.caption: User.set_property("mailing_caption", Message.html_caption)
				User.get_property("mailing_content").append({"type": "photo", "file_id": Message.photo[-1].file_id})

	def reply_keyboards(self, bot: TeleBot, users: UsersManager):
		"""
		Набор декораторов: Reply-кнопки.
			bot – экземпляр бота;\n
			users – менеджер пользователей.
		"""

		@bot.message_handler(content_types = ["text"], regexp = "🎯 Выборка")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_expected_type(UserInput.Sampling.value)
			bot.send_message(
				chat_id = Message.chat.id,
				text = f"*Укажите выборку*\n\nТекущее количество пользователей: {len(users.users)}",
				parse_mode = "MarkdownV2",
				reply_markup = InlineKeyboards().sampling(User)
			)

		@bot.message_handler(content_types = ["text"], regexp = "🕹️ Добавить кнопку")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_expected_type(UserInput.ButtonLabel.value)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Введите подпись для кнопки.",
				reply_markup = ReplyKeyboards().cancel()
			)

		@bot.message_handler(content_types = ["text"], regexp = "✅ Завершить")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_expected_type(None)
			User.clear_temp_properties()
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Сообщение сохранено.",
				reply_markup = ReplyKeyboards().mailing(User)
			)

		@bot.message_handler(content_types = ["text"], regexp = "❌ Закрыть")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Панель управления закрыта.",
				reply_markup = types.ReplyKeyboardRemove()
			)

		@bot.message_handler(content_types = ["text"], regexp = "🟢 Запустить")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_object("mailer", Mailer(bot))
			
			if not User.get_property("mailing_caption") and not User.get_property("mailing_content"):
				bot.send_message(
					chat_id = Message.chat.id,
					text = "Вы не задали сообщение для рассылки."
				)

			else:
				User.get_object("mailer").start_mailing(User, users)

		@bot.message_handler(content_types = ["text"], regexp = "↩️ Назад")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Панель управления.",
				reply_markup = ReplyKeyboards().admin()
			)

		@bot.message_handler(content_types = ["text"], regexp = "❌ Отмена")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_expected_type(None)

			try:
				Caption = User.get_property("temp_mailing_caption")
				Content = User.get_property("temp_mailing_content")
				User.clear_temp_properties()
				User.set_property("mailing_caption", Caption)
				User.set_property("mailing_content", Content)
				
			except: pass

			bot.send_message(
				chat_id = Message.chat.id,
				text = "Действие отменено.",
				reply_markup = ReplyKeyboards().mailing(User)
			)

		@bot.message_handler(content_types = ["text"], regexp = "🔴 Остановить")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_property("mailing", None)

		@bot.message_handler(content_types = ["text"], regexp = "🔎 Просмотр")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			
			if not User.get_property("mailing_caption") and not User.get_property("mailing_content"):
				bot.send_message(
					chat_id = Message.chat.id,
					text = "Вы не задали сообщение для рассылки."
				)

			else:
				Mailer(bot).send_message(User, User)

		@bot.message_handler(content_types = ["text"], regexp = "👤 Рассылка")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Управление рассылкой.",
				reply_markup = ReplyKeyboards().mailing(User)
			)

		@bot.message_handler(content_types = ["text"], regexp = "✏️ Редактировать")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_expected_type(UserInput.Message.value)
			Caption = User.get_property("mailing_caption")
			Content = User.get_property("mailing_content")
			User.set_temp_property("temp_mailing_caption", Caption)
			User.set_temp_property("temp_mailing_content", Content)
			User.set_property("mailing_caption", None)
			User.set_property("mailing_content", [])
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Отправьте сообщение, которое будет использоваться в рассылке.\n\nЕсли вы прикрепляете несколько вложений, для их упорядочивания рекомендуется выполнять загрузку файлов последовательно.",
				reply_markup = ReplyKeyboards().editing()
			)

		@bot.message_handler(content_types = ["text"], regexp = "📊 Статистика")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			PremiumUsersCount = len(users.premium_users)
			UsersCount = len(users.users)
			BlockedUsersCount = 0

			for user in users.users:
				if user.is_chat_forbidden: BlockedUsersCount += 1

			bot.send_message(
				chat_id = Message.chat.id,
				text = f"*📊 Статистика*\n\n👤 Всего пользователей: {UsersCount}\n⭐ Из них Premium: {PremiumUsersCount}\n⛔ Заблокировали: {BlockedUsersCount}",
				parse_mode = "MarkdownV2"
			)

		@bot.message_handler(content_types = ["text"], regexp = "🕹️ Удалить кнопку")
		def Button(Message: types.Message):
			User = users.auth(Message.from_user)
			User.set_property("button_label", None)
			User.set_property("button_link", None)
			bot.send_message(
				chat_id = Message.chat.id,
				text = "Кнопка удалена.",
				reply_markup = ReplyKeyboards().mailing(User)
			)

class Keyboards:
	"""Контейнер разметок кнопок."""

	@property
	def inline(self) -> types.InlineKeyboardMarkup:
		"""Inline-разметки кнопок."""

	@property
	def reply(self) -> types.ReplyKeyboardMarkup:
		"""Reply-разметки кнопок."""

	def __init__(self):
		"""Контейнер разметок кнопок."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Inline = InlineKeyboards()
		self.__Reply = ReplyKeyboards()

class Procedures:
	"""Наборы процедур."""

	def __init__(self):
		"""Наборы процедур."""

		pass

	def text(self, bot: TeleBot, user: UserData, message: types.Message) -> bool:
		"""
		Набор процедур: текст.
			bot – экземпляр бота;\n
			user – пользователь;\n
			message – сообщение.
		"""

		if user.has_permissions("admin") and user.expected_type:

			if user.expected_type == UserInput.Message.value:
				user.set_property("mailing_caption", message.html_text)

				return True

			if user.expected_type == UserInput.ButtonLabel.value:
				user.set_property("button_label", message.text)
				user.set_expected_type(UserInput.ButtonLink.value)
				bot.send_message(
					chat_id = message.chat.id,
					text = "Отправьте ссылку, которая будет помещена в кнопку.",
					reply_markup = ReplyKeyboards().cancel()
				)

				return True
			
			if user.expected_type == UserInput.ButtonLink.value:
				user.set_property("button_link", message.text)
				user.set_expected_type(None)
				bot.send_message(
					chat_id = message.chat.id,
					text = "Кнопка прикреплена к сообщению.",
					reply_markup = ReplyKeyboards().mailing(user)
				)

				return True

	def files(self, bot: TeleBot, user: UserData = None, message: types.Message = None):
		"""
		Набор процедур: файлы.
			bot – экземпляр бота;\n
			message – сообщение;\n
			user – пользователь.
		"""

		if user.has_permissions("admin") and user.expected_type == UserInput.Message.value:
			if message.caption: user.set_property("mailing_caption", message.html_caption)
			if message.content_type == "audio": user.get_property("mailing_content").append({"type": "audio", "file_id": message.audio.file_id})
			elif message.content_type == "document": user.get_property("mailing_content").append({"type": "document", "file_id": message.document.file_id})
			elif message.content_type == "video": user.get_property("mailing_content").append({"type": "video", "file_id": message.video.file_id})
			elif message.content_type == "photo": user.get_property("mailing_content").append({"type": "photo", "file_id": message.photo[-1].file_id})

class UserInput(enum.Enum):
	ButtonLabel = "button_label"
	ButtonLink = "button_link"
	Message = "message"
	Sampling = "sampling"

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Panel:
	"""Панель управления."""

	@property
	def decorators(self) -> Decorators:
		"""Наборы декораторов."""

		return self.__Decorators

	@property
	def keyboards(self) -> Keyboards:
		"""Наборы разметок кнопок."""

		return self.__Keyboards
	
	@property
	def procedures(self) -> Procedures:
		"""Наборы процедур."""

		return self.__Procedures

	def __init__(self):
		"""Панель управления."""

		#---> Генерация динамических атрибутов.
		#==========================================================================================#
		self.__Decorators = Decorators()
		self.__Keyboards = Keyboards()
		self.__Procedures = Procedures()