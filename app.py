import config
from os import getenv
from tortoise import Tortoise
from dotenv import load_dotenv
from tortoise.models import Model
from models import Font, UserState
from vkbottle import User, Message
from vkbottle.ext import Middleware
from typing import NoReturn, List, Union, Callable
from vkbottle.types.responses.messages import Edit


load_dotenv()

user = User(getenv("VK_TOKEN"))


@user.middleware.middleware_handler()
class NoStrangerMiddleware(Middleware):
    async def pre(self, message: Message):
        if message.from_id != user.user_id:
            return False


@user.middleware.middleware_handler()
class NoSelfMessagesMiddleware(Middleware):
    async def pre(self, message: Message):
        if (await user.api.messages.get_by_id(message.id)).items[
            0
        ].payload == config.BOT_INDICATOR:
            return False


def make_dict(from_chars: str, to_chars: str) -> dict:
    return dict(zip(from_chars, to_chars))


def translate(text: str, dictionary: dict, force_lowercase: bool = True) -> str:
    res = ""
    for char in text:
        new_char = dictionary.get(char)
        if force_lowercase:
            new_char = new_char or dictionary.get(char.lower())
        res += new_char or char
    return res


def command_handler(command: Union[str, List[str]]) -> Callable:
    if isinstance(command, str):
        command = [command]
    text = [config.DELIMITER + com for com in command]

    def wrapper(func):
        return user.on.message_handler(text=text, lower=config.LOWER)(func)

    return wrapper


async def init_db() -> NoReturn:
    await Tortoise.init(db_url=getenv("DB_URL"), modules={"models": ["models"]})
    await Tortoise.generate_schemas()


async def send_message(message: Message, text: str, **params):
    params["payload"] = config.BOT_INDICATOR
    return await message(text, **params)


async def edit_message(
    orig: Message,
    new_text: str = None,
    new_lat: float = None,
    new_long: float = None,
    new_attachment: str = None,
    keep_forward_messages: bool = True,
    keep_snippets: bool = True,
    dont_parse_links: bool = True,
) -> Edit:
    if new_attachment is None:
        attachments = []
        for attachment in orig.attachments:
            attachment_type = attachment["type"]
            data = attachment[attachment_type]
            res = f"{attachment_type}{data['owner_id']}_{data['id']}"
            if key := data.get("key"):
                res = f"{res}_{key}"
            attachments.append(res)
        new_attachment = ",".join(attachments)

    return await user.api.messages.edit(
        peer_id=orig.peer_id,
        message_id=orig.id,
        message=new_text or orig.text,
        lat=new_lat or (orig.geo.coordinates.latitude if orig.geo else None),
        long=new_long or (orig.geo.coordinates.longitude if orig.geo else None),
        attachment=new_attachment,
        keep_forward_messages=keep_forward_messages,
        keep_snippets=keep_snippets,
        dont_parse_links=dont_parse_links,
    )


async def get_or_create(model: Model, **params) -> Model:
    if obj := await model.get_or_none(**params):
        return obj
    else:
        return await model.create(**params)


@command_handler(config.CREATE_FONT)
async def create_font(message: Message, from_chars: str, to_chars: str) -> NoReturn:
    if len(from_chars) == len(to_chars):
        font_id = (await Font.create(dictionary=make_dict(from_chars, to_chars))).id
        await send_message(message, config.FONT_CREATED.format(font_id=font_id))
    else:
        await send_message(message, config.INVALID_DICTIONARY)


@command_handler(config.EDIT_FONT)
async def edit_font(
    message: Message, font_id: int, from_chars: str, to_chars: str
) -> NoReturn:
    if len(from_chars) == len(to_chars):
        if font := await Font.get_or_none(id=font_id):
            font.dictionary = {**font.dictionary, **make_dict(from_chars, to_chars)}
            await font.save()
            await send_message(message, config.FONT_UPDATED.format(font_id=font_id))
        else:
            await send_message(message, config.FONT_NOT_FOUND.format(font_id=font_id))
    else:
        await send_message(message, config.INVALID_DICTIONARY)


@command_handler(config.REDUCE_FONT)
async def reduce_font(message: Message, font_id: int, chars: str) -> NoReturn:
    if font := await Font.get_or_none(id=font_id):
        for char in chars:
            if char in font.dictionary:
                del font.dictionary[char]
        await font.save()
        await send_message(message, config.FONT_UPDATED.format(font_id=font_id))
    else:
        await send_message(message, config.FONT_NOT_FOUND.format(font_id=font_id))


@command_handler(config.SELECT_FONT)
async def select_font(message: Message, font_id: int) -> NoReturn:
    if await Font.get_or_none(id=font_id):
        user_state = await get_or_create(UserState)
        user_state.font_id = font_id
        await user_state.save()
        await send_message(message, config.FONT_SELECTED.format(font_id=font_id))
    else:
        await send_message(message, config.FONT_NOT_FOUND.format(font_id=font_id))


@command_handler(config.DELETE_FONT)
async def delete_font(message: Message, to_delete: str) -> NoReturn:
    ids = (
        [font.id for font in await Font.all()]
        if to_delete == "all"
        else to_delete.replace(" ", "").split(",")
    )

    for font_id in ids:
        if font := await Font.get_or_none(id=font_id):
            await font.delete()
        else:
            return await send_message(
                message, config.FONT_NOT_FOUND.format(font_id=font_id)
            )
    if len(ids) > 1:
        await send_message(
            message, config.FONTS_DELETED.format(font_ids=", ".join(ids))
        )
    else:
        await send_message(message, config.FONT_DELETED.format(font_id=to_delete))


@command_handler(config.SET_FORCE_LOWERCASE_STATE)
async def set_force_lowercase_state(message: Message, state: str) -> NoReturn:
    if state in ("1", "+", "true", "yes", "y"):
        force_lowercase = True
    elif state in ("0", "-", "false", "no", "n"):
        force_lowercase = False
    else:
        return await send_message(
            message, config.INVALID_FORCE_LOWERCASE_STATE.format(state=state)
        )

    user_state = await get_or_create(UserState)
    user_state.force_lowercase = force_lowercase
    await user_state.save()
    await send_message(
        message, config.FORCE_LOWERCASE_STATE_SELECTED.format(state=force_lowercase)
    )


@command_handler(config.VIEW_FONT)
async def view_font(message: Message, font_id: int, text: str = None) -> NoReturn:
    if font := await Font.get_or_none(id=font_id):
        if text:
            await send_message(
                message,
                config.FONT_VIEW.format(
                    font_id=font_id,
                    output=translate(
                        text,
                        font.dictionary,
                        (await get_or_create(UserState)).force_lowercase,
                    ),
                ),
            )
        else:
            await send_message(
                message,
                config.FONT_VIEW.format(
                    font_id=font_id,
                    output=f"{''.join(font.dictionary.keys())}\n{''.join(font.dictionary.values())}",
                ),
            )
    else:
        await send_message(message, config.FONT_NOT_FOUND.format(font_id=font_id))


@command_handler(config.GET_FONTS)
async def get_fonts(message: Message) -> NoReturn:
    font_ids = [str(font.id) for font in await Font.all()]
    if len(font_ids) > 0:
        await send_message(
            message, config.FONT_LIST.format(font_ids=", ".join(font_ids))
        )
    else:
        await send_message(message, config.NO_FONTS)


@command_handler(config.TURN_ON)
async def turn_on(message: Message) -> NoReturn:
    user_state = await get_or_create(UserState)
    user_state.enabled = True
    await user_state.save()
    await send_message(message, config.BOT_ENABLED)


@command_handler(config.TURN_OFF)
async def turn_off(message: Message) -> NoReturn:
    user_state = await get_or_create(UserState)
    user_state.enabled = False
    await user_state.save()
    await send_message(message, config.BOT_DISABLED)


@user.on.message_handler()
async def on_sending(message: Message) -> NoReturn:
    if (
        (user_state := await get_or_create(UserState))
        and user_state.enabled
        and (font := await Font.get_or_none(id=user_state.font_id))
    ):
        await edit_message(
            orig=message,
            new_text=translate(message.text, font.dictionary, user_state.force_lowercase),
        )


#  @user.on.event.message_edit()
#  async def on_editing(event: UserEvents) -> NoReturn:
#      ...  # TODO: translating on editing


if __name__ == "__main__":
    user.run_polling(on_startup=init_db)
