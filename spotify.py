# The MIT License (MIT)

# Copyright(c) 2022 Ben Hunt

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from subprocess import CompletedProcess, run
from typing import List

from libqtile.group import _Group
from libqtile.config import Screen

from libqtile.widget import base
from libqtile.log_utils import logger

SPOTIFY = "Spotify"


class Spotify(base.ThreadPoolText):
    """
    A widget to interact with spotify via dbus.
    """

    defaults = [
        ("play_icon", "", "icon to display when playing music"),
        ("pause_icon", "", "icon to display when music paused"),
        ("update_interval", 0.5, "polling rate in seconds"),
        ("format", "{icon} {artist}:{album} - {track}", "Spotify display format"),
    ]

    def __init__(self, **config) -> None:
        # init base class
        super().__init__(text="", **config)
        self.add_defaults(Spotify.defaults)
        self.add_callbacks(
            {
                "Button1": self.toggle_music,
            }
        )

    def _is_proc_running(self, proc_name: str) -> bool:
        # create regex pattern to search for to avoid similar named processes
        pattern = f"{proc_name}$"
        # pgrep will return a string of pids for matching processes
        cmd = ["pgrep", "-fli", pattern]
        proc_out = run(cmd, capture_output=True).stdout.decode(
            "utf-8"
        )

        return proc_out != ""

    def toggle_between_groups(self) -> None:
        """
        remember which group you were on before you switched to spotify
        so you can toggle between the 2 groups
        """
        current_screen: Screen = self.qtile.current_screen
        current_group_info = self.qtile.current_group.info()
        logger.warning(f"current group info: {current_group_info}")
        windows = current_group_info["windows"]
        if SPOTIFY in windows:
            # go to previous group
            logger.warning("going to previous group")
            current_screen.group.get_previous_group().toscreen()
            logger.warning("went to previous group")
        else:
            self.go_to_spotify()

    def go_to_spotify(self) -> None:
        """
        Switch to whichever group has the current spotify instance
        if none exists then we will spawn an instance on the current group
        """
        # spawn spotify if not already running
        if not self._is_proc_running("spotify"):
            self.qtile.spawn("spotify", shell=True)
            return

        all_groups: List[_Group] = self.qtile.groups
        # we need to find the group that has spotify in it
        for group in all_groups:
            info = group.info()
            # get a list of windows for the group.  We look for 'Spotify here'
            windows = info["windows"]
            if SPOTIFY in windows:
                name = group.name
                # switch to 'name' group
                spotify_group = self.qtile.groups_map[name]
                spotify_group.toscreen()
                break

    def poll(self) -> str: # type: ignore
        """Poll content for the text box"""
        vars = {
            "icon": self.pause_icon if self.playing else self.play_icon,
            "artist": self.artist,
            "track": self.song_title,
            "album": self.album,
        }

        return self.format.format(**vars) # type: ignore

    def toggle_music(self) -> None:
        cmd = """
        dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify \
        /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.PlayPause
        """
        run(cmd, shell=True)


    def get_proc_output(self, proc: CompletedProcess) -> str:
        stdout = proc.stdout.decode("utf-8")
        no_spotify = "Error" in stdout
        return (
            ""
            if no_spotify
            else stdout.rstrip()
        )


    @property
    def _meta(self) -> str:
        cmd = """dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify \
            /org/mpris/MediaPlayer2 \
            org.freedesktop.DBus.Properties.Get \
            string:'org.mpris.MediaPlayer2.Player' \
            string:'Metadata'
        """
        proc = run( cmd, shell=True, capture_output=True)

        output: str = proc.stdout.decode("utf-8").replace("'", "ʼ").rstrip()
        return "" if ("org.mpris.MediaPlayer2.spotify" in output) else output

    @property
    def artist(self) -> str:
        cmd ="""
        dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify \
        /org/mpris/MediaPlayer2 \
        org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' \
        string:'Metadata' | grep -m1 'xesam:artist' -b2 | tail -n 1 | grep -o '\".*\"' | \
        sed 's/\"//g' | sed -e 's/&/and/g'
        """
        proc: CompletedProcess = run(cmd,
            shell=True,
            capture_output=True,
        )

        return self.get_proc_output(proc)

    @property
    def song_title(self) -> str:
        cmd = f"""
        echo '{self._meta}' | grep -m1 'xesam:title' -b1 | tail -n1 | grep -o '\".*\"' | \
        sed 's/\"//g' | sed -e 's/&/and/g'
        """
        proc: CompletedProcess = run(cmd,
            shell=True,
            capture_output=True
        )

        return self.get_proc_output(proc)

    @property
    def album(self) -> str:
        cmd =  f"""
        echo '{self._meta}' | grep -m1 'xesam:album' -b1 | tail -n1 | grep -o '\".*\"' | \
        sed 's/\"//g' | sed -e 's/&/and/g'
        """
        proc = run(cmd,
            shell=True,
            capture_output=True,
        )

        return self.get_proc_output(proc)

    @property
    def playing(self) -> bool:
        cmd = """
        dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify \
        /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get \
        string:'org.mpris.MediaPlayer2.Player' string:'PlaybackStatus' | grep -o Playing
        """
        play = run(cmd,
            shell=True,
            capture_output=True,
        ).stdout.decode("utf-8")

        return play != ""
