#file: savegame.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains the savegame screen.

import pygame

from code import g
from code.graphics import dialog, button, slider, text, constants, listbox, g as gg

class SavegameScreen(dialog.ChoiceDialog):
    def __init__(self, parent, *args, **kwargs):
        super(SavegameScreen, self).__init__(parent, *args, yes_type="load", **kwargs)

        self.yes_button.exit_code_func = self.return_savegame
        self.no_button.exit_code = None

    def show(self):
        save_names = g.get_save_names()
        save_names.sort(key=str.lower)
        self.list = save_names

        return super(SavegameScreen, self).show()

    def return_savegame(self):
        index = self.return_list_pos()
        if 0 <= index < len(self.list):
            save = self.list[index]
            return g.load_game(save)
        return False
