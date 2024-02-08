import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import aiohttp

from ComradeAI.Mycelium import Mycelium, Message, Dialog, UnifiedPrompt, RoutingStrategy

from config import API_TOKEN, ComradeAIToken, model_mapping, requestAgentConfigs, token_limits
from utils import extract_and_clean_links, url_text, count_cut_tokens

bot = AsyncTeleBot(API_TOKEN)


async def message_received_handler(dialog):
    dialog_id = dialog.dialog_id
    print(dialog_id)
    model = await get_data(dialog_id, 'user_model')
    print(model)
    user_model = "Использована модель: " + model

    try:
        if dialog_id and model:
            for message in dialog.messages:
                for prompt in message.unified_prompts:
                    content = prompt.content
                    if len(content) > 4096:
                        parts = [content[i:i + 4096] for i in range(0, len(content), 4096 - len(user_model))]
                        for part_index, part in enumerate(parts):
                            if part_index == len(parts) - 1:
                                part += "\n\n" + user_model
                                print('Ответ 1')
                            await bot.send_message(dialog_id, f"Ответ от модели: {part}")
                    else:
                        content += "\n\n" + user_model
                        print('Ответ 2')
                        await bot.send_message(dialog_id, f"Ответ от модели: {content}")
        else:
            print(f"Произошла ошибка с диалогом: {dialog_id}")
    except:
        await bot.send_message(dialog_id, f"Произошла ошибка при отправке сообщения")


mycelium = Mycelium(ComradeAIToken=ComradeAIToken, message_received_callback=message_received_handler)

user_data = {}


async def set_data(user_id, key, value):
    user_id = str(user_id)
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][key] = value


async def get_data(user_id, key):
    user_id = str(user_id)
    return user_data.get(user_id, {}).get(key, "")


async def reset_state(user_id):
    user_data.pop(user_id, None)


def generate_model_selection_keyboard():
    markup = types.InlineKeyboardMarkup()
    models = ["GPT-3.5", "Gemini Pro", "GPT-4", "LLaMa 2", "YandexGPT v2", "Claude-2.1"]
    for model in models:
        markup.add(types.InlineKeyboardButton(text=model, callback_data=f"model:{model}"))
    return markup


@bot.message_handler(commands=['start', 'reset'])
async def start_cmd(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Выбор модели"))
    await bot.send_message(message.chat.id, "Привет! Нажмите на кнопку ниже, чтобы выбрать модель AI.",
                           reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Выбор модели")
async def choose_model_cmd(message):
    markup = generate_model_selection_keyboard()
    await bot.send_message(message.chat.id, "Выберите модель AI:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
async def callback_inline(call):
    if call.data.startswith('model:'):
        user_model = call.data.split(':')[1]
        selected_model = model_mapping[user_model]
        selected_config = requestAgentConfigs[user_model]
        await set_data(call.message.chat.id, 'model', selected_model)
        await set_data(call.message.chat.id, 'user_model', user_model)
        await set_data(call.message.chat.id, 'model_config', selected_config)
        await bot.answer_callback_query(call.id, text=f"Выбрана модель {user_model}")
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        await bot.send_message(call.message.chat.id, "Введите ваш запрос")


@bot.message_handler(func=lambda message: True, content_types=['text'])
async def process_input(message):
    global mycelium

    model = await get_data(message.chat.id, 'model')
    print(model)
    user_model = await get_data(message.chat.id, 'user_model')
    model_config = await get_data(message.chat.id, 'model_config')

    if not model:
        await choose_model_cmd(message)
        return

    prompt = message.text + " Далее идет содержание ссылок: "

    links = await extract_and_clean_links(prompt)
    if links:
        async with aiohttp.ClientSession() as session:
            links_data = [await url_text(session, link) for link in links]
    else:
        await bot.send_message(message.chat.id, "Не могу получить доступ к информации по ссылке")
        return

    combined_text = "\n".join(links_data)
    prompt += combined_text

    token_limit = token_limits.get(user_model, 4096)
    prompt = await count_cut_tokens(prompt, token_limit)

    dialog_id = str(message.chat.id)

    dialog = Dialog(messages=[], dialog_id=dialog_id, reply_to=ComradeAIToken, requestAgentConfig=model_config)
    mycelium.dialogs[dialog_id] = dialog

    routing_strategy = RoutingStrategy("direct", model)
    hello_prompt = UnifiedPrompt(content_type="text", content=prompt, mime_type="text/plain")
    hello_message = Message(role="user", unified_prompts=[hello_prompt], routingStrategy=routing_strategy)
    dialog.messages.append(hello_message)

    await mycelium.send_to_mycelium(dialog_id, isReply=False)


bot.register_message_handler(start_cmd, commands=['start', 'reset'], state="*")


async def main():
    server_task = mycelium.start_server(allowNewDialogs=True)
    bot_task = bot.polling(non_stop=True)
    await asyncio.gather(server_task, bot_task)


if __name__ == "__main__":
    asyncio.run(main())
