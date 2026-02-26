from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    choice_event = State()
    waiting_for_broadcast_text = State()
    waiting_for_broadcast_image = State()
    waiting_for_broadcast_image_text = State()
    waiting_for_broadcast_video = State()
    waiting_for_broadcast_media_text = State()
    waiting_for_target_broadcast_image = State()
    waiting_for_target_broadcast_image_text = State()
    waiting_for_target_broadcast_video = State()
    waiting_for_target_broadcast_media_text = State()

class AdminChangeBalance(StatesGroup):
    waiting_subtractsum = State()
    waiting_addvalue = State()
    waiting_subtractvalue = State()


class AddPhoneNumber(StatesGroup):
    add_phone = State()

class AdminWasEvent(StatesGroup):
    add_event = State()

class AdminAddRemind(StatesGroup):
    add_text = State()
    add_date = State()