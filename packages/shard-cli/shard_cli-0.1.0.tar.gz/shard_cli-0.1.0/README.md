# 🧩 Shard

**Shard** is a terminal companion for your `Obsidian.md` vault.  
Quickly create notes, access daily entries, search, and push your vault to Git – all from the command line.

---

## 🚀 Features

- 📄 Create new notes with frontmatter
- 📅 Manage daily notes
- 🔍 Search notes by title
- 🏷️ List tags across your vault
- ⛓️ View backlinks to any note
- ☁️ Push changes to a Git repo with one command

---

## 📦 Installation

### Using pip (via PyPI):

```bash
pip install shard
````

### Using Poetry (local development):

```bash
git clone https://codeberg.org/WolfQuery/shard
cd shard
poetry install
```

---

## 🔧 Usage

```bash
shard new "My Project Idea" --tags project,cli
shard daily
shard search "zettel"
shard tags
shard backlinks zettelkasten.md
shard push
```

You can also pass a custom commit message:

```bash
shard push -m "added new zettel on memory systems"
```

---

## 📂 Vault Setup

By default, `shard` looks for your Obsidian vault in `~/vault/`.

You can customize this in a future config file at:

```bash
~/.config/shard/config.toml
```

---

## 💻 Requirements

* Python 3.9+
* Git (installed and initialized in your vault)
* Optional: `fzf` for fuzzy search

---

## 📖 License

CC BY-NC-SA 4.0 © 2025 WolfQuery