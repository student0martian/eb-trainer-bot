from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from handlers.start import tickets_keyboard
from utils.loader import get_ticket, get_ticket_ids

router = Router()

# Состояние каждого пользователя в памяти: {user_id: {...}}
sessions = {}


def question_text(ticket, index, chosen=None):
    q = ticket["questions"][index]
    total = len(ticket["questions"])
    lines = [f"{ticket['ticket']}, вопрос {index + 1} из {total}", "", q["question"], ""]
    for key in sorted(q["options"], key=int):
        text = q["options"][key]
        if chosen is not None:
            if key == q["answer_id"]:
                text = "✅ " + text
            elif key == chosen:
                text = "❌ " + text
        lines.append(text)
    return "\n".join(lines)


def answer_keyboard(ticket_id, question):
    builder = InlineKeyboardBuilder()
    for key in sorted(question["options"], key=int):
        builder.button(
            text=key,
            callback_data=f"ans:{ticket_id}:{question['question_id']}:{key}",
        )
    builder.adjust(5)
    return builder.as_markup()


def next_keyboard(ticket_id, question_id, is_last):
    builder = InlineKeyboardBuilder()
    label = "Результат" if is_last else "Далее"
    builder.button(text=label, callback_data=f"next:{ticket_id}:{question_id}")
    return builder.as_markup()


def finish_keyboard(ticket_id):
    ids = get_ticket_ids()
    next_id = ids[(ids.index(ticket_id) + 1) % len(ids)]
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Следующий тест ({next_id})", callback_data=f"ticket:{next_id}")
    builder.button(text="К списку тестов", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data.startswith("ticket:"))
async def start_ticket(callback: CallbackQuery):
    ticket_id = int(callback.data.split(":")[1])
    ticket = get_ticket(ticket_id)
    if ticket is None:
        await callback.answer("Тест не найден", show_alert=True)
        return

    sessions[callback.from_user.id] = {
        "ticket": ticket_id,
        "index": 0,
        "correct": 0,
        "wrong": 0,
        "answered": False,
    }
    question = ticket["questions"][0]
    await callback.message.answer(
        question_text(ticket, 0),
        reply_markup=answer_keyboard(ticket_id, question),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery):
    _, ticket_id, question_id, key = callback.data.split(":")
    ticket_id, question_id = int(ticket_id), int(question_id)

    session = sessions.get(callback.from_user.id)
    ticket = get_ticket(ticket_id)
    if not session or session["ticket"] != ticket_id or session["answered"]:
        await callback.answer("Этот вопрос уже неактуален", show_alert=True)
        return

    index = session["index"]
    question = ticket["questions"][index]
    if question["question_id"] != question_id:
        await callback.answer("Этот вопрос уже неактуален", show_alert=True)
        return

    is_correct = key == question["answer_id"]
    if is_correct:
        session["correct"] += 1
        verdict = "✅ Правильно!"
    else:
        session["wrong"] += 1
        verdict = f"❌ Неправильно.\nПравильный ответ: {question['answer']}"
    session["answered"] = True

    text = (
        question_text(ticket, index, chosen=key)
        + f"\n\n{verdict}\n\nПравильно: {session['correct']}, ошибок: {session['wrong']}"
    )
    is_last = index == len(ticket["questions"]) - 1
    await callback.message.edit_text(
        text,
        reply_markup=next_keyboard(ticket_id, question_id, is_last),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("next:"))
async def handle_next(callback: CallbackQuery):
    _, ticket_id, question_id = callback.data.split(":")
    ticket_id, question_id = int(ticket_id), int(question_id)

    session = sessions.get(callback.from_user.id)
    ticket = get_ticket(ticket_id)
    if not session or session["ticket"] != ticket_id or not session["answered"]:
        await callback.answer("Этот вопрос уже неактуален", show_alert=True)
        return
    if ticket["questions"][session["index"]]["question_id"] != question_id:
        await callback.answer("Этот вопрос уже неактуален", show_alert=True)
        return

    session["index"] += 1
    session["answered"] = False
    total = len(ticket["questions"])

    if session["index"] >= total:
        text = (
            f"{ticket['ticket']} завершён.\n\n"
            f"Правильных ответов: {session['correct']}\n"
            f"Ошибок: {session['wrong']}\n"
            f"Всего вопросов: {total}"
        )
        sessions.pop(callback.from_user.id, None)
        await callback.message.edit_text(text, reply_markup=finish_keyboard(ticket_id))
    else:
        question = ticket["questions"][session["index"]]
        await callback.message.edit_text(
            question_text(ticket, session["index"]),
            reply_markup=answer_keyboard(ticket_id, question),
        )
    await callback.answer()


@router.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery):
    await callback.message.answer("Выберите тест:", reply_markup=tickets_keyboard())
    await callback.answer()
