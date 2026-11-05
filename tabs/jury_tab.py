from nicegui import ui
from store.jury_store import load_jury, save_jury, reset_jury
from store.settings_store import load_settings


# Make the card for one juror. model_options maps the model slot (1 or 2) to the model name.
def make_card(juror: dict, jurors: list[dict], model_options: dict):

    with ui.card().classes('w-full'):
    
        with ui.row().classes('w-full items-center no-wrap'):
            name = ui.input(label='Name', validation={'At least 3 characters': lambda v: len((v or '').strip()) >= 3}).bind_value(juror, 'name').props('borderless dense readonly').classes('grow')
            button = ui.button(icon='edit').props('flat round dense')

        occupation = ui.input(label='Occupation', validation={'At least 5 characters': lambda v: len((v or '').strip()) >= 5}).bind_value(juror, 'occupation').props('borderless dense readonly autogrow').classes('w-full')
        age = ui.number(label='Age', validation={'Between 18 and 75': lambda v: v is not None and 18 <= v <= 75}).bind_value(juror, 'age').props('borderless dense readonly').classes('w-full')
        model = ui.select(model_options, label='Model').bind_value(juror, 'model_slot').props('borderless dense readonly').classes('w-full')
        bias = ui.textarea(label='Personality/Bias (Optional)',
                           placeholder='e.g. "Deeply distrusts authority figures"').bind_value(juror, 'bias').props('borderless dense readonly autogrow').classes('w-full')

        # Each field and the extra props it gets while editing
        fields = {
            name: 'maxlength=50 counter',
            occupation: 'maxlength=100 counter',
            age: 'hint="Between 18 and 75"',
            model: '',
            bias: 'maxlength=200 counter',
        }
        editing = False

        def toggle():
            nonlocal editing

            # Do not save if there are errors
            if editing and not all(f.validate() for f in (name, occupation, age)):
                ui.notify('Fix the highlighted fields', type='negative')
                return

            editing = not editing

            for field, extra in fields.items():
                if editing:
                    field.props(remove='readonly borderless').props('outlined ' + extra)
                else:
                    field.props(remove='outlined maxlength counter hint').props('readonly borderless')

            button.props(f'icon={"check" if editing else "edit"}')

            if not editing:
                juror['age'] = int(juror['age'])
                juror['bias'] = (juror['bias'] or '').strip() or None
                save_jury(jurors)
                ui.notify(f'Saved: {juror["name"]}')

        button.on_click(toggle)


# Create the grid with the cards for all jurors
def build_jury_tab():
    # Load the jurors details from the json file
    jurors = load_jury()

    # The two juror models from the settings, a juror picks one of them
    settings = load_settings()
    model_options = {1: settings['juror_model_1'], 2: settings['juror_model_2']}

    @ui.refreshable
    def jury_grid():
        with ui.grid(columns=4).classes('w-full gap-4'):
            for juror in jurors:
                make_card(juror, jurors, model_options)

    def confirm_reset():
        jurors[:] = reset_jury()      # keep the same list object
        jury_grid.refresh()
        ui.notify('Jury configuration reset to defaults.', type='info')

    with ui.dialog() as dialog, ui.card():
        ui.label(f'Reset all jurors to their defaults? Your current jury configuration will be lost.')
        with ui.row():
            ui.button('Cancel', on_click=dialog.close).props('flat no-caps')
            ui.button('Reset', on_click=lambda: (confirm_reset(), dialog.close())).props('color=negative no-caps')

    ui.button(icon='restart_alt', on_click=dialog.open).props('flat no-caps').tooltip("Reset all jurors")
    jury_grid()
