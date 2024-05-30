import os
import shutil
from glob import glob
from itertools import product
from os.path import join, isfile, exists
from pathlib import Path

from tqdm import tqdm
from mutagen import File


ARTIST_DIR = "/mnt/d/music/artist"
DEFAULT_MUSIC_ALBUM = "single"
DEFAULT_VIDEO_ALBUM = "video"
DEFAULT_ALBUMS = (DEFAULT_MUSIC_ALBUM, DEFAULT_VIDEO_ALBUM)
REMOVE_WORDS = ["xfd", "trailer", "teaser"]
REMIX_WORDS = ["remix", "live"]
INCOMING_DIR = "incoming"


def set_tags_album(artist: str, album: str, date: str = None, deduplication: bool = True) -> None:
    # 1. Set tags
    root_path = get_valid_path(join(ARTIST_DIR, artist))
    incoming_files = get_files(root_path)
    for file in tqdm(incoming_files):
        tags = {"artist": artist, "album": album}
        if date:
            tags["date"] = date
        
        try:
            set_tags(file, tags)
        except Exception as e:
            print(e)
            continue
    print("[success] Set tags")

    # 2. Deduplication
    incoming_infos = get_infos(root_path, "incoming")
    existing_infos = get_infos(root_path, "existing")
    if deduplication:
        deduplicate(incoming_infos, existing_infos)

    # 3. Move incoming files to album directory
    for info in tqdm(incoming_infos):
        if exists(info["file"]):
            album_dir = join(root_path, info["album"])
            os.makedirs(album_dir, exist_ok=True)
            shutil.move(info["file"], album_dir)
    print("[success] Move incoming files to album directory")



def get_valid_path(path: str) -> str:
    p = Path(path)
    parent = p.parent
    name = p.name
    for char in ("\\", "/", ":", "*", "\"", "<", ">", "|"):
        valid_name = name.replace(char, "")
    return join(parent, valid_name)


def get_files(root_path: str) -> list[str]:
    return list(filter(isfile, glob(join(root_path, "*"))))


def get_infos(root_path: str, type: str) -> list[dict]:
    if type == "incoming":
        all_files = get_files(root_path)
    elif type == "existing":
        all_files = get_files(join(root_path, "*"))
    else:
        raise ValueError(f"Invalid type: {type}")
    return list(map(get_info, filter(isfile, all_files)))


def set_tags(file: str, tags: dict) -> bool:
    audio = File(file)
    if not audio:
        raise ValueError(f"Invalid file: {file}")
    audio.tags.update(tags)
    audio.save()


def deduplicate(incoming_infos: list[dict], existing_infos: list[dict]) -> None:
    for inc_info, ext_info in tqdm(list(product(incoming_infos, existing_infos))):
        if inc_info == ext_info:
            continue
        
        if check_duplicate(inc_info, ext_info):
            inc_default_album = inc_info["album"] in DEFAULT_ALBUMS
            ext_default_album = ext_info["album"] in DEFAULT_ALBUMS
            try:
                if inc_default_album and ext_default_album:
                    os.remove(inc_info["file"])
                elif inc_default_album and not ext_default_album:
                    os.remove(inc_info["file"])
                elif not inc_default_album and ext_default_album:
                    os.remove(ext_info["file"])
                elif not inc_default_album and not ext_default_album:
                    os.remove(inc_info["file"])
                else:
                    raise ValueError("This condition should not be reached.")
            except Exception as e:
                print(e)
                print("Error in", inc_info["file"], ext_info["file"])

def check_duplicate(inc_info: dict, ext_info: dict) -> bool:
    inc_title, ext_title = inc_info["title"].lower(), ext_info["title"].lower()
    cond_dup = inc_title == ext_title
    cond_inc = ext_title in inc_title
    cond_remix = any(remix_word in inc_title for remix_word in REMIX_WORDS)
    if cond_dup or (cond_inc and not cond_remix):
        return True
    else:
        return False


def get_info(file: str) -> dict:
    audio = File(file)
    if audio:
        tags = audio.tags
    else:
        raise ValueError(f"Invalid file: {file}")
    
    tags = {"title": tags["title"][0], "album": tags["album"][0], "date": tags.get("date", [None])[0]}
    artist, *_, name = file.removeprefix(ARTIST_DIR + "/").split("/")
    tags.update({"file": file, "artist": artist, "name": name})
    return tags
