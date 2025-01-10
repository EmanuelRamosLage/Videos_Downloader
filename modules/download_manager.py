import yt_dlp

import logging          as log
import traceback        as trace

from modules                 import settings
from modules.bytes_formatter import bytes_formatter
from pathlib                 import Path

# GLOBAL VARS FOR THIS MODULE
logger = log.getLogger()

video_path: Path        = Path()
total_downloaded: int   = 0
video_size: int         = 0
eta: int                = 0
speed: int              = 0

def yt_dlp_monitor(progress_hooks: dict):
    '''progress_hooks:    
    A list of functions that get called on download
    progress, with a dictionary with the entries
    * status: One of "downloading", "error", or "finished".
    Check this first and ignore unknown values.

    If status is one of "downloading", or "finished", the
    following properties may also be present:
    * filename: The final filename (always present)
    * tmpfilename: The filename we're currently writing to
    * downloaded_bytes: Bytes on disk
    * total_bytes: Size of the whole file, None if unknown
    * total_bytes_estimate: Guess of the eventual file size, None if unavailable.
    * elapsed: The number of seconds since download started.
    * eta: The estimated time in seconds, None if unknown
    * speed: The download speed in bytes/second, None if unknown
    * fragment_index: The counter of the currently downloaded video fragment.
    * fragment_count: The number of fragments (= individual files that will be merged)

    Progress hooks are guaranteed to be called at least once (with status "finished") if the download is successful.
    '''
    global video_path
    global total_downloaded
    global video_size
    global speed
    global eta

    video_path          = Path(progress_hooks.get('info_dict', {}).get('filename'))
    total_downloaded    = progress_hooks.get('downloaded_bytes', 0)
    video_size          = progress_hooks.get('total_bytes',      0)
    speed               = progress_hooks.get('speed',            0)
    eta                 = progress_hooks.get('eta',              0)

def download_videos(videos: dict[str, dict], monitors: list = []):
    logger.info(f'Starting to download {len(videos)}.')
    print('Press Ctrl-C at any time to stop it.')

    global video_path
    global video_size

    callables = [yt_dlp_monitor]
    for func in monitors:
        if callable(func):
            callables.append(func) # type: ignore

    resolution = settings.read_sets()['default resolution']
    ytdlp_opts: dict = {
        'outtmpl': '.\\Videos\\Temp\\%(title)s.%(ext)s',
        'format': f'bestvideo[height<={resolution}]+bestaudio/bestvideo[height<={resolution}]/best',
        'progress_hooks': callables,
        'quiet': True
        }
    
    for url, info in videos.copy().items():
        try:
            with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:

                logger.info(f'Downloading the video file of "{info['title']}" with {bytes_formatter(info['size'])} of size.')
                ydl.download(url)
                videos.pop(url)
                yield [url, video_size, video_path]
                
        except Exception:
            logger.warning(f'An error occurred trying to download "{info['title']}": {trace.format_exc()}.')
            continue

def extractor(links: list[str])-> tuple[list[str], dict[str, dict]]:
    '''Extract useful info about the link, such as: title, link and size.'''


    videos: dict[str, dict]    = {}
    links_len: int             = len(links)
    links_done: list[str]      = []

    logger.info(f'Starting to extract {links_len} links.')
    for url in links.copy():
        links_len -= 1
        ytdlp_opts = {'quiet': True, 
                      'skip_download': True,
                      'format': 'best[height<=720]/bestvideo[height<=720]/best',
                      'ignoreerrors': True,
                      }
        try:
            with yt_dlp.YoutubeDL(ytdlp_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                # Check if the URL is a playlist or a single video

                # Wasn't able to get any info
                if info_dict == None:
                    videos[url] = {'size': 0, 'title': 'Nothing', 'id': None}
                # Playlist
                elif 'entries' in info_dict:                                        # type: ignore
                    for entry in info_dict['entries']:                              # type: ignore
                        video_url: str      = entry.get('webpage_url', url)         # type: ignore
                        filesize: int       = entry.get('filesize', 0)              # type: ignore
                        video_id: str       = entry.get('id', None)
                        title: str          = entry.get('title', 'Nothing')         # type: ignore
                        videos[video_url]   = {'size': filesize, 'title': title, 'id': video_id}
                # Video 
                else:
                    video_url: str          = info_dict.get('webpage_url', url)     # type: ignore
                    filesize: int           = info_dict.get('filesize', 0)          # type: ignore
                    video_id: str           = info_dict.get('id', None)
                    title: str              = info_dict.get('title', 'Nothing')     # type: ignore
                    videos[video_url]       = {'size': filesize, 'title': title, 'id': video_id}
        
        except:
            traceback = trace.format_exc()
            logger.warning(f'An error occurred trying to extract "{url}": {traceback}. Skipping.')
            continue
    
        links_done.append(url)
    return links_done, videos

def sorter(videos: dict[str, dict]) -> dict[str, dict]:
    '''Sorts the dict by video's size and set the videos with unknown size (0B) a large number to be the last to download.'''
    sorted_videos: dict[str, dict] = {}
    
    for url, info in videos.copy().items():
        if info['size'] == 0:
            value: tuple = max(videos.items(), key= lambda item: item[1]['size'])
            videos[url]['size'] = value[1]['size'] + 1  


    for url, info in dict(sorted(videos.items(), key= lambda item: item[1]['size'])).items():
        sorted_videos[url] = info


    return sorted_videos