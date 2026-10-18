from nicegui import ui

from jury_store import load_jury, save_jury, reset_jury


# Make the card for one juror
def make_card(juror: dict, jurors: list[dict]):

    with ui.card().classes('w-full'):
    
        with ui.row().classes('w-full items-center no-wrap'):
            name = ui.input(label='Name', validation={'At least 3 characters': lambda v: len((v or '').strip()) >= 3}).bind_value(juror, 'name').props('borderless dense readonly').classes('grow')
            button = ui.button(icon='edit').props('flat round dense')

        occupation = ui.input(label='Occupation', validation={'At least 5 characters': lambda v: len((v or '').strip()) >= 5}).bind_value(juror, 'occupation').props('borderless dense readonly autogrow').classes('w-full')
        age = ui.number(label='Age', validation={'Between 18 and 75': lambda v: v is not None and 18 <= v <= 75}).bind_value(juror, 'age').props('borderless dense readonly').classes('w-full')
        bias = ui.textarea(label='Personality/Bias (Optional)',
                           placeholder='e.g. "Deeply distrusts authority figures"').bind_value(juror, 'bias').props('borderless dense readonly autogrow').classes('w-full')

        # Each field and the extra props it gets while editing
        fields = {
            name: 'maxlength=50 counter',
            occupation: 'maxlength=100 counter',
            age: 'hint="Between 18 and 75"',
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


def build_jury_tab():
    # Load the jurors details from the json file
    jurors = load_jury()

    @ui.refreshable
    def jury_grid():
        with ui.grid(columns=4).classes('w-full gap-4'):
            for juror in jurors:
                make_card(juror, jurors)

    def confirm_reset():
        jurors[:] = reset_jury()      # keep the same list object
        jury_grid.refresh()
        ui.notify('Jury reset to defaults')

    with ui.dialog() as dialog, ui.card():
        ui.label('Reset all jurors to their defaults? Your changes will be lost.')
        with ui.row():
            ui.button('Cancel', on_click=dialog.close).props('flat no-caps')
            ui.button('Reset', on_click=lambda: (confirm_reset(), dialog.close())).props('color=negative no-caps')

    ui.button(icon='restart_alt', on_click=dialog.open).props('flat no-caps').tooltip("Reset all jurors")
    jury_grid()
