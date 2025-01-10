import json
from pathlib import Path

settings_file = Path('Settings.json')
if not(settings_file.exists()):
    settings_file.touch()

    if settings_file.stat().st_size == 0:
        sets = {'default resolution': '720p',
                'default playlist': ''
        }
        settings_file.write_text(json.dumps(sets, indent= 1))


def read_sets() -> dict:
    return json.loads(settings_file.read_text())