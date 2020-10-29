BOT_INDICATOR = '{"vk-fonts":"self"}'


INVALID_DICTIONARY = "❌  Это чё за хуйня?"

INVALID_FORCE_LOWERCASE_STATE = "❌  Это чё за хуйня?"
FORCE_LOWERCASE_STATE_SELECTED = (
    "✅  Установлено новое значение 'force lowercase': {state}"  # get 'state'
)

FONT_CREATED = "✅  Создан новый шрифт с id={font_id}."  # get 'font_id'
FONT_UPDATED = "✅  Шрифт с id={font_id} обновлён."  # get 'font_id'
FONT_SELECTED = "✅  Выбран шрифт с id={font_id}."  # get 'font_id'
FONT_NOT_FOUND = "❌  Ты еблан? Нет такого шрифта."
FONT_DELETED = "✅  Шрифт с id={font_id} удалён."  # get 'font_id'
FONTS_DELETED = "✅  Выбранные шрифты удалены."  # get 'font_ids'
FONT_VIEW = "✅  Шрифт с id={font_id}:\n\n{output}"  # get 'font_id' and 'output'
FONT_LIST = "✅  Доступные шрифты: {font_ids}"  # get 'font_ids'
NO_FONTS = "❌  Не создано ни одного шрифта."

BOT_ENABLED = "✅  Изменение шрифта включено."
BOT_DISABLED = "✅  Изменение шрифта отключено."


DELIMITER = "!"
LOWER = True

CREATE_FONT = [
    "create\n<from_chars>\n<to_chars>",
    "create <from_chars> <to_chars>",
    "new\n<from_chars>\n<to_chars>",
    "new <from_chars> <to_chars>",
]  # 'from_chars' and 'to_chars' must be specified

EDIT_FONT = [
    "add <font_id:int>\n<from_chars>\n<to_chars>",
    "add <font_id:int> <from_chars> <to_chars>",
    "edit <font_id:int>\n<from_chars>\n<to_chars>",
    "edit <font_id:int> <from_chars> <to_chars>",
]  # 'font_id:int', 'from_chars' and 'to_chars' must be specified

REDUCE_FONT = [
    "reduce <font_id:int>\n<chars>",
    "reduce <font_id:int> <chars>",
]  # 'font_id:int' and 'chars' must be specified

SELECT_FONT = [
    "select <font_id:int>",
    "sel <font_id:int>",
    "change <font_id:int>",
    "ch <font_id:int>",
]  # 'font_id:int' must be specified

DELETE_FONT = [
    "delete <to_delete>",
    "del <to_delete>",
    "remove <to_delete>",
    "rm <to_delete>",
]  # 'to_delete' must be specified

SET_FORCE_LOWERCASE_STATE = [
    "force lowercase <state>",
    "force lc <state>",
    "flc <state>",
]  # 'state' must be specified

VIEW_FONT = [
    "view <font_id:int>",
    "view <font_id:int> <text>",
]  # 'font_id:int' and optionally 'text' must be specified

GET_FONTS = ["list", "fonts"]

TURN_ON = ["enable", "on"]

TURN_OFF = ["disable", "off"]
