"""CLI exit status and temporary-file cleanup without loading real model weights."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CLIScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="m4-cli-check-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "CLI With Spaces"
        self.root.mkdir()
        for script in ("generate.sh", "edit.sh"):
            shutil.copyfile(ROOT / script, self.root / script)
        for directory in ("bin", "outputs", "logs", "commands"):
            (self.root / directory).mkdir()
        native = self.root / "bin/sd-cli"
        native.write_text('#!/bin/bash\nexit 17\n')
        native.chmod(0o755)
        sips = self.root / "commands/sips"
        sips.write_text('''#!/bin/bash
if [ "$1" = "-g" ]; then
  printf 'pixelWidth: 768\npixelHeight: 768\n'
else
  while [ "$#" -gt 0 ]; do
    if [ "$1" = "--out" ]; then printf 'reference' > "$2"; break; fi
    shift
  done
fi
''')
        sips.chmod(0o755)
        (self.root / "input.png").write_text("reference fixture")
        self.env = dict(os.environ, PATH=str(self.root / "commands") + ":/usr/bin:/bin")
        self.env.pop("TURBO", None)

    def run_cli(self, name, *args):
        return subprocess.run(["/bin/bash", str(self.root / name), *args], cwd=self.temp.name,
                              env=self.env, text=True, capture_output=True, timeout=10)

    def test_generate_propagates_native_failure_without_claiming_an_output(self):
        result = self.run_cli("generate.sh", "a red mug", "512", "512")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Saved:", result.stdout)

    def test_edit_propagates_failure_and_removes_temporary_reference(self):
        result = self.run_cli("edit.sh", "input.png", "change the mug to blue")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Saved:", result.stdout)
        self.assertEqual(list((self.root / "studio/tmp").glob("cli_ref_*.png")), [])

    def test_edit_missing_arguments_reports_usage(self):
        result = self.run_cli("edit.sh")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("Usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
