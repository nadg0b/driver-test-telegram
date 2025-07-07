import asyncio
import logging
import sys
import json
import random
import os
import datetime

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import FSInputFile
from aiogram.types import WebAppInfo

from core.config import settings

bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML, show_caption_above_media=True))

dp = Dispatcher()

with open(os.path.join(os.path.dirname(__file__), "data", "data.json"), 'r', encoding="utf-8") as f:
    questions = json.load(f)

user_data = {}


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привіт")


@dp.message(Command("end"))
async def command_end_handler(message: Message) -> None:
    chat_id = message.chat.id

    if not user_data.get(chat_id):
        await message.answer(f"Наразі ти не маєш активних квитків... Натисни /start")
    else:
        await send_summary(chat_id)
        user_data.pop(chat_id)


@dp.message(Command("ticket"))
async def ticket_handler(message: Message, command: CommandObject):
    chat_id = message.chat.id

    if not command.args:
        ticket_num = random.randint(1, 86)
    else:   
        try:
            ticket_num = int(command.args)
            if ticket_num <= 0 or ticket_num > 86:
                await message.answer("❌ Обери номер квитка між 1 та 86.")
                return
            
        except ValueError:
            await message.answer("❌ Неправильний номер квитка.")
            return

    if not user_data.get(chat_id):
        user_data[chat_id] = {"ticket_num": ticket_num,
                              "current_question": 0, 
                              "correct": 0, 
                              "wrong": 0, 
                              "questions": [q for q in questions if q["ticket_num"] == ticket_num],
                              "stamp": str(datetime.datetime.now())}

        await message.answer(f"Вітаю, {html.bold(message.from_user.full_name)}! Твій квиток - №{ticket_num}")
        await send_question(chat_id)
    else:
        await message.answer(f"Заверши квиток №{user_data[chat_id]['ticket_num']} або відправ команду /end")

    
@dp.message(Command("web"))
async def command_web_handler(message: Message) -> None:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Open Web App 🌐", web_app=WebAppInfo(url=settings.web_app_url)
                )
            ]
        ],
        resize_keyboard=True
    )
    await message.answer("Натисни на кнопку щоб відкрити у браузері:", reply_markup=keyboard)


async def send_question(chat_id: int):
    user = user_data.get(chat_id)
    if not user:
        return

    current_index = user["current_question"]

    if current_index >= len(user["questions"]):
        await send_summary(chat_id)
        user_data.pop(chat_id)
        return

    question = user["questions"][current_index]
    answers_text = "\n\n".join([answer_text.strip() for (answer_text, _) in question["answers"]])

    text = (
        f"Питання №{question['ticket_num']}.{question['quest_num']}\n\n"
        f"{question['title']}\n\n"
        f"{answers_text}"
    )

    buttons = [
        [InlineKeyboardButton(text=str(idx+1), callback_data=f"cd_{question['quest_num']}_{idx}_{user['stamp']}")] 
        for idx in range(len(question["answers"]))
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    img_src = question.get("img_src")
    if img_src:
        try:
            img_src = os.path.join(os.path.dirname(__file__), "static/images/", img_src)
            await bot.send_photo(chat_id, photo=FSInputFile(img_src), caption=text, reply_markup=keyboard)
        except Exception as e:
            logging.warning(f"Failed to send image: {e}")
    else:
        await bot.send_message(chat_id, text, reply_markup=keyboard)


async def send_summary(chat_id: int) -> None:
    user = user_data.get(chat_id)
    if not user:
        return

    total = len(user["questions"])
    correct = user["correct"]
    wrong = user["wrong"]

    result = 1 if correct >= 18 else 0

    summary = (
        f"{html.bold('Результат:')}\n\n"
        f"📊 Всього питань: {html.bold(str(total))}\n"
        f"✅ Правильних відповідей: {html.bold(str(correct))}\n"
        f"❌ Неправильних відповідей: {html.bold(str(wrong))}\n\n"
        f"{html.bold('Іспит складено 🤓' if result else 'Іспит не складено 💀')}\n\n"
    )

    await bot.send_message(chat_id, summary)
 

@dp.callback_query(lambda c: c.data.startswith("cd_"))
async def handle_answer(callback_query: CallbackQuery) -> None:
    chat_id = callback_query.message.chat.id

    user = user_data.get(chat_id)
    if not user or user["stamp"] != callback_query.data.split("_")[3]:
        logging.warning("No user or invalid stamp")
        return

    current_index = user["current_question"]
    if not current_index == int(callback_query.data.split("_")[1])-1:
        logging.warning("User presses on old button")
        return 
    
    question = user["questions"][current_index]

    selected_index = int(callback_query.data.split("_")[2])
    is_correct = question["answers"][selected_index][1] == 1

    if is_correct:
        user["correct"] += 1
        response = "✅ Правильно!"
    else:
        user["wrong"] += 1
        correct = [a for a in question['answers'] if a[1]][0][0].split()[0]
        response = f"❌ Ні! Правильна відповідь: {correct}"

    await callback_query.answer(response, show_alert=True)

    user["current_question"] += 1
    await send_question(chat_id)
    

async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())