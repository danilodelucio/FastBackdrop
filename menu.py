import nuke
from FastBackdrop import show_fast_backdrop

def add_menu():
    edit_menu = nuke.menu("Nuke").findItem("Edit")
    if not edit_menu:
        edit_menu = nuke.menu("Nuke").addMenu("Edit")

    edit_menu.addCommand("FastBackdrop", "show_fast_backdrop()", "Alt+B")

add_menu()
