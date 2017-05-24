''' Main script _(:з」∠)_'''
#!/usr/bin/python
# -*- coding: utf-8 -*-

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from telegram.ext.filters import Filters
from telegram.bot import Bot
from telegram.chataction import ChatAction
import logging
import config
import actions
import sys
import db


class MemoBot:
    def __init__(self):
        # Setting up bot
        self.updater = Updater(token=config.token)
        self.dispatcher = self.updater.dispatcher
        self.botObj = Bot(token=config.token)
        # Register handlers
        self.dispatcher.add_handler(CommandHandler('start', actions.start))
        # Add memo ,long version.
        add_memo_handler = ConversationHandler(
            entry_points=[CommandHandler('add_memo', actions.add_memo,pass_args=True,pass_chat_data=True)],
            states={actions.QUICK: [MessageHandler(Filters.text,
                                                actions.add_quick,
                                                pass_chat_data=True)],
                    actions.CONTENT: [MessageHandler(Filters.text,
                                                actions.add_content,
                                                pass_chat_data=True)],
                    actions.TITLE: [MessageHandler(Filters.text,
                                                actions.add_title,
                                                pass_chat_data=True)],
                    actions.TAG: [MessageHandler(Filters.text,
                                                actions.add_tag,
                                                pass_chat_data=True)]                     
            },
            fallbacks=[CommandHandler('cancel', actions.cancel,pass_chat_data=True)])
        self.dispatcher.add_handler(add_memo_handler)
        self.dispatcher.add_handler(CommandHandler('list', actions.query_list,pass_args=True))
        self.dispatcher.add_handler(CommandHandler('test', actions.test))  
        self.dispatcher.add_handler(CommandHandler('get', actions.query,pass_args=True))  
        self.dispatcher.add_handler(CommandHandler('delete', actions.delete,pass_args=True))  
        self.dispatcher.add_handler(CommandHandler('restart', actions.restart)) 
        self.dispatcher.add_handler(CommandHandler('update', actions.upgrade))                                                             
        self.dispatcher.add_handler(MessageHandler(lambda update: update.text and update.text.startswith('#'),actions.query_hashtag))  
    def start(self):
        self.updater.start_polling()

    def __str__(self):
        return str(self.botObj)
        
if __name__=="__main__":
    # import bot components
    try:
        import config
    except ImportError:
        print("Please create config file 'config.py' first.")
        exit(1)
    logging.basicConfig(stream=sys.stderr,format='%(message)s',level=logging.DEBUG)
    bot=MemoBot()
    bot.start()
