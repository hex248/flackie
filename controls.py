import display

###########
# BUTTONS #
###########
btn1 = None
btn2 = None

def init_controls():
    global btn1, btn2
    btn1, btn2 = display.get_buttons()

def register_callbacks(btn1_callback, btn2_callback):
    btn1.when_activated = btn1_callback
    btn2.when_activated = btn2_callback
