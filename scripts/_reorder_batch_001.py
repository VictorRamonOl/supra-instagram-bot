"""Renomeia pastas em content/pending/ para nova ordem de publicacao (Wed 03/06 inicio)."""
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PENDING = PROJECT_ROOT / "content" / "pending"

# (slug, new_id, new_date)
NEW_ORDER = [
    ("mobiliario-5-erros",      "01", "2026-06-03"),  # Qua catálogo
    ("logistica-interior-am",   "02", "2026-06-05"),  # Sex regional
    ("pdde-guia-rapido",        "03", "2026-06-08"),  # Seg técnico
    ("brinquedo-3-perguntas",   "04", "2026-06-10"),  # Qua catálogo
    ("censo-escolar-am",        "05", "2026-06-12"),  # Sex regional
    ("srm-resolucao-fnde",      "06", "2026-06-15"),  # Seg técnico
    ("lousa-projetor-tv",       "07", "2026-06-17"),  # Qua catálogo
    ("srm-subutilizada",        "08", "2026-06-19"),  # Sex regional
    ("educacao-conectada",      "09", "2026-06-22"),  # Seg técnico
    ("compras-publicas-2026",   "10", "2026-06-24"),  # Qua catálogo
    ("5-perguntas-fornecedor",  "11", "2026-06-26"),  # Sex regional
    ("cantinho-leitura-7030",   "12", "2026-06-29"),  # Seg técnico
]


def main():
    # Pass 1: encontra todas as pastas e renomeia para TMP_*
    folders = {}
    for d in PENDING.iterdir():
        if d.is_dir():
            slug = "_".join(d.name.split("_")[2:])
            folders[slug] = d

    tmp_paths = {}
    for d in folders.values():
        tmp = d.parent / f"TMP_{d.name}"
        d.rename(tmp)
        tmp_paths[d.name] = tmp

    # Pass 2: renomeia TMP_* para final
    for slug, new_id, new_date in NEW_ORDER:
        # Acha pasta TMP correspondente ao slug
        match = None
        for old_name, tmp_path in tmp_paths.items():
            if old_name.endswith(slug):
                match = (old_name, tmp_path)
                break
        if not match:
            print(f"[ATENCAO] Slug nao encontrado: {slug}")
            continue
        old_name, tmp_path = match
        new_name = f"{new_id}_{new_date}_{slug}"
        new_path = tmp_path.parent / new_name
        tmp_path.rename(new_path)

        # Atualiza post.json
        meta_file = new_path / "post.json"
        if meta_file.exists():
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            meta["id"] = new_id
            meta["scheduled_for"] = new_date
            meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  OK: {new_name}")


if __name__ == "__main__":
    main()
