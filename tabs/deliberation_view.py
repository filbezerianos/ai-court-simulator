from nicegui import ui

from ai.jury import run_jury_deliberation, did_player_win
from store.case_store import save_case_copy
from store.jury_store import load_jury

# Colours and icon of each decision
DECISION_STYLES = {
    'guilty': ('border-red-700 bg-red-950/40 text-red-400', 'gavel'),
    'not guilty': ('border-green-700 bg-green-950/40 text-green-400', 'shield'),
}


# The decision of a juror as a badge, with the rationale in an expandable section
def show_vote(vote: dict):
    style, icon = DECISION_STYLES[vote['decision']]
    with ui.row().classes(f'items-center no-wrap gap-2 px-3 py-1 rounded-md border {style}'):
        ui.icon(icon, size='xs')
        ui.label(vote['decision'].upper()).classes('text-xs font-bold tracking-wide')
    with ui.expansion('Rationale', icon='info').classes('w-full text-sm'):
        ui.label(vote['rationale']).classes('text-gray')


# The card of one juror: the name, then the dots while the juror decides, or the vote when it is known.
# Returns the container of the status, so the dots can be replaced by the vote later.
def show_juror_card(juror_name: str, vote: dict | None = None):
    with ui.card().classes('w-full gap-1'):
        ui.label(juror_name).classes('font-bold')
        status = ui.column().classes('w-full gap-1')
        with status:
            if vote is None:
                ui.spinner('dots', size='2rem', color='white')
            else:
                show_vote(vote)
    return status


# The final verdict of a round and whether the player won, or the hung jury message
def show_verdict_banner(round_result: dict, player_side: str):
    score = f"{round_result['guilty']} guilty – {round_result['not_guilty']} not guilty"
    result = round_result['result']

    with ui.column().classes('w-full items-center gap-1 border rounded-lg p-4 shadow-2xl'):
        if result == 'tie':
            ui.label('HUNG JURY').classes('text-3xl font-bold text-orange-400')
            ui.label(f'{score}. The jury has to decide again.').classes('text-gray-300')
            return

        verdict_colour = 'text-red' if result == 'guilty' else 'text-green'
        ui.label(f'VERDICT: {result.upper()}').classes(f'text-3xl font-bold {verdict_colour}')
        ui.label(score).classes('text-gray-300')
        if did_player_win(player_side, result):
            ui.label(f'You won the case as the {player_side}!').classes('text-xl font-bold text-green mt-2')
        else:
            ui.label(f'You lost the case as the {player_side}.').classes('text-xl font-bold text-red mt-2')


# The saved result of a round: the 12 jurors with their decisions, then the verdict
def show_round_result(round_result: dict, round_number: int, player_side: str):
    if round_number > 1:
        ui.label(f'Round {round_number}').classes('text-xs tracking-widest text-gray font-semibold')
    with ui.grid(columns=3).classes('w-full gap-4'):
        for vote in round_result['votes']:
            show_juror_card(vote['name'], vote)
    show_verdict_banner(round_result, player_side)


# The jurors decide: their names with dots, each replaced by the decision as it arrives.
# The Start Deliberation / Run Jury Decisions Again button is clicked.
async def run_deliberation_on_page(button, board, refresh_court):
    button.visible = False
    board.clear()

    statuses = {}
    with board:
        ui.notification('The jury is deliberating. Please wait...', type='info')
        ui.separator()
        ui.label('The jury is deliberating...').classes('text-gray')
        with ui.grid(columns=3).classes('w-full gap-4'):
            for juror in load_jury():
                statuses[juror['id']] = show_juror_card(juror['name'])

    def show_decision(vote: dict):
        status = statuses[vote['juror_id']]
        status.clear()
        with status:
            show_vote(vote)

    try:
        await run_jury_deliberation(on_juror_decided=show_decision)
    except Exception as e:
        ui.notify(f'The jury could not reach a decision: {e}', type='negative')
    # Redraw from the saved rounds: the result, or the button again if nothing was saved
    refresh_court()


# The Save Case button is clicked: keep a copy of the finished case in data/saved_cases
def save_finished_case():
    saved_file = save_case_copy()
    ui.notify(f'Case saved: {saved_file.name}', type='positive')


# The last phase of the trial. refresh_court redraws the Courtroom tab,
# open_start_over_dialog opens the confirmation to clear the case.
def show_jury_deliberation(trial: dict, refresh_court, open_start_over_dialog):
    rounds = trial.get('verdict', {}).get('rounds', [])
    last_round = rounds[-1] if rounds else None
    player_side = trial['cast']['player']['side']

    board = ui.column().classes('w-full gap-4')
    if last_round is not None:
        with board:
            show_round_result(last_round, len(rounds), player_side)

    # The jurors have not decided yet, or they were tied 6 - 6
    if last_round is None or last_round['result'] == 'tie':
        button_text = 'Start Deliberation' if last_round is None else 'Run Jury Decisions Again'
        deliberation_button = ui.button(button_text).props('no-caps').classes('self-center')
        deliberation_button.on_click(lambda: run_deliberation_on_page(deliberation_button, board, refresh_court))

    # The final verdict is shown: the player can keep the case or start over from here
    else:
        with ui.row().classes('self-center gap-4'):
            ui.button('Save Case', icon='save', on_click=save_finished_case).props('no-caps')
            ui.button('Start Over', icon='delete', on_click=open_start_over_dialog).props('no-caps color=negative')
