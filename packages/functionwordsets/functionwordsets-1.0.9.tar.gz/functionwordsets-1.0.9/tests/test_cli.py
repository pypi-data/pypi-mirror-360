import subprocess, sys, json, shutil, importlib.resources as res

def _run(cmd):
    return subprocess.check_output(cmd, text=True).strip()

def test_cli_list_sets():
    out = _run(["fw-list"])
    assert "fr_21c" in out.splitlines()

def test_cli_export_subset(tmp_path):
    out_file = tmp_path / "mini.json"
    _run(["fw-export", "fr_21c",
          "--include", "negations", "coord_conj",
          "-o", str(out_file)])
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert "pas" in data and "et" in data
