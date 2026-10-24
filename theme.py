from nicegui import ui

# The colours of the app
PRIMARY = '#5B9BD5'
SECONDARY = '#C9A24B'
ACCENT = '#C9A24B'


# Register the colours, so classes such as text-primary or bg-accent and props such as color=primary use them
def apply_theme():
    ui.colors(primary=PRIMARY, secondary=SECONDARY, accent=ACCENT)
