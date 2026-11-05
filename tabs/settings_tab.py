from nicegui import ui
from store.settings_store import load_settings, save_settings


def build_settings_tab():
    # Load the settings from the json file
    settings = load_settings()

    with ui.card().classes('w-full'):
        ui.label('Name Settings').classes('text-h6 text-primary')
        user_input = ui.input(label='Your Name', validation={'At least 3 characters': lambda v: len((v or '').strip()) >= 3}).classes('w-full').bind_value(settings, 'user_name')
        opponent_input = ui.input(label='Opponent Attorney Name', validation={'At least 3 characters': lambda v: len((v or '').strip()) >= 3}).classes('w-full').bind_value(settings, 'opponent_name')
        judge_input = ui.input(label='Judge Name', validation={'At least 3 characters': lambda v: len((v or '').strip()) >= 3}).classes('w-full').bind_value(settings, 'judge_name')

        # The model of the opponent attorney, and the two models the jurors can use.
        # Each juror picks one of the two juror models in the Jury tab.
        ui.label('Models').classes('text-h6 text-primary')
        opponent_model_input = ui.input(label='Opponent Attorney Model', validation={'Required': lambda v: bool((v or '').strip())}).classes('w-full').bind_value(settings, 'opponent_model')
        juror_model_1_input = ui.input(label='Juror Model 1', validation={'Required': lambda v: bool((v or '').strip())}).classes('w-full').bind_value(settings, 'juror_model_1')
        juror_model_2_input = ui.input(label='Juror Model 2', validation={'Required': lambda v: bool((v or '').strip())}).classes('w-full').bind_value(settings, 'juror_model_2')

        def on_save():
            if not all(f.validate() for f in (user_input, opponent_input, judge_input, opponent_model_input, juror_model_1_input, juror_model_2_input)):
                ui.notify('Fix the highlighted fields', type='negative')
                return
            for key in ('user_name', 'opponent_name', 'judge_name', 'opponent_model', 'juror_model_1', 'juror_model_2'):
                settings[key] = settings[key].strip()
            save_settings(settings)
            ui.notify('Settings Saved', type='info')

        ui.button('Save', icon='save', on_click=on_save)
