"""Generate icons.py file from popular web fonts."""

import tkinter as tk
from xml.etree import ElementTree

import tksvg  # type: ignore[import-untyped]

from tk_font_icons import feather, phosphor
from tk_font_icons import font_awesome as fa

ElementTree.register_namespace('', 'http://www.w3.org/2000/svg')

# https://fontawesome.com/search

icon_fa = fa.load_icon(
    'fontawesome-free-6.5.1-desktop.zip',
    'github',
    fill='#691E7C',
    stroke='#000000',
)
icon_feather = feather.load_icon(
    'feather.zip', 'arrow-up-circle', fill='#1E7C26', stroke='#691E7C',
)
icon_phosphor = phosphor.load_icon(
    'phosphor-icons.zip',
    'sword',
    style='regular',
    flat=True,
    fill='#8A185A',
    stroke='#691E7C',
)

root = tk.Tk()

scale_to_width = scale_to_height = None
scale = 1
scale_to_width = 64

kwargs = {}
if scale_to_width:
    kwargs['scaletowidth'] = scale_to_width
if scale_to_height:
    kwargs['scaletoheight'] = scale_to_height
if scale != 1:
    kwargs['scale'] = scale

img_fa = tksvg.SvgImage(name='icon_github', data=icon_fa, **kwargs)
img_feather = tksvg.SvgImage(name='icon_arrow', data=icon_feather, **kwargs)
img_phosphor = tksvg.SvgImage(name='icon_sword', data=icon_phosphor, **kwargs)

label = tk.Label(root, image='icon_github')
label.pack()
label = tk.Label(root, image='icon_arrow')
label.pack()
label = tk.Label(root, image='icon_sword')
label.pack()

root.mainloop()
