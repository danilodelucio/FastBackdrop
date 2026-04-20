# -----------------------------------------------------------------------------------
#  FastBackdrop
#  Version: v01.0
#  Author: Danilo de Lucio
#  Website: www.danilodelucio.com
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
#  [Summary]
#  A fast, clean backdrop creator for Nuke.
#
#  [Default shorcut]
#  Alt + B 
# -----------------------------------------------------------------------------------


import nuke
import os
from functools import partial

try:
    from PySide2 import QtWidgets, QtGui, QtCore
except ImportError:
    try:
        from PySide6 import QtWidgets, QtGui, QtCore
    except ImportError:
        nuke.message("Error: Neither PySide2 nor PySide6 is available in this Nuke build.")
        raise


# --------- CONSTANTS ---------
DEFAULT_FONT = "Segoe UI"
DEFAULT_FONT_SIZE = 80

DEFAULT_BOLD = True
DEFAULT_ITALIC = False

DEFAULT_COLOR = 0x1F252FFF

DEFAULT_PADDING = 80
TOP_EXTRA = 120

COLOR_PRESETS = [
    0x592929FF,
    0x595929FF,
    0x293959FF,
    0x392959FF,
    0x592949FF,
    0x594929FF,
    0x295959FF,
]


# ==========================
# BACKDROP LOGIC
# ==========================
def create_fast_backdrop(label, color):
    sel = nuke.selectedNodes()
    if not sel:
        nuke.message("Select some nodes first.")
        return

    if label.strip():
        top_extra = TOP_EXTRA
        label = "<center>%s" % label
    else:
        top_extra = 0

    font_style = DEFAULT_FONT
    if DEFAULT_BOLD and DEFAULT_ITALIC:
        font_style += " Bold Italic"
    elif DEFAULT_BOLD:
        font_style += " Bold"
    elif DEFAULT_ITALIC:
        font_style += " Italic"

    min_x = min(n.xpos() for n in sel)
    min_y = min(n.ypos() for n in sel)
    max_x = max(n.xpos() + n.screenWidth() for n in sel)
    max_y = max(n.ypos() + n.screenHeight() for n in sel)

    bd = nuke.nodes.BackdropNode(
        xpos=min_x - DEFAULT_PADDING,
        ypos=min_y - (DEFAULT_PADDING + top_extra),
        bdwidth=(max_x - min_x) + DEFAULT_PADDING * 2,
        bdheight=(max_y - min_y) + DEFAULT_PADDING * 2 + top_extra,
        tile_color=color,
        note_font=font_style,
        note_font_size=DEFAULT_FONT_SIZE,
        note_font_color=0xFFFFFFFF,
        label=label
    )

    return bd


# ==========================
# COLOR BUTTON
# ==========================
class ColorButton(QtWidgets.QPushButton):
    def __init__(self, color, selectable=False, *args, **kwargs):
        super(ColorButton, self).__init__(*args, **kwargs)
        self.setFixedSize(26, 26)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.selectable = selectable
        self.selected = False
        self.set_color(color)

    def set_color(self, color):
        self.color = color

        r = (color >> 24) & 255
        g = (color >> 16) & 255
        b = (color >> 8) & 255

        if self.selected:
            border = "#4A90E2"
        else:
            border = "transparent"

        style = (
            "QPushButton {"
            "background-color: rgb(%d,%d,%d);"
            "border-radius: 4px;"
            "border: 2px solid %s;"
            "}"
            "QPushButton:hover {"
            "border: 2px solid #AAA;"
            "}"
        ) % (r, g, b, border)

        self.setStyleSheet(style)

    def set_selected(self, state):
        self.selected = state
        self.set_color(self.color)


# ==========================
# UI PANEL
# ==========================
class FastBackdropPanel(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(FastBackdropPanel, self).__init__(parent)

        self.setWindowTitle("FastBackdrop")
        self.setMinimumWidth(380)
        self.color = DEFAULT_COLOR
        self.preset_buttons = []

        main = QtWidgets.QVBoxLayout(self)
        row1 = QtWidgets.QHBoxLayout()

        # Label input
        self.label_edit = QtWidgets.QLineEdit()
        self.label_edit.setPlaceholderText("Custom Label")
        self.label_edit.setMinimumHeight(34)
        self.label_edit.setStyleSheet("QLineEdit { padding: 6px; font-size: 14px; }")
        row1.addWidget(self.label_edit)

        # Presets
        for preset in COLOR_PRESETS:
            btn = ColorButton(preset, selectable=True)
            btn.clicked.connect(partial(self.set_preset_color, preset, btn))
            self.preset_buttons.append(btn)
            row1.addWidget(btn)

        # Separator
        sep = QtWidgets.QLabel(" | ")
        sep.setStyleSheet("color: #666; font-size: 14px;")
        row1.addWidget(sep)

        # Pick Color button with external PNG
        self.color_btn = ColorButton(self.color)

        icon_path = os.path.join(os.path.dirname(__file__), "img", "colorpicker_icon.png")
        if os.path.exists(icon_path):
            self.color_btn.setIcon(QtGui.QIcon(icon_path))
            self.color_btn.setIconSize(QtCore.QSize(18, 18))

        self.color_btn.clicked.connect(self.pick_color)
        row1.addWidget(self.color_btn)

        main.addLayout(row1)

        # Create Backdrop button
        create_btn = QtWidgets.QPushButton("Create Backdrop")
        create_btn.setMinimumHeight(36)
        create_btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        create_btn.clicked.connect(self.create_backdrop)
        main.addWidget(create_btn)

        self.label_edit.returnPressed.connect(self.create_backdrop)

    def set_preset_color(self, color, button):
        self.color = color
        self.color_btn.set_color(color)

        for b in self.preset_buttons:
            b.set_selected(b is button)

    def pick_color(self):
        color = nuke.getColor()
        if color is not None:
            self.color = color
            self.color_btn.set_color(color)
            for b in self.preset_buttons:
                b.set_selected(False)

    def create_backdrop(self):
        label = self.label_edit.text()
        create_fast_backdrop(label, self.color)
        self.close()


# ==========================
# ENTRY POINT
# ==========================
FAST_BACKDROP_PANEL = None

def show_fast_backdrop():
    if not nuke.selectedNodes():
        nuke.message("FastBackdrop: Please select some nodes first.")
        return

    global FAST_BACKDROP_PANEL

    if FAST_BACKDROP_PANEL is not None:
        try:
            FAST_BACKDROP_PANEL.close()
        except:
            pass

    FAST_BACKDROP_PANEL = FastBackdropPanel()
    FAST_BACKDROP_PANEL.show()
