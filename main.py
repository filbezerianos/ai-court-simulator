from nicegui import ui
from pathlib import Path
from tabs.court_tab import build_court_tab
from tabs.jury_tab import build_jury_tab
from tabs.settings_tab import build_settings_tab


# The title
with ui.row().classes('w-full'):
    with ui.column().classes('w-full items-center text-center gap-0'):
        ui.icon('account_balance', size='md').classes('text-blue')
        ui.markdown('### AI Court Simulator').classes('text-blue')
        ui.markdown('###### An AI-powered courtroom drama.')

ui.separator()

with ui.tabs().props('active-color=blue indicator-color=blue no-caps').classes('w-full') as tabs:
    one = ui.tab('one', label='Courtroom', icon='gavel')
    two = ui.tab('two', label='Jury', icon='groups')
    three = ui.tab('three', label='Settings', icon='settings')

# Select the first tab
tabs.set_value(one)



with ui.tab_panels(tabs, value=one).classes('w-full'):
    with ui.tab_panel(one):
        build_court_tab()

    with ui.tab_panel(two):
        build_jury_tab()

    with ui.tab_panel(three):
        build_settings_tab()



# Enable dark mode
dark = ui.dark_mode()
dark.enable()

ui.page_title("AI Court Simulator")

with ui.footer(fixed=False).classes('bg-transparent justify-center'):
    ui.label('Created by Fil Bezerianos.').classes('text-xs text-gray-500')
    ui.link('GitHub', 'https://github.com/filbezerianos/ai-court-simulator', new_tab=True).classes('text-xs')


# Run the app
ui.run(favicon=Path(__file__).parent / 'assets' / 'favicon.svg')
