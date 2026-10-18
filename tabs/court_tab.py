from nicegui import ui

from ai.case_generator import generate_case
from case_store import load_case, clear_case


async def new_case(button):
    button.props('loading')
    button.disable()
    try:
        await generate_case()
    except Exception as e:
        ui.notify(f'Could not generate the case: {e}', type='negative')
        button.props(remove='loading')
        button.enable()
        return
    court_view.refresh()


def case_card(trial: dict):
    case = trial['case']

    async def confirm():
        dialog.close()
        await new_case(reset_button)

    with ui.dialog() as dialog, ui.card():
        ui.label('Start over? The current case and all progress will be lost.')
        with ui.row():
            ui.button('Cancel', on_click=dialog.close).props('flat no-caps')
            ui.button('Start Over', on_click=confirm).props('color=negative no-caps')

    def confirm_clear():
        clear_dialog.close()
        clear_case()
        court_view.refresh()

    with ui.dialog() as clear_dialog, ui.card():
        ui.label('Clear the case? The current case and all progress will be deleted.')
        with ui.row():
            ui.button('Cancel', on_click=clear_dialog.close).props('flat no-caps')
            ui.button('Clear', on_click=confirm_clear).props('color=negative no-caps')

    with ui.column().classes('w-full gap-2 border rounded-lg p-4 shadow-2xl items-center'):
        
        with ui.row().classes('w-full'):
            reset_button = ui.button(icon='restart_alt', on_click=dialog.open).props('flat round dense')
            reset_button.tooltip('Generate a new case')
            clear_button = ui.button(icon='delete', on_click=clear_dialog.open).props('flat round dense')
            clear_button.tooltip('Clear the case')

        # Title: large serif
        ui.label(case['title']).classes('text-2xl font-bold text-center')

        # Charge: red badge
        with ui.row().classes('items-center no-wrap gap-2 px-3 py-1 rounded-md border border-red-800 bg-red-950/40'):
            ui.icon('warning', size='xs').classes('text-red-400')
            ui.label(case['charge']).classes('tracking-wide text-red-400')

        # Summary: the main body text, larger
        ui.label(case['summary']).classes('text-lg leading-relaxed text-gray-300 text-center max-w-3xl')

        ui.separator()

        # Background: small, muted, italic
        ui.label(case['context']).classes('text-gray-500 text-center max-w-3xl')

        # Twist: orange accent with a bolt, under a dashed line
        ui.separator().props('dashed')
        with ui.row().classes('items-start no-wrap gap-2 max-w-3xl'):
            ui.icon('bolt', size='sm').classes('text-orange-400')
            ui.label(case['twist']).classes('text-orange-300 text-center')

        ui.separator()

        # Evidence: numbered list
        ui.label('EVIDENCE').classes('text-xs tracking-widest text-gray-500 font-semibold')
        with ui.column().classes('gap-1 items-start max-w-3xl'):
            for i, item in enumerate(case['evidence'], start=1):
                ui.label(f'E{i}.  {item}').classes('text-sm text-gray-300')

        # Witnesses: pill-shaped chips in a row
        ui.label('WITNESSES').classes('text-xs tracking-widest text-gray-500 font-semibold mt-2')
        with ui.row().classes('gap-2 justify-center'):
            for item in case['witnesses']:
                with ui.row().classes('items-center no-wrap gap-1 px-3 py-1 rounded-full border border-gray-600'):
                    ui.icon('person', size='xs').classes('text-gray-500')
                    ui.label(item).classes('text-xs text-gray-300')


# Redrawn with court_view.refresh() after the case changes
@ui.refreshable
def court_view():
    trial = load_case()

    if trial is None:
        with ui.column().classes('w-full items-center'):

            button = ui.button('Generate Case', icon='auto_awesome').props('no-caps')
            button.on_click(lambda: new_case(button))
    else:
        case_card(trial)


def build_court_tab():
    court_view()
