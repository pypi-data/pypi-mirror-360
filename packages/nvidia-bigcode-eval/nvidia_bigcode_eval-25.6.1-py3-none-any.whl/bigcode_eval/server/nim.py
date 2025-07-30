"""
NIM completion and NIM chat completion classes
"""
from bigcode_eval.server.base_server import BaseOpenAiServer
from bigcode_eval.server.openai_messages_handlers import ChatCompletionHandler, CompletionHandler

class NIMCompletion(BaseOpenAiServer):
    @property
    def message_handler(self):
        return CompletionHandler
    

class NIMChat(BaseOpenAiServer):
    @property
    def message_handler(self):
        return ChatCompletionHandler
