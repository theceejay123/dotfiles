# pylint: disable=C0111,R0903

"""Displays information about the current song in cmus.

Requires the following executable:
    * cmus-remote

Parameters:
    * cmus.format: Format string for the song information. Tag values can be put in curly brackets (i.e. {artist})
    * cmus.layout: Space-separated list of widgets to add. Possible widgets are the buttons/toggles cmus.prev, cmus.next, cmus.shuffle and cmus.repeat, and the main display with play/pause function cmus.main.
"""

from collections import defaultdict

import string

import bumblebee.util
import bumblebee.input
import bumblebee.output
import bumblebee.engine

from bumblebee.output import scrollable

class Module(bumblebee.engine.Module):
    def __init__(self, engine, config):
        super(Module, self).__init__(engine, config, [])

        self._layout = self.parameter("layout", "cmus.prev cmus.main cmus.next cmus.shuffle cmus.repeat")
        self._fmt = self.parameter("format", "{artist} - {title} {position}/{duration}")
        self._status = None
        self._shuffle = False
        self._repeat = False
        self._tags = defaultdict(lambda: '')

        # Create widgets
        widget_list = []
        widget_map = {}
        for widget_name in self._layout.split():
            widget = bumblebee.output.Widget(name=widget_name)
            widget_list.append(widget)

            if widget_name == "cmus.prev":
                widget_map[widget] = {"button": bumblebee.input.LEFT_MOUSE, "cmd": "cmus-remote -r"}
            elif widget_name == "cmus.main":
                widget_map[widget] = {"button": bumblebee.input.LEFT_MOUSE, "cmd": "cmus-remote -u"}
                widget.full_text(self.description)
            elif widget_name == "cmus.next":
                widget_map[widget] = {"button": bumblebee.input.LEFT_MOUSE, "cmd": "cmus-remote -n"}
            elif widget_name == "cmus.shuffle":
                widget_map[widget] = {"button": bumblebee.input.LEFT_MOUSE, "cmd": "cmus-remote -S"}
            elif widget_name == "cmus.repeat":
                widget_map[widget] = {"button": bumblebee.input.LEFT_MOUSE, "cmd": "cmus-remote -R"}
            else:
                raise KeyError("The cmus module does not support a {widget_name!r} widget".format(widget_name=widget_name))
        self.widgets(widget_list)

        # Register input callbacks
        for widget, callback_options in widget_map.items():
            engine.input.register_callback(widget, **callback_options)

    def hidden(self):
        return self._status is None

    @scrollable
    def description(self, widget):
        return string.Formatter().vformat(self._fmt, (), self._tags)

    def update(self, widgets):
        self._load_song()

    def state(self, widget):
        returns = {
            "cmus.shuffle": "shuffle-on" if self._shuffle else "shuffle-off",
            "cmus.repeat": "repeat-on" if self._repeat else "repeat-off",
            "cmus.prev": "prev",
            "cmus.next": "next",
        }
        return returns.get(widget.name, self._status)

    def _eval_line(self, line):
        name, key, value = (line.split(" ", 2) + [None, None])[:3]

        if name == "status":
            self._status = key
        if name == "tag":
            self._tags.update({key: value})
        if name in ["duration", "position"]:
            self._tags.update({name: bumblebee.util.durationfmt(int(key))})
        if name == "set" and key == "repeat":
            self._repeat = value == "true"
        if name == "set" and key == "shuffle":
            self._shuffle = value == "true"

    def _load_song(self):
        info = ""
        try:
            info = bumblebee.util.execute("cmus-remote -Q")
        except RuntimeError:
            self._status = None

        self._tags = defaultdict(lambda: '')
        for line in info.split("\n"):
            self._eval_line(line)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
