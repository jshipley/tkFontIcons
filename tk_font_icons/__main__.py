"""Generate icons.py file from popular web fonts."""

import tkinter as tk
import xml.etree.ElementTree as ET

import tksvg

ET.register_namespace('', 'http://www.w3.org/2000/svg')

svg = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--! Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free (Icons: CC BY 4.0, Fonts: SIL OFL 1.1, Code: MIT License) Copyright 2023 Fonticons, Inc. --><path d="M0 192C0 103.6 71.6 32 160 32s160 71.6 160 160V320c0 88.4-71.6 160-160 160S0 408.4 0 320V192zM160 96c-53 0-96 43-96 96V320c0 53 43 96 96 96s96-43 96-96V192c0-53-43-96-96-96z"/></svg>')
svg.attrib['fill'] = '#691E7C'

root = tk.Tk()

img = tksvg.SvgImage(name="icon_zero", data=ET.tostring(svg))

label = tk.Label(root, image="icon_zero")
label.pack()

root.mainloop()