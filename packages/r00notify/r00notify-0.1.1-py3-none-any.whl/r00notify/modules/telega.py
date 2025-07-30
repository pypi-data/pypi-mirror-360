from .interfaces.isender import ISender
import telebot



class Telega(ISender):
    def __init__(self, token, type_msg="message", chat_id = "349447507"):
        """
        :param token: содержиться в r00secret
        :param type_msg: message или photo
        :param chat_id: ???
        """
        self.token = token
        self.type_msg = type_msg
        self.chat_id = chat_id
        self.api = telebot.TeleBot(self.token)

    def send(self, message: str):
        """
        Отправка сообщения в свой канал
        :param message: Сообщение или путь к файлу которое будет отправлено в телеграм
        :return:
        """
        if self.type_msg == "message":
            self.api.send_message(self.chat_id, text=message)
        else:
            with open(message, 'rb') as f:
                self.api.send_photo(chat_id=self.chat_id, photo=f)
