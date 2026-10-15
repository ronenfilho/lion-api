"""Carrega o corpus de exemplo (`data/sample/*.md`) numa API em execução.

Uso: python scripts/load_sample.py [URL_BASE]   (padrão: http://localhost:8000)
"""

import sys
from pathlib import Path

import httpx

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"


def parse(path: Path) -> dict[str, str]:
    """Lê o front matter simples (title/source) e o corpo do arquivo."""
    _, header, body = path.read_text(encoding="utf-8").split("---", 2)
    meta = dict(line.split(": ", 1) for line in header.strip().splitlines())
    return {"title": meta["title"], "source": meta["source"], "content": body.strip()}


def main(base_url: str) -> None:
    for path in sorted(SAMPLE_DIR.glob("*.md")):
        response = httpx.post(f"{base_url}/documents", json=parse(path), timeout=30)
        response.raise_for_status()
        doc = response.json()
        print(f"#{doc['id']} {doc['title']} ({doc['chunk_count']} trechos)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000")
