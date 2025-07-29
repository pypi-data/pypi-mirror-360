###############
# commands.py #
###############

import typer
from typing import Optional
from pathlib import Path
from datetime import datetime
from shard.utils import slugify, generate_note_id
import re

app = typer.Typer()



@app.command()
def new(
    title: str = typer.Argument(..., help="Title of the note"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags"),
    kasten: Optional[int] = typer.Option(None, "--kasten", "-k", help="Kasten ID"),
    links: Optional[str] = typer.Option(None, "--links", "-l", help="Comma-separated linked note IDs or names"),
):
    # Load your config here (or pass it in)
    from shard.config import load_or_create_config
    config = load_or_create_config()

    # Parse flags
    tags_list = tags.split(",") if tags else []
    links_list = links.split(",") if links else []

    note_id = generate_note_id(config["general"]["date_format"])
    filename = f"{slugify(title)}.md"
    vault_path = config["vault_path"]
    note_path = vault_path / filename

    kasten_name = config.get("kasten", {}).get(str(kasten), "Unknown") if kasten else "Unassigned"

    # Compose frontmatter
    frontmatter = [
        "---",
        f"id: {note_id}",
        f"title: {title}",
        f"tags: [{', '.join(tags_list)}]",
        f"kasten: {kasten_name}",
        f"links: [{', '.join(links_list)}]",
        f"created: {datetime.now().isoformat()}",
        "---\n",
    ]

    content = "\n".join(frontmatter) + f"# {title}\n\n"

    vault_path.mkdir(parents=True, exist_ok=True)
    note_path.write_text(content)

    typer.echo(f"Created note: {note_path}")

if __name__ == "__main__":
    app()
