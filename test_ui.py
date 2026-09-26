from ui import render_error_card

render_error_card(
    explanation="The variable 'name' is used but never declared.",
    fix_command="int name = 0;"
)
