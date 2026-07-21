#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
# ═════════════════════════════════════════════════════════════════════
#
#  UTILITY SKIN
#  Version: 5.4
#  Created by Lululla (https://github.com/Belfagor2005)
#  License: CC BY-NC-SA 4.0
#  https://creativecommons.org/licenses/by-nc-sa/4.0
#
#  Last Modified: "15:14 - 20250423"
#
#  Credits:
#
# 👨‍💻 Original Developers: Lululla
# ✍️ (2024-07-20)
#
# ⚖️ License: GNU General Public License (v2 or later)
#    You must NOT remove credits and must share modified code.
# ═════════════════════════════════════════════════════════════════════

from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from enigma import getDesktop, eLabel
from Screens.Screen import Screen
from Tools.Directories import fileExists
from errno import ENOENT
import sys
from gettext import gettext

_ = gettext

PY3 = sys.version_info[0] >= 3
DEFAULT_MODULE_NAME = __name__.split(".")[-1]

pname = "File Commander - Addon"
pdesc = "play/show Files"
pversion = "1.0-r3"


def getTextBoundarySize(instance, font, targetSize, text):
    return eLabel.calculateTextSize(font, text, targetSize)


def fileReadLines(
        filename,
        default=None,
        source=DEFAULT_MODULE_NAME,
        debug=False):
    lines = None
    try:
        if PY3:
            with open(filename, "r", encoding="utf-8") as fd:
                lines = fd.read().splitlines()
        else:
            with open(filename, "r") as fd:
                lines = fd.read().decode("utf-8").splitlines()
    except (OSError, IOError) as err:
        if err.errno != ENOENT:
            print("[%s] Error %d: Unable to read lines from file '%s'!  (%s)" %
                  (source, err.errno, filename, err.strerror))
        lines = default
    except UnicodeDecodeError:
        try:
            with open(filename, "r") as fd:
                lines = fd.read().splitlines()
        except BaseException:
            lines = default
    return lines


def getDesktopSize():
    s = getDesktop(0).size()
    return (s.width(), s.height())


def _build_skin():
    # Base FHD (1920x1080) – valori di riferimento
    base = {
        "screen_w": 1920, "screen_h": 1080,
        "head_x": 8, "head_y": 10, "head_w": 1850, "head_h": 45, "head_font": 32,
        "btn_w": 260, "btn_h": 40, "btn_y": 935, "btn_font": 24,
        "btn_x_red": 95, "btn_x_green": 395, "btn_x_yellow": 690, "btn_x_blue": 985,
        "pixmap_y": 975, "pixmap_w": 260, "pixmap_h": 25,
        "pixmap_x_red": 95, "pixmap_x_green": 395, "pixmap_x_yellow": 690, "pixmap_x_blue": 985,
        "list_x": 45, "list_y": 115, "list_w": 1830, "list_h": 810,
        "list_itemHeight": 45, "list_font": 30
    }

    desktop_w, desktop_h = getDesktopSize()

    if desktop_w >= 3840:
        scale = 2.0
    elif desktop_w >= 2560:
        scale = 1.3333
    elif desktop_w >= 1920:
        scale = 1.0
    else:
        scale = 0.6667   # HD

    def s(v):
        return int(round(v * scale))

    params = {
        "screen_w": s(base["screen_w"]),
        "screen_h": s(base["screen_h"]),
        "head_x": s(base["head_x"]),
        "head_y": s(base["head_y"]),
        "head_w": s(base["head_w"]),
        "head_h": s(base["head_h"]),
        "head_font": s(base["head_font"]),
        "btn_w": s(base["btn_w"]),
        "btn_h": s(base["btn_h"]),
        "btn_y": s(base["btn_y"]),
        "btn_font": s(base["btn_font"]),
        "btn_x_red": s(base["btn_x_red"]),
        "btn_x_green": s(base["btn_x_green"]),
        "btn_x_yellow": s(base["btn_x_yellow"]),
        "btn_x_blue": s(base["btn_x_blue"]),
        "pixmap_y": s(base["pixmap_y"]),
        "pixmap_w": s(base["pixmap_w"]),
        "pixmap_h": s(base["pixmap_h"]),
        "pixmap_x_red": s(base["pixmap_x_red"]),
        "pixmap_x_green": s(base["pixmap_x_green"]),
        "pixmap_x_yellow": s(base["pixmap_x_yellow"]),
        "pixmap_x_blue": s(base["pixmap_x_blue"]),
        "list_x": s(base["list_x"]),
        "list_y": s(base["list_y"]),
        "list_w": s(base["list_w"]),
        "list_h": s(base["list_h"]),
        "list_itemHeight": s(base["list_itemHeight"]),
        "list_font": s(base["list_font"]),
    }

    # Template XML – usiamo le variabili
    skin_xml = """
<screen name="File_Commander" position="center,center" size="{screen_w},{screen_h}" title="Lululla Commander" flags="wfNoBorder">
    <widget name="list_head" position="{head_x},{head_y}" size="{head_w},{head_h}" font="Regular;{head_font}" foregroundColor="#00fff000" />

    <widget name="key_red" position="{btn_x_red},{btn_y}" zPosition="19" size="{btn_w},{btn_h}" transparent="1" font="Regular;{btn_font}" halign="center" />
    <widget name="key_green" position="{btn_x_green},{btn_y}" zPosition="19" size="{btn_w},{btn_h}" transparent="1" font="Regular;{btn_font}" halign="center" />
    <widget name="key_yellow" position="{btn_x_yellow},{btn_y}" zPosition="19" size="{btn_w},{btn_h}" transparent="1" font="Regular;{btn_font}" halign="center" />
    <widget name="key_blue" position="{btn_x_blue},{btn_y}" zPosition="19" size="{btn_w},{btn_h}" transparent="1" font="Regular;{btn_font}" halign="center" />

    <ePixmap position="{pixmap_x_red},{pixmap_y}" size="{pixmap_w},{pixmap_h}" zPosition="0" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
    <ePixmap position="{pixmap_x_green},{pixmap_y}" size="{pixmap_w},{pixmap_h}" zPosition="0" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
    <ePixmap position="{pixmap_x_yellow},{pixmap_y}" size="{pixmap_w},{pixmap_h}" zPosition="0" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
    <ePixmap position="{pixmap_x_blue},{pixmap_y}" size="{pixmap_w},{pixmap_h}" zPosition="0" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />

    <widget name="filedata" position="{list_x},{list_y}" size="{list_w},{list_h}" itemHeight="{list_itemHeight}" font="Regular;{list_font}" transparent="1" scrollbarMode="showOnDemand" scrollbarSliderForegroundColor="#ff005826" scrollbarSliderBorderColor="#ff171a1c" scrollbarWidth="10" scrollbarSliderBorderWidth="1" itemCornerRadius="8" valign="center" />
</screen>"""

    return skin_xml.format(**params)


class File_Commander(Screen):

    def __init__(self, session, file):
        self.skin = _build_skin()
        Screen.__init__(self, session)
        self.file_name = file
        title = "Lululla File Commander"
        self.newtitle = 'Console' if title == 'vEditorScreen' else title
        self.list = []
        self["filedata"] = MenuList(self.list)
        self["actions"] = ActionMap(["WizardActions", "ColorActions", "DirectionActions"], {
            "ok": self.edit_Line,
            "green": self.SaveFile,
            "back": self.exitEditor,
            "red": self.exitEditor,
            "yellow": self.del_Line,
            "blue": self.ins_Line,
        }, -1)
        self["list_head"] = Label(self.file_name)
        self["key_red"] = Label(_("Exit"))
        self["key_green"] = Label(_("Save"))
        self["key_yellow"] = Label(_("Del Line"))
        self["key_blue"] = Label(_("Ins Line"))
        self.selLine = None
        self.oldLine = None
        self.isChanged = False
        self.GetFileData(file)
        self.setTitle(self.newtitle)

    def exitEditor(self):
        self.close()

    def GetFileData(self, fx):
        lines = fileReadLines(fx)
        if lines:
            for idx, line in enumerate(lines):
                if not PY3 and isinstance(line, bytes):
                    try:
                        line = line.decode("utf-8")
                    except BaseException:
                        line = line.decode("latin-1")
                self.list.append(str(idx + 1).zfill(4) + ": " + line)
            self["filedata"].setList(self.list)
        self["list_head"].setText(fx)

    def posStart(self):
        self.selLine = 0
        self["filedata"].moveToIndex(0)

    def posEnd(self):
        if self.list:
            self.selLine = len(self.list) - 1
            self["filedata"].moveToIndex(self.selLine)

    def edit_Line(self):
        self.selLine = self["filedata"].getSelectionIndex()
        if self.selLine is not None and 0 <= self.selLine < len(self.list):
            current_line_full = self.list[self.selLine]
            colon_pos = current_line_full.find(": ", 4)
            if colon_pos != -1:
                current_line_text = current_line_full[colon_pos + 2:]
            else:
                current_line_text = current_line_full

            from Screens.VirtualKeyBoard import VirtualKeyBoard
            self.session.openWithCallback(
                self.VirtualKeyBoardCallback,
                VirtualKeyBoard,
                title=_("Edit Line"),
                text=current_line_text)

    def VirtualKeyBoardCallback(self, callback=None):
        if callback is not None:
            line_num = self.list[self.selLine][:6]  # Prendi "0001: "
            self.list[self.selLine] = line_num + callback
            self.isChanged = True
            self["filedata"].setList(self.list)
            self["filedata"].moveToIndex(self.selLine)

    def del_Line(self):
        self.selLine = self["filedata"].getSelectionIndex()
        if self.selLine is not None and len(self.list) > 0:
            self.isChanged = True
            del self.list[self.selLine]
            self.refreshList()
            if self.selLine >= len(self.list):
                self.selLine = len(self.list) - 1
            if self.selLine >= 0:
                self["filedata"].moveToIndex(self.selLine)

    def ins_Line(self):
        self.selLine = self["filedata"].getSelectionIndex()
        if self.selLine is None:
            self.selLine = len(self.list)
        self.list.insert(self.selLine, "0000: " + "")
        self.isChanged = True
        self.refreshList()
        self["filedata"].moveToIndex(self.selLine)

    def refreshList(self):
        new_list = []
        for idx, line in enumerate(self.list):
            if ": " in line:
                text_part = line.split(": ", 1)[1]
            else:
                text_part = line
            new_list.append(str(idx + 1).zfill(4) + ": " + text_part)
        self.list = new_list
        self["filedata"].setList(self.list)

    def SaveFile(self):
        try:
            if fileExists(self.file_name):
                import shutil
                shutil.copy(self.file_name, self.file_name + ".bak")

            mode = "w"
            encoding = "utf-8"

            if PY3:
                with open(self.file_name, mode, encoding=encoding) as eFile:
                    for x in self.list:
                        if isinstance(x, tuple):
                            x = x[0]
                        if ": " in x:
                            text_to_save = x.split(": ", 1)[1]
                        else:
                            text_to_save = x
                        eFile.write(text_to_save + "\n")
            else:
                with open(self.file_name, mode) as eFile:
                    for x in self.list:
                        if isinstance(x, tuple):
                            x = x[0]
                        if ": " in x:
                            text_to_save = x.split(": ", 1)[1]
                        else:
                            text_to_save = x
                        eFile.write(str(text_to_save) + "\n")

            self.isChanged = False

        except (OSError, IOError) as e:
            print("Error saving file:", str(e))
        self.close()
