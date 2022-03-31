# Spotify
- a Qtile widget for viewing and interacting your current spotify track

![image](https://user-images.githubusercontent.com/45215137/160912874-9f6ebaa4-5b9a-4fda-9fcb-ecc7d04123a9.png)

# Install

- copy the file into `~/.config/qtile/spotify.py` your own `config.py` should be in the same directory

## In config.py

```python
from spotify import Spotify

#...rest of config

# add Spotify to list of widgets
screens = [
    Screen(
            bottom=bar.Bar(
                widgets=[
                    Spotify(), # add config options as you like them
                ],
                size=24,
                # border_width=[2, 0, 2, 0],  # Draw top and bottom borders
                # border_color=["ff00ff", "000000", "ff00ff", "000000"]  # Borders are magenta
            ),
        ),
    ]
]
```

# Customization

| key | default | description |
|-----|---------|-------------|
|play_icon| ''| "icon to display when playing music"|
|pause_icon| ''| "icon to display when music paused"|
|update_interval| 0.5| "polling rate in seconds"|
|format| "{icon} {artist}:{album} - {track}"| "Spotify display format"|

- see also Qtile's built-in [`TextBox`](https://docs.qtile.org/en/stable/manual/ref/widgets.html#libqtile.widget.TextBox) for more keys to customize

# Future
- I would like to eventually merge this into Qtile's built-in widgets but will work on it here until I start that process

# Alternatives

- [Mpris2](https://docs.qtile.org/en/stable/manual/ref/widgets.html#libqtile.widget.Mpris2) a more generic widget that allows you to display music info from any player (audacious, vlc, etc.)
