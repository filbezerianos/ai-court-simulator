from nicegui import ui

from ai.case import generate_case
from ai.judge import judge_opening, generate_judge_statement
from ai.lawyer import generate_opponent_statement
from ai.trial_stages import get_next_stage, STAGE_LABELS, STAGE_INPUT_HINTS
from store.case_store import load_case, clear_case, choose_side, add_entry


# Generate a new case, Generate Case button is clicked
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

    # Refresh with the new case (if successful)
    court_view.refresh()


def on_choose(side: str):

    # Update the json with the chosen side and refresh
    choose_side(side)
    court_view.refresh()


def case_card(trial: dict):
    case = trial['case']

    def confirm_clear():
        clear_dialog.close()
        clear_case()
        court_view.refresh()

    # The dialog when the button on the top right to clear the case and start over is clicked
    with ui.dialog() as clear_dialog, ui.card():
        ui.label('Start over? The current case and all progress will be deleted.')
        with ui.row():
            ui.button('Cancel', on_click=clear_dialog.close).props('flat no-caps')
            ui.button('Start Over', on_click=confirm_clear).props('color=negative no-caps')

    with ui.column().classes('w-full gap-2 border rounded-lg p-4 shadow-2xl items-center'):

        # The button to clear the case and start over
        with ui.row().classes('w-full'):
            clear_button = ui.button(icon='delete', on_click=clear_dialog.open).props('flat round dense')
            clear_button.tooltip('Start over')

        # Title of the case
        ui.label(case['title']).classes('text-2xl font-bold text-center')

        # The charge
        with ui.row().classes('items-center no-wrap gap-2 px-3 py-1 rounded-md border border-red-800 bg-red-950/40'):
            ui.icon('warning', size='xs').classes('text-red-400')
            ui.label(case['charge']).classes('tracking-wide text-red-400')

        # The summary
        ui.label(case['summary']).classes('text-lg leading-relaxed text-gray-300 text-center max-w-3xl')

        ui.separator()

        # The background, context
        ui.label(case['context']).classes('text-gray-500 text-center max-w-3xl')

        # The twist
        ui.separator().props('dashed')
        with ui.row().classes('items-start no-wrap gap-2 max-w-3xl'):
            ui.icon('bolt', size='sm').classes('text-orange-400')
            ui.label(case['twist']).classes('text-orange-300 text-center')

        ui.separator()

        # The evidence
        ui.label('EVIDENCE').classes('text-xs tracking-widest text-gray-500 font-semibold')
        with ui.column().classes('gap-1 items-start max-w-3xl'):
            for i, item in enumerate(case['evidence'], start=1):
                ui.label(f'E{i}.  {item}').classes('text-sm text-gray-300')

        # The witnesses
        ui.label('WITNESSES').classes('text-xs tracking-widest text-gray-500 font-semibold mt-2')
        with ui.row().classes('gap-2 justify-center'):
            for item in case['witnesses']:
                with ui.row().classes('items-center no-wrap gap-1 px-3 py-1 rounded-full border border-gray-600'):
                    ui.icon('person', size='xs').classes('text-gray-500')
                    ui.label(item).classes('text-xs text-gray-300')


    # The two button for the user to select side, Prosecution or Defence
    with ui.column().classes('w-full gap-2 p-4 items-center'):

        # Side selection, until the player has chosen
        player = trial['cast']['player']

        # Check if a side has been selected already, the current_case.jspn must not be empty
        if player['side'] is None:
            ui.label('Choose your side').classes('tracking-widest text-gray-500 font-semibold')
            with ui.row().classes('gap-4'):
                ui.button('Prosecution', icon='gavel', on_click=lambda: on_choose('prosecution')).props('no-caps')
                ui.button('Defence', icon='shield', on_click=lambda: on_choose('defence')).props('no-caps')
        else:
            # Pick the values from the json file
            opponent = trial['cast']['opponent']
            ui.label(f"You are the {player['side']} | Opposing Counsel: {opponent['name']} ({opponent['side']})").classes('text-blue-400 text-bold')


# This is the opening from the judge, the Start Trial button is clicked
async def start_trial_with_judge_opening(button, typing, judge_name: str):
    button.visible = False

    # Show the typing animation while the judge "thinks"
    with typing:
        with ui.chat_message(name=judge_name):
            ui.spinner('dots', size='2rem')
    try:
        await judge_opening()
    except Exception as e:
        typing.clear()
        button.visible = True
        ui.notify(f'The judge could not open the trial: {e}', type='negative')
        return
    court_view.refresh()


# An AI speaker (the opponent or the judge) speaks, the Continue button is clicked.
# generate_statement is the function that asks the model for the given stage.
async def continue_with_ai_statement(continue_button, typing, speaker_name: str, stage: str, generate_statement):
    continue_button.visible = False

    # Show the typing animation while the speaker "thinks"
    with typing:
        with ui.chat_message(name=speaker_name):
            ui.spinner('dots', size='2rem')
    try:
        await generate_statement(stage)
    except Exception as e:
        typing.clear()
        continue_button.visible = True
        ui.notify(f'{speaker_name} could not give the statement: {e}', type='negative')
        return
    court_view.refresh()


# The player's statement is typed in the input box, the Deliver Statement button is clicked
def submit_player_statement(statement_input, stage: str, player: dict):
    if not statement_input.validate():
        ui.notify('Your statement is too short', type='negative')
        return
    add_entry(player['name'], player['side'], stage, statement_input.value.strip())
    court_view.refresh()


# Decide who speaks next: the player gets an input box, the AI opponent gets a Continue button
def show_next_trial_step(trial: dict):
    next_stage = get_next_stage(trial)
    if next_stage is None:
        return

    stage = next_stage['stage']
    stage_label = STAGE_LABELS[stage]
    player = trial['cast']['player']
    opponent = trial['cast']['opponent']
    judge = trial['cast']['judge']

    if next_stage['speaker_role'] == 'judge':
        typing = ui.column().classes('w-full')
        continue_button = ui.button(
            f'Continue: {judge["name"]} gives the {stage_label}', icon='arrow_forward'
        ).props('no-caps').classes('self-center')
        continue_button.on_click(lambda: continue_with_ai_statement(continue_button, typing, judge['name'], stage, generate_judge_statement))
    elif next_stage['speaker_role'] == player['side']:
        statement_input = ui.textarea(
            label=f'Your {stage_label} ({player["side"]})',
            placeholder=STAGE_INPUT_HINTS[stage],
            validation={'At least 50 characters': lambda v: len((v or '').strip()) >= 50},
        ).props('outlined autogrow').classes('w-full')
        deliver_statement_button = ui.button('Deliver Statement', icon='send').props('no-caps').classes('self-center')
        deliver_statement_button.on_click(lambda: submit_player_statement(statement_input, stage, player))
    else:
        typing = ui.column().classes('w-full')
        continue_button = ui.button(
            f'Continue: {opponent["name"]} ({opponent["side"]}) gives the {stage_label}', icon='arrow_forward'
        ).props('no-caps').classes('self-center')
        continue_button.on_click(lambda: continue_with_ai_statement(continue_button, typing, opponent['name'], stage, generate_opponent_statement))


# The trial as a chat: one message per transcript entry
def trial_chat(trial: dict):
    player_name = trial['cast']['player']['name']

    with ui.column().classes('w-full mx-auto gap-1 p-4'):
        for entry in trial['transcript']:
            paragraphs = [p for p in entry['text'].split('\n') if p.strip()]
            ui.chat_message(
                paragraphs,
                name=entry['speaker'],
                stamp=STAGE_LABELS[entry['stage']],
                sent=entry['speaker'] == player_name,
            )

        # For the first chat, transcript not created yet, the judge is doing the opening
        if not trial['transcript']:
            typing = ui.column().classes('w-full')
            start_trial_button = ui.button('Start Trial', icon='play_arrow').props('no-caps').classes('self-center')
            start_trial_button.on_click(lambda: start_trial_with_judge_opening(start_trial_button, typing, trial['cast']['judge']['name']))
        else:
            show_next_trial_step(trial)


# Redrawn with court_view.refresh() after the case changes
@ui.refreshable
def court_view():
    
    # Load the current_case.json to see if there is one in progress
    trial = load_case()

    # If the json is empty, show the Generate Case button, else show the details of the case
    if trial is None:
        with ui.column().classes('w-full items-center'):

            generate_case_button = ui.button('Generate Case', icon='auto_awesome').props('no-caps')
            generate_case_button.on_click(lambda: new_case(generate_case_button))
    else:
        # If there is a current case already show it
        case_card(trial)

        # The trial starts once the player has chosen a side
        if trial['cast']['player']['side'] is not None:
            trial_chat(trial)


def build_court_tab():
    court_view()
