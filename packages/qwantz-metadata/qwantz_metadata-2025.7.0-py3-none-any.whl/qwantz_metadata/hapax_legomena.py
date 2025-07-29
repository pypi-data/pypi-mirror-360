import json
import re
import sys
from collections import Counter
from typing import Iterator

from qwantz_metadata.utils import get_words_from_line


def get_words_from_comic(comic) -> Iterator[str]:
    for panel in comic["panels"]:
        for line in panel:
            yield from get_words_from_line(line)


def main():
    comics = json.load(sys.stdin)
    ryan_comics = [comic for comic in comics if comic["guest_artist"] is None]
    all_words = Counter(word for comic in ryan_comics for word in get_words_from_comic(comic))
    hapax_legomena = set(word for word, count in all_words.items() if count == 1)
    for comic in ryan_comics:
        comic_words = set(get_words_from_comic(comic))
        for hapax in comic_words & hapax_legomena:
            print(comic["comic_id"], hapax)


if __name__ == '__main__':
    main()
