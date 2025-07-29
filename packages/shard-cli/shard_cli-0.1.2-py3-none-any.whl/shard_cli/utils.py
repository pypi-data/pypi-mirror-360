############
# utils.py #
############

def slugify(title: str) -> str:
    title = title.lower()
    title = re.sub(r"\s+", "-", title)
    title = re.sub(r"[^a-z0-9\-]", "", title)
    return title

def generate_note_id(date_format: str) -> str:
    return datetime.now().strftime(date_format)
