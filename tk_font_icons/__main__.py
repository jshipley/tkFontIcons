"""Generate icons.py file from popular web fonts."""

import tkinter as tk
from xml.etree import ElementTree

import tksvg  # type: ignore[import-untyped]

from tk_font_icons.font_awesome import load_icon

ElementTree.register_namespace('', 'http://www.w3.org/2000/svg')

# https://fontawesome.com/search

icon = load_icon('fontawesome-free-6.5.1-desktop', 'github', fill='#691E7C')

root = tk.Tk()

img = tksvg.SvgImage(name='icon_github', data=icon)

label = tk.Label(root, image='icon_github')
label.pack()

root.mainloop()
