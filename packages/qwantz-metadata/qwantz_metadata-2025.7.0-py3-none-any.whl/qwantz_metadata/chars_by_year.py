import json
import sys
from typing import Iterator

from qwantz_metadata.utils import strip_line


def get_chars_from_comic(comic) -> Iterator[str]:
    for panel in comic["panels"]:
        for line in panel:
            yield from strip_line(line)


def main():
    comics = json.load(sys.stdin)
    ryan_comics = [comic for comic in comics if comic["guest_artist"] is None]
    char_appearances = {}
    for comic in ryan_comics:
        comic_chars = set(get_chars_from_comic(comic))
        for new_char in comic_chars - set(char_appearances):
            char_appearances[new_char] = comic["comic_id"]
    for char, first_id in sorted(char_appearances.items()):
        if first_id <= 14277:
            print(char, first_id)


if __name__ == '__main__':
    main()
