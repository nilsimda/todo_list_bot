#!/usr/bin/env python3

import json
from threading import Thread
from time import sleep

import schedule
import telebot

# fill in your own values
bot = telebot.TeleBot("TOKEN")
chat_id = 123456789
friend_username = "max_mustermann"
email = "youremail@gmail.com"


@bot.message_handler(commands=["start", "help"])
def send_help(message):
    bot.reply_to(
        message,
        "Hello, I'm a todo list bot. You can add items with /add <item_id> <description> and finish them with /finish <item_id>. Everyday at 23:59 I will send you a message with the remaining items and calculate how much you owe.",
    )


@bot.message_handler(commands=["add"])
def add_todo_item(message):
    global added_no_items
    args = message.text.split(" ")[1:]
    item_id = args[0]
    description = " ".join(args[1:])

    with open("todolist.json", "r") as f:
        todolist_dict = json.load(f)

    todolist_dict[item_id] = description

    with open("todolist.json", "w") as f:
        json.dump(todolist_dict, f)

    todo_str = dict_to_string(todolist_dict)

    bot.reply_to(message, f"Added todo item: {item_id}!\nRemaining items:\n{todo_str}")
    added_no_items = False


@bot.message_handler(commands=["finish"])
def finish_todo_item(message):
    item_id = message.text.split(" ")[1]

    with open("todolist.json", "r") as f:
        todolist_dict = json.load(f)

    desc = todolist_dict.pop(item_id, None)

    with open("todolist.json", "w") as f:
        json.dump(todolist_dict, f)

    todo_str = dict_to_string(todolist_dict)

    bot.reply_to(message, f"Finished todo item: {desc}!\nRemaining items:\n{todo_str}")


def dict_to_string(todo_dict):
    return "\n".join([f"- {key}: {value}" for key, value in todo_dict.items()])


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(10)


@bot.message_handler(func=lambda message: False)
def send_daily():
    global added_no_items
    with open("todolist.json", "r") as f:
        todolist_dict = json.load(f)

    n_remaining = len(todolist_dict)

    if todolist_dict:
        return bot.send_message(
            chat_id,
            f"You did not finish {n_remaining} items today, this will cost {5*n_remaining} Euro! @{friend_username} please send a Paypal invoice to {email}.",
        )
    elif added_no_items:
        return bot.send_message(
            chat_id,
            f"You did not add any items today, this will cost 20 Euro! @{friend_username} please send a Paypal invoice to {email}.",
        )
    else:
        added_no_items = True
        return bot.send_message(
            chat_id,
            "You finished all items today! You can now add new items for tomorrow.",
        )


if __name__ == "__main__":
    added_no_items = True
    schedule.every().day.at("16:11").do(send_daily)
    Thread(target=schedule_checker).start()

    bot.infinity_polling()
