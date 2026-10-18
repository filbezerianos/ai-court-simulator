from nicegui import ui

from settings_store import load_settings, save_settings


def build_settings_tab():
    # Load the settings from the json file
    settings = load_settings()

    with ui.card().classes('w-96'):
        ui.label('Name Settings').classes('text-h6')
        user_input = ui.input(label='Your Name', validation={'At least 3 characters': lambda v: len((v or '').strip()) >= 3}).classes('w-full').bind_value(settings, 'user_name')
        opponent_input = ui.input(label='Opponent Attorney Name', validation={'At least 3 characters': lambda v: len((v or '').strip()) >= 3}).classes('w-full').bind_value(settings, 'opponent_name')
        judge_input = ui.input(label='Judge Name', validation={'At least 3 characters': lambda v: len((v or '').strip()) >= 3}).classes('w-full').bind_value(settings, 'judge_name')

        def on_save():
            if not all(f.validate() for f in (user_input, opponent_input, judge_input)):
                ui.notify('Fix the highlighted fields', type='negative')
                return
            settings['user_name'] = settings['user_name'].strip()
            settings['opponent_name'] = settings['opponent_name'].strip()
            settings['judge_name'] = settings['judge_name'].strip()
            save_settings(settings)
            ui.notify('Name Settings saved')

        ui.button('Save', icon='save', on_click=on_save)
