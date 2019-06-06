import logging
import os
import subprocess
from subprocess import PIPE
from time import sleep

import telegram
from telegram.error import NetworkError, Unauthorized

from bot.long_tasks import full_submission_cycle_test

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

nick_chat_id = 138018444

authorized_chats = [138018444, 126848884, -1001163348450]

BOT_AUTH_TOKEN = os.getenv('BOT_AUTH_TOKEN')
if not BOT_AUTH_TOKEN:
    raise ValueError('No valid BOT_AUTH_TOKEN supplied')


def main():
    """Run the bot."""
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(BOT_AUTH_TOKEN)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


unauthorized_actions = ['/submit_queue', '/is_all_ok']


def get_submit_queue(*_, **__) -> str:
    cp = subprocess.run(['bash', '-c', 'redis-cli -n 1 --eval redis-submits-queue-count.lua 0'],
                        stdout=PIPE, stderr=PIPE)
    return cp.stdout.decode('utf-8')


def full_submission_cycle(_, chat_id):
    full_submission_cycle_test.delay(chat_id)
    return 'Начинаем тестирование...'


actions_map = {
    '/submit_queue': get_submit_queue,
    '/start_full_submission_cycle': full_submission_cycle
}


def make_action(text: str, chat_id: int) -> str:
    try:
        action = actions_map[text]
    except KeyError:
        return 'Я вас не понял'
    try:
        return action(text, chat_id)
    except Exception as e:
        logger.exception(e)
        if chat_id == nick_chat_id:
            return f'Exception\n{str(e)}'
        return 'Oops! An error wa happened. We already trying to solve the problem!'


def handle_command(msg):
    text = msg.text
    chat_id = msg.chat['id']
    text = text.split('@')[0]
    if text in unauthorized_actions:
        resp = make_action(text, chat_id)
        msg.reply_text(resp)
    else:
        if chat_id in authorized_chats:
            resp = make_action(text, chat_id)
            msg.reply_text(resp)
        else:
            msg.reply_text('Я вас не понял')


def echo(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            print(update.message.chat)
            handle_command(update.message)


if __name__ == '__main__':
    main()
