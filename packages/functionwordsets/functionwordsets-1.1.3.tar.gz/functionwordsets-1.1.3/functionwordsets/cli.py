\"\"\"Command-line interface for *functionwords*.\"\"\"

import argparse, json, sys
from ._loader import load, available_ids

def list_sets() -> None:
    \"\"\"Print available dataset IDs, one per line.\"\"\"
    print(*available_ids(), sep=\"\\n\")

def export_set() -> None:
    \"\"\"Export a dataset (or subset) to stdout or a file.\"\"\"
    p = argparse.ArgumentParser(
        description=\"Export function-word lists.\"
    )
    p.add_argument(\"set_id\", choices=available_ids(),
                   help=\"Dataset ID, e.g. fr_21c\")
    p.add_argument(\"-o\", \"--out\", default=\"-\",
                   help=\"Output path, or - for stdout [default].\")
    p.add_argument(\"--include\", nargs=\"+\",
                   help=\"Categories to include (space-separated).\")
    args = p.parse_args()

    fw = load(args.set_id)
    try:
        data = sorted(fw.subset(args.include)) if args.include else sorted(fw.all)
    except KeyError as e:
        p.error(f\"unknown category: {e.args[0]}\")  # nice argparse message

    if args.out == \"-\":
        print(*data, sep=\"\\n\")
    else:
        with open(args.out, \"w\", encoding=\"utf-8\") as f:
            if args.out.endswith(\".json\"):
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                f.write(\"\\n\".join(data))
        sys.stderr.write(f\"Wrote {len(data)} entries to {args.out}\\n\")
