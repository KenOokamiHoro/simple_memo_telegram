import config
import mwt
from functools import wraps

def admin_required(func):
    @wraps(func)
    def wrapped(bot, update,*args, **kwargs):
        chat_id,user_id=get_chat(update)
        if not user_id in get_admin_ids(bot, update, chat_id):
            update.message.reply_text("汝是咱的什么人啊……不对，咱是汝的什么人啊？")
            print("Unauthorized access denied for {}.".format(chat_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

def current_conversation(func):
    @wraps(func)
    def wrapped(bot, update, chat_data,*args, **kwargs):
        chat_id,user_id=get_chat(update)
        if str(user_id) != str(chat_data['author']):
            return
        return func(bot, update, chat_data, *args, **kwargs)
    return wrapped

def operator_required(func):
    @wraps(func)
    def wrapped(bot, update,*args, **kwargs):
        chat_id,user_id=get_chat(update)
        if not str(user_id) in config.operators:
            update.message.reply_text("汝认为所有人都要遵循汝的常识是吗？")
            print("Unauthorized access denied for {}.".format(chat_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


@mwt.MWT(timeout=60*60)
def get_admin_ids(bot, update, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    if update.message.from_user.id == chat_id:
        return [chat_id,]
    else:
        return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

def get_chat(update):
    # extract user_id from arbitrary update
    chat_id = update.message.chat_id
    try:
        user_id = update.message.from_user.id
    except (NameError, AttributeError):
        try:
            user_id = update.inline_query.from_user.id
        except (NameError, AttributeError):
            try:
                user_id = update.chosen_inline_result.from_user.id
            except (NameError, AttributeError):
                try:
                    user_id = update.callback_query.from_user.id
                except (NameError, AttributeError):
                    print("No user_id available in update.")
                    return
    else:
        return(chat_id,user_id)
