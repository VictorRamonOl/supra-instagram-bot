"""
approve_batch.py - Aprova ou rejeita posts em /pending/ em lote.

Uso:
  python approve_batch.py --ids 01,03,07           # move esses pra /approved/
  python approve_batch.py --reject 02,05           # apaga esses
  python approve_batch.py --all                    # aprova todos pendentes
"""
import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
PENDING_DIR = PROJECT_ROOT / "content" / "pending"
APPROVED_DIR = PROJECT_ROOT / "content" / "approved"


def find_post_dir(post_id: str) -> Path | None:
    for d in PENDING_DIR.iterdir():
        if d.is_dir() and d.name.startswith(f"{post_id}_"):
            return d
    return None


def approve(post_id: str) -> bool:
    src = find_post_dir(post_id)
    if not src:
        print(f"  [erro] Post #{post_id} nao encontrado em pending/")
        return False
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    dst = APPROVED_DIR / src.name
    if dst.exists():
        print(f"  [erro] Ja existe em approved/: {dst.name}")
        return False
    shutil.move(str(src), str(dst))
    print(f"  [ok] Aprovado: {src.name}")
    return True


def reject(post_id: str) -> bool:
    src = find_post_dir(post_id)
    if not src:
        print(f"  [aviso] Post #{post_id} nao encontrado (talvez ja rejeitado)")
        return False
    shutil.rmtree(src)
    print(f"  [ok] Rejeitado e apagado: {src.name}")
    return True


def list_pending_ids() -> list[str]:
    return sorted(d.name.split("_")[0] for d in PENDING_DIR.iterdir() if d.is_dir())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", default="", help="IDs a aprovar (ex: 01,03,07)")
    parser.add_argument("--reject", default="", help="IDs a rejeitar/apagar")
    parser.add_argument("--all", action="store_true", help="Aprovar todos pendentes")
    args = parser.parse_args()

    if not args.ids and not args.reject and not args.all:
        print("Nada a fazer. Use --ids, --reject ou --all.")
        sys.exit(1)

    if args.all:
        all_ids = list_pending_ids()
        print(f"\nAprovando todos os {len(all_ids)} posts pendentes...")
        for pid in all_ids:
            approve(pid)

    if args.ids:
        ids = [x.strip() for x in args.ids.split(",") if x.strip()]
        print(f"\nAprovando {len(ids)} posts...")
        for pid in ids:
            approve(pid)

    if args.reject:
        ids = [x.strip() for x in args.reject.split(",") if x.strip()]
        print(f"\nRejeitando {len(ids)} posts...")
        for pid in ids:
            reject(pid)

    print("\nResumo:")
    pending = sorted([d.name for d in PENDING_DIR.iterdir() if d.is_dir()])
    approved = sorted([d.name for d in APPROVED_DIR.iterdir() if d.is_dir()]) if APPROVED_DIR.exists() else []
    print(f"  Pendentes ({len(pending)}): {pending}")
    print(f"  Aprovados ({len(approved)}): {approved}")


if __name__ == "__main__":
    main()
