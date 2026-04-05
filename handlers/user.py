from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder as Builder

from database.requests import new, getUserByLink, getUser
from config import config

user = Router()


class States(StatesGroup):
    send = State()
    reply = State()


def shareKeyboard(link: str):
    k = Builder()
    k.button(text="🔗 Поделиться ссылкой", url=f"""https://t.me/share/url?url=По этой ссылке можно прислать мне **анонимное сообщение**: t.me/{config.username}?start={link}""")
    return k


def cancelKeyboard():
    k = Builder()
    k.button(text="Отменить отправку", callback_data="back")
    return k


def replyKeyboard(senderLink: str):
    k = Builder()
    k.button(text="↩️ Ответить (текст)", callback_data=f"reply:{senderLink}")
    return k


def mainText(link: str) -> str:
    return f"""<b>Начните получать анонимные вопросы прямо сейчас!

Ваша ссылка:
<blockquote>t.me/{config.username}?start={link}</blockquote>

Разместите эту ссылку ☝️ в описании своего профиля Telegram, TikTok, Instagram (stories), чтобы вам могли написать 💬</b>"""


async def sendMainMenu(m: Message, link: str):
    await m.answer(mainText(link), disable_web_page_preview=True, reply_markup=shareKeyboard(link).as_markup())


@user.message(CommandStart())
async def start(m: Message, command: CommandObject, state: FSMContext):
    data = await state.get_data()
    messageId = data.get("messageId")

    if messageId:
        await m.bot.delete_message(m.chat.id, messageId)
        await state.clear()

    link = await new(m.from_user.id)
    param = command.args
    targetUser = await getUserByLink(param)

    if targetUser:
        sent = await m.answer("""<b>🚀 Здесь можно отправить анонимное сообщение человеку, который опубликовал эту ссылку

🖊 Напишите сюда всё, что хотите ему передать, и через несколько секунд он получит ваше сообщение, но не будет знать от кого

Отправить можно фото, видео, 💬 текст, 🔊 голосовые, 📷 видеосообщения (кружки), а также ✨ стикеры</b>""", reply_markup=cancelKeyboard().as_markup())
        await state.update_data(link=targetUser.link, messageId=sent.message_id)
        await state.set_state(States.send)
        return

    await sendMainMenu(m, link)


@user.message(States.send)
async def send(m: Message, state: FSMContext):
    data = await state.get_data()
    messageId = data.get("messageId")
    link = data.get("link")

    if not messageId or not link:
        await state.clear()
        await sendMainMenu(m, link or "")
        return

    targetUser = await getUserByLink(link)

    if not targetUser:
        await state.clear()
        await sendMainMenu(m, link)
        return

    senderUser = await getUser(m.from_user.id)

    await m.bot.delete_message(m.chat.id, messageId)
    await state.clear()

    if m.text:
        await m.bot.send_message(targetUser.id, f"""📩 У тебя новое сообщение:

<blockquote>{m.text}</blockquote>""", reply_markup=replyKeyboard(senderUser.link).as_markup())
    elif m.photo:
        await m.bot.send_photo(targetUser.id, photo=m.photo[-1].file_id, caption="📷 У тебя новое сообщение", reply_markup=replyKeyboard(senderUser.link).as_markup())
    elif m.video:
        await m.bot.send_video(targetUser.id, video=m.video.file_id, caption="🎬 У тебя новое сообщение", reply_markup=replyKeyboard(senderUser.link).as_markup())
    elif m.voice:
        await m.bot.send_voice(targetUser.id, voice=m.voice.file_id, caption="🔊 У тебя новое сообщение", reply_markup=replyKeyboard(senderUser.link).as_markup())
    elif m.video_note:
        await m.bot.send_video_note(targetUser.id, video_note=m.video_note.file_id, reply_markup=replyKeyboard(senderUser.link).as_markup())
    elif m.sticker:
        await m.bot.send_sticker(targetUser.id, sticker=m.sticker.file_id, reply_markup=replyKeyboard(senderUser.link).as_markup())
    else:
        await sendMainMenu(m, link)
        return

    await m.answer("<b>Отправлено ✅</b>")


@user.callback_query(F.data.startswith("reply:"))
async def replyStart(c: CallbackQuery, state: FSMContext):
    senderLink = c.data.split("reply:")[1]

    targetUser = await getUserByLink(senderLink)
    if not targetUser:
        await c.answer("Пользователь не найден", show_alert=True)
        return

    sent = await c.message.answer("""<b>↩️ Напишите ваш анонимный ответ:

Получатель не будет знать, кто вы</b>""", reply_markup=cancelKeyboard().as_markup())
    await state.update_data(link=senderLink, messageId=sent.message_id)
    await state.set_state(States.reply)
    await c.answer()


@user.message(States.reply)
async def replyMessage(m: Message, state: FSMContext):
    data = await state.get_data()
    messageId = data.get("messageId")
    link = data.get("link")

    if not messageId or not link:
        await state.clear()
        return

    targetUser = await getUserByLink(link)
    if not targetUser:
        await state.clear()
        return

    senderUser = await getUser(m.from_user.id)

    await m.bot.delete_message(m.chat.id, messageId)
    await state.clear()

    reply_markup = replyKeyboard(senderUser.link).as_markup()

    if m.text:
        await m.bot.send_message(targetUser.id, f"""↩️ Тебе ответили анонимно:

<blockquote>{m.text}</blockquote>""", reply_markup=reply_markup)
    elif m.photo:
        await m.bot.send_photo(targetUser.id, photo=m.photo[-1].file_id, caption="↩️ Тебе ответили анонимно (фото)", reply_markup=reply_markup)
    elif m.video:
        await m.bot.send_video(targetUser.id, video=m.video.file_id, caption="↩️ Тебе ответили анонимно (видео)", reply_markup=reply_markup)
    elif m.voice:
        await m.bot.send_voice(targetUser.id, voice=m.voice.file_id, caption="↩️ Тебе ответили анонимно (голосовое)", reply_markup=reply_markup)
    elif m.video_note:
        await m.bot.send_video_note(targetUser.id, video_note=m.video_note.file_id, reply_markup=reply_markup)
    elif m.sticker:
        await m.bot.send_sticker(targetUser.id, sticker=m.sticker.file_id, reply_markup=reply_markup)
    else:
        await sendMainMenu(m, link)
        return

    await m.answer("<b>Ответ отправлен ✅</b>")


@user.callback_query(F.data == "back")
async def back(c: CallbackQuery, state: FSMContext):
    targetUser = await getUser(c.from_user.id)

    if not targetUser:
        return

    await state.clear()
    await c.message.edit_text(mainText(targetUser.link), disable_web_page_preview=True, reply_markup=shareKeyboard(targetUser.link).as_markup())
