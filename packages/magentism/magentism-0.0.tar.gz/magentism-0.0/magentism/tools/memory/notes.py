import yaml
from ._logger import logger


try:
    notes = yaml.safe_load(open("notes.yaml")) or {}
except FileNotFoundError:
    notes = None


def write_note(title: str, content: str):
    """Write a note for later use.
    Goal: as to not forget some thought, or interesting piece of information.
    Title must be explicit enough, to easily find relevant notes while browsing titles.
    Content of the note should be rather short (one note should cover a narrow topic).
    """
    logger.debug(f"WRITE_NOTE: {title} (content is {len(content)} bytes)")
    notes[title] = content
    yaml.safe_dump(notes, open("notes.yaml", "w"), sort_keys=False)

def read_note_content(title: str) -> str:
    """Read a note's content.
    """
    logger.debug(f"READ_NOTE: {title}")
    for key, value in notes.items():
        if key.lower().strip() == title.lower().strip():
            return value

def list_notes_titles() -> list[str]:
    """Retrieve the full list of notes titles.
    """
    logger.debug(f"LIST_NOTES_TITLES: {len(notes)}")
    return list(notes)
