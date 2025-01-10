import os
import sys

import logging          as log
import threading        as thr
import traceback        as trace

from modules.bytes_formatter import bytes_formatter
from modules.stray_image     import create_image
from modules                 import gui, settings
from modules.db_manager      import database
from modules                 import download_manager
from pathlib                 import Path
from time                    import perf_counter
from pystray                 import Icon, MenuItem, Menu

# MAIN INITIALIZATION
# logging
logger = log.getLogger()
logger.setLevel(log.INFO)

console_handler = log.StreamHandler()
console_handler.setLevel(log.INFO)

file_handler = log.FileHandler('VideosDownloader.log', encoding='utf-8')
file_handler.setLevel(log.INFO)

formatter = log.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%d.%b.%y %H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.info(f'VideosDownloader by Emanuel. Start of the program.')
logger.addHandler(console_handler)


# Small func
def on_click(icon, item) -> None:
    if str(item) == "Exit":
        terminate.set()
    elif str(item) == 'Show in folder':
        os.startfile(cwd / 'videos/temp')

# Global Variables
cwd: Path     = Path.cwd()
db: database  = database()
terminate     = thr.Event()
noti_img      = create_image()
noti_menu     = Menu(MenuItem("Show in folder", on_click), MenuItem("Exit", on_click))
notification  = Icon("Downloader Monitor", icon= noti_img, title= 'Videos Downloader', menu= noti_menu, visible= True)

# Environment
db.open_db()
if not(cwd.joinpath('./videos/temp').exists()):
    cwd.joinpath('./videos/temp').mkdir(parents= True, exist_ok= True)

# END OF MAIN INITIALIZATION


def exit_program(code: int = 0) -> None:
    notification.stop()
    db.close_db()
    log.shutdown()
    sys.exit(code)

def finish_download(d):
    '''This function is a way to finish the downloader since once started it cannot be closed.'''
    if terminate.is_set():
        notification.title = 'Exiting'
        raise KeyboardInterrupt

def get_convert_db_data() -> tuple[list[str], dict[str, dict]]:
    every_link = db.read_db()

    unextracted_links: list[str]       = []
    extracted_links:   dict[str, dict] = {}

    for tuple_data in every_link:
        if tuple_data[1] == 'Nothing':
            unextracted_links.append(tuple_data[2])
        else:
            extracted_links[tuple_data[2]] = {'size': tuple_data[3], 'title': tuple_data[1], 'id': tuple_data[4]}

    return unextracted_links, extracted_links

def format_seconds(seconds) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def update_tooltip(progress_hooks) -> None:
    video_title         = Path(progress_hooks.get('info_dict', {}).get('filename')).stem
    total_downloaded    = bytes_formatter(progress_hooks.get('downloaded_bytes', 0))
    video_size          = bytes_formatter(progress_hooks.get('total_bytes',      0))
    speed               = bytes_formatter(progress_hooks.get('speed', 0)) + '/s'

    text = f'{video_title[:115]}\n{total_downloaded} / {video_size} - {speed}'[:128]
    notification.title = text

def main() -> None:
    gui.cli_interface(db)

    unextracted_links, videos = get_convert_db_data()

    if playlist:= settings.read_sets()['default playlist']:
        unextracted_links.append(playlist)

    if unextracted_links:
        notification.title = f'Videos Downloader\nExtracting {len(unextracted_links)} {'link' if len(unextracted_links) == 1 else 'links'}.'
        links_2_rm, temp = download_manager.extractor(unextracted_links)
        videos.update(temp)
        videos = download_manager.sorter(videos)
        for link in links_2_rm:
            db.rm_link(link)
        db.save_db()

    for link, value in videos.items():
        db.add_link(link, value['title'], value['size'], value['id'])
    db.save_db()

    for downloaded in download_manager.download_videos(videos, [update_tooltip, finish_download]):

        try:
            downloaded[2].replace('.\\videos\\' + downloaded[2].name)
        except Exception:
            logger.warning(f'An error occurred trying to move "{downloaded[2].name}": {trace.format_exc()}')
            
        db.rm_link(downloaded[0])
        db.save_db()
        logger.info(f'The video "{downloaded[2].name}" was successfully downloaded with {bytes_formatter(downloaded[1])}.')

if __name__ == '__main__':
    try:
        counter_start = perf_counter()

        # Start the notification in a separate thread
        tray_thread = thr.Thread(target=notification.run, daemon=True)
        tray_thread.start()
        

        main()

    except KeyboardInterrupt:
        pass
    except Exception:
        logger.error(f'An critical error occurred: {trace.format_exc()}.')
    finally:
        notification.title = 'Exiting'
        counter_end = perf_counter()
        print()
        logger.info(f'The program finished its tasks in {format_seconds(int(counter_end - counter_start))}.')
        exit_program()