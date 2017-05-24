#!/usr/bin/python3
from telegram import ReplyKeyboardMarkup,ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.bot import Bot
from telegram.chataction import ChatAction
from telegram.error import TelegramError
from telegram.ext import Updater,CommandHandler,MessageHandler,ConversationHandler,CallbackQueryHandler
import config
import db
import helpers
import os
import subprocess
import sys
import time

# status code in add memo
QUICK, CONTENT, TITLE, TAG, CONFIRM = range(5)
confirm_keyboard = [['看起来不错 🤣'],['等等好像标题不对 😂'],['等等好像内容不对 😂'],['等等好像标签不对 😂']]

def start(bot,update):
    '''resopnse /start'''
    bot.sendMessage(chat_id=update.message.chat_id,text="这只是个简单的小备忘录 bot 呗~")

@helpers.admin_required
def test(bot,update):
   update.message.reply_text("真是的，汝惊慌失措时的样子还比较可爱呐。")
    

def add_memo(bot, update, chat_data, args):
    '''add a memo'''
    chat_data['channel'] = update.message.chat.id
    chat_data['author'] = update.message.from_user.id
    chat_data['refuse_level'] = 3
    if args:
        update.message.reply_text("想让咱记些啥？第一行就让咱拿去当作标题了呗~")
        chat_data['tag']=args[0]
        return QUICK
    else:
        update.message.reply_text("想让咱记些啥？")
        return CONTENT

def summary(update,chat_data):
    '''preview memo'''
    display(update,chat_data,prefix='😋 嗯，汝写了这些:\n',
            reply_markup=ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True))
        
def display(update,chat_data,prefix='',**args):
    update.message.reply_text('{}#{}\n{}\n{}'.format(prefix,chat_data['tag'],chat_data['title'],chat_data['content']),**args)

def view(update,chat_data):
    display(update,chat_data)

@helpers.current_conversation
def add_quick(bot, update, chat_data):
    '''add memo quickly'''
    title = update.message.text.split("\n",1)[0]
    text = update.message.text.replace(title,"").lstrip()
    chat_data['content'] = text
    chat_data['title'] = title
    success(bot,update,chat_data)
    return ConversationHandler.END

@helpers.current_conversation
def add_content(bot, update, chat_data):
    '''ask a memo step 1'''
    text = update.message.text
    chat_data['content'] = text
    update.message.reply_text('😋 OK，接下来起个标题呗~')
    return TITLE

@helpers.current_conversation
def add_title(bot, update, chat_data):
    '''ask a memo step 2'''
    text = update.message.text
    chat_data['title'] = text
    update.message.reply_text('😋 OK，接下来贴个标签呗~（一个词就好啦）')
    return TAG

@helpers.current_conversation
def add_tag(bot, update, chat_data):
    '''ask a memo step 3'''
    text = update.message.text
    chat_data['tag'] = text
    success(bot,update,chat_data)
    return ConversationHandler.END

def terminate(update,chat_data):
    ''' _(:з」∠)_'''
    update.message.reply_text("汝是咱的什么人啊……不对，咱是汝的什么人啊？",reply_markup=ReplyKeyboardRemove())
    chat_data.clear()

def success(bot,update,chat_data):
    config.dbc.log_memo(channel=chat_data['channel'], author=chat_data['author'], 
                     title=chat_data['title'], tag=chat_data['tag'], memo=chat_data['content'])
    chat_data.clear()
    update.message.reply_text("咱就这么记下了呗~",reply_markup=ReplyKeyboardRemove())    

def cancel(bot, update,chat_data):
    update.message.reply_text("😒 真是个有始无终的家伙……",reply_markup=ReplyKeyboardRemove())
    chat_data.clear()
    return ConversationHandler.END

def query_channel(channel):
    return config.dbc.Query(db.ChatMemo).filter_by(channel=channel)

def query_list(bot,update,args):
    memos = [memo.jsonify() for memo in query_channel(channel=update.message.chat.id).all()]
    if not memos:
        update.message.reply_text("😋 啥都没有~")
        return
    try:
        memos = memos[:int(args[0])]
    except (IndexError,TypeError):
        pass
    memos_texts = "\n".join(["#{}:{}".format(item['tag'],item['title']) for item in memos])
    update.message.reply_text("{}\n用 /get <标签名称> 获得备忘的详细信息呗~".format(memos_texts))

def query_hashtag(bot,update):
    args=[update.message.text[1:]]
    query(bot,update,args,notice=False)

def query(bot,update,args,notice=True):
    if not args:
        update.message.reply_text("汝在说啥？")
        return
    try:
        memo_item = query_channel(channel=update.message.chat.id).filter_by(tag=args[0]).first().jsonify()
        assert memo_item
    except AssertionError:
        if notice:
            update.message.reply_text("汝有对咱讲过这个？")
    else:
        view(update,memo_item)

def get_author_id(update,memo_id):
    memo_item = query_channel(channel=update.message.chat.id).filter_by(id=memo_id).first().jsonify()
    return memo_item['author']

def get_author_tag(update,tag):
    memo_item = query_channel(channel=update.message.chat.id).filter_by(tag=tag).first().jsonify()
    return memo_item['author']

def delete(bot,update,args,notice=True):
    if not args:
        update.message.reply_text("汝在说哪个？")
        return
    chat_id,user_id = helpers.get_chat(update)
    if not user_id in helpers.get_admin_ids(bot, update, chat_id) + [get_author_tag(update,args[0])]:
        update.message.reply_text("汝是咱的什么人啊……不对，咱是汝的什么人啊？")
        print("Unauthorized access denied for {}.".format(chat_id))
        return
    try:
        memo_item = query_channel(channel=update.message.chat.id).filter_by(tag=args[0]).first().jsonify()
        assert memo_item
    except AssertionError:
        if notice:
            update.message.reply_text("汝有对咱讲过这个？")
    else:
        config.dbc.delete_memo(memo_item['id'])
        update.message.reply_text("交给咱好了 😋")

@helpers.operator_required
def restart(bot, update):
    bot.send_message(update.message.chat_id, "受汝照顾了。")
    time.sleep(0.2)
    os.execl(sys.executable, sys.executable, *sys.argv)

@helpers.operator_required
def upgrade(bot,update):
    try:
        proc=subprocess.Popen(["git","pull"], stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        time.sleep(3)
        bot.sendMessage(chat_id=update.message.chat_id,text="受汝照顾了。")
        os.execl(sys.executable, sys.executable, *sys.argv)
    except subprocess.CalledProcessError:
        bot.sendMessage(chat_id=update.message.chat_id,text="唔，发生了点意外😱")
        bot.sendMessage(chat_id=update.message.chat_id,text=proc.stderr.read())
