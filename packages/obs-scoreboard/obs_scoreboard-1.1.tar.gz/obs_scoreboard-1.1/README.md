# obs-scoreboard
![GitHub Release #](https://img.shields.io/github/v/release/gsl4295/scores?include_prereleases&sort=date&display_name=tag)
![GitHub Commits](https://img.shields.io/github/commit-activity/t/gsl4295/scores)
![GitHub Issues](https://img.shields.io/github/issues/gsl4295/scores)<br>
Simple python-powered scoreboard for use with my online webcasts.

<img src="scores/images/GUI.png" width=500 /><br>

### Setup
- This program is available on pip:
```commandline
pip install obs-scoreboard
```

### Features
- User-inputted:
  - Team names
  - Team colors
  - Score
    - +1, -1, or by text input

| Hotkeys  | Team 1  | Team 2  |
|:--------:|:-------:|:-------:|
| Score +1 | numpad7 | numpad9 |
| Score -1 | numpad1 | numpad3 |

- Streaming-friendly outputs
  - Background (for using color key): `#252526`
  - Find an example of how I'm using this program in `images/OBS-overlay-example.png`
  - This program also outputs each score and team name to its respective text file in `outputs/`
  - To update a text source with this data, set "Add Data Mode" to "from file" and find the files in this project.
