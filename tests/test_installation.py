"""Run real shell flows with platform/network doubles; never download or load models."""
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ("download.sh", "install.sh", "studio.sh", "Install.command", "Start.command")

# Only external commands are replaced. Extraction, shell branching and filesystem changes are real.
DOUBLE = r'''
import json, os, pathlib, shutil, subprocess, sys
name, args = pathlib.Path(sys.argv[0]).name, sys.argv[1:]
env = os.environ
log = pathlib.Path(env["TEST_LOG"])
def record(**fields):
    with log.open("a") as f: f.write(json.dumps(dict(command=name, **fields)) + "\n")
if name == "uname":
    print(env.get("TEST_OS", "Darwin") if args == ["-s"] else env.get("TEST_ARCH", "arm64"))
elif name == "sw_vers": print(env.get("TEST_MACOS", "26.0"))
elif name.startswith("python") or name == "Custom Python":
    version = env.get("TEST_PYTHON", "3.8") if name == "python3" else env.get("TEST_FALLBACK", "3.12")
    if args[:1] == ["-c"]: sys.exit(0 if tuple(map(int, version.split("."))) >= (3, 9) else 1)
    record(args=args, cwd=os.getcwd()); print("server stub launched")
elif name in ("sleep", "open"): pass
elif name == "stat":
    sizes = json.loads(pathlib.Path(env["TEST_SIZES"]).read_text())
    print(sizes.get(str(pathlib.Path(args[-1]).resolve()), pathlib.Path(args[-1]).stat().st_size))
elif name == "shasum":
    # Native receipt creation/checking uses macOS's actual shasum on the tiny extracted files.
    if "-c" not in args or args[args.index("-c") + 1] != "-":
        sys.exit(subprocess.run(["/usr/bin/shasum", *args]).returncode)
    if "-c" in args:
        source = args[args.index("-c") + 1]
        lines = sys.stdin if source == "-" else pathlib.Path(source).read_text().splitlines()
        for line in lines:
            digest, filename = line.rstrip().split("  ", 1)
            target = pathlib.Path(filename)
            if not target.exists() or env.get("TEST_BAD_HASH") == target.name: sys.exit(1)
            print(filename + ": OK")
elif name == "unzip":
    result = subprocess.run(["/usr/bin/unzip", *args])
    if env.get("TEST_UNZIP_FAIL"):
        dest = pathlib.Path(args[args.index("-d") + 1])
        (dest / "sd-server").write_bytes(b"interrupted nonempty extraction")
        sys.exit(9)
    sys.exit(result.returncode)
elif name == "curl":
    dest, url = pathlib.Path(args[args.index("-o") + 1]), args[-1]
    record(dest=str(dest), url=url, resume=("-C" in args and args[args.index("-C") + 1] == "-"))
    if env.get("TEST_CURL_FAIL") == dest.name: sys.exit(22)
    fixtures = pathlib.Path(env["TEST_FIXTURES"])
    if dest.suffix == ".zip":
        fixture = "incomplete.zip" if env.get("TEST_INCOMPLETE") else "native.zip"
        shutil.copyfile(fixtures / fixture, dest)
    elif dest.name == "llama.tar.gz": shutil.copyfile(fixtures / "llama.tar.gz", dest)
    else: dest.write_bytes(b"tiny model fixture")
    sizes_by_name = {
        "sd.zip": 35049086, "turbo8.zip": 35158090, "llama.tar.gz": 11763877,
        "qwen-image-2.1-Q4_K_M.gguf": 4199565024,
        "Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf": 5148699488,
        "mmproj-Qwen3VL-8B-Instruct-F16.gguf": 1159030336,
        "qwen_image_2.1_vae_bf16.safetensors": 675508656,
        "fun-acc-4step.safetensors": 344600164, "RealESRGAN_x4plus.pth": 67040989,
        "Qwen-Image-2.1-Turbo-AD-Q4_K.gguf": 4201694944,
    }
    sizes_file = pathlib.Path(env["TEST_SIZES"])
    sizes = json.loads(sizes_file.read_text())
    sizes[str(dest.resolve())] = 7 if env.get("TEST_BAD_SIZE") == dest.name else sizes_by_name[dest.name]
    sizes_file.write_text(json.dumps(sizes))
else: raise AssertionError("unexpected command: " + name)
'''


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="qwen-install-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name) / "Release With Spaces"
        self.work.mkdir()
        for name in SCRIPTS:
            if (ROOT / name).exists(): shutil.copyfile(ROOT / name, self.work / name)
        (self.work / "studio").mkdir()
        (self.work / "studio/server.py").write_text('print("isolated server stub")\n')
        self.bin = Path(self.temp.name) / "command doubles"
        self.bin.mkdir()
        shim = self.bin / "double"
        shim.write_text("#!" + sys.executable + "\n" + DOUBLE)
        shim.chmod(0o755)
        for name in ("uname", "sw_vers", "python3", "python3.12", "Custom Python", "stat", "curl", "shasum", "unzip", "open", "sleep"):
            (self.bin / name).symlink_to(shim)
        fixtures = Path(self.temp.name) / "fixtures"
        fixtures.mkdir()
        for filename, complete in (("native.zip", True), ("incomplete.zip", False)):
            with zipfile.ZipFile(fixtures / filename, "w") as archive:
                for name in ["sd-cli", "sd-server"] + (["libstable-diffusion.dylib"] if complete else []):
                    archive.writestr(name, "native fixture")
        with tarfile.open(fixtures / "llama.tar.gz", "w:gz") as archive:
            libraries = ("libllama", "libmtmd", "libggml", "libggml-base", "libggml-cpu",
                         "libggml-metal", "libggml-blas", "libggml-rpc", "libllama-common")
            names = ["llama-mtmd-cli"] + [name + suffix for name in libraries for suffix in (".dylib", ".0.dylib")]
            for name in names:
                info = tarfile.TarInfo("llama-b11249/" + name)
                data = b"native fixture"
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        self.log = Path(self.temp.name) / "calls.jsonl"
        sizes = Path(self.temp.name) / "sizes.json"
        sizes.write_text("{}")
        self.env = dict(os.environ, PATH=str(self.bin) + ":/usr/bin:/bin", TEST_LOG=str(self.log),
                        TEST_SIZES=str(sizes), TEST_FIXTURES=str(fixtures))
        self.env.pop("PYTHON", None)

    def run_script(self, name, *args, **environment):
        return subprocess.run(["/bin/bash", str(self.work / name), *args], cwd=self.temp.name,
                              env=dict(self.env, **environment), text=True, capture_output=True, timeout=20)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def assert_failed(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Installation complete", result.stdout)
        self.assertNotIn("All files ready", result.stdout)
        self.assertNotIn("Turbo 8-step ready", result.stdout)

    def test_check_rejects_unsupported_platforms_before_any_download(self):
        for environment in ({"TEST_OS": "Linux"}, {"TEST_ARCH": "x86_64"}, {"TEST_MACOS": "25.6"}):
            with self.subTest(environment=environment):
                result = self.run_script("install.sh", "--check", **environment)
                self.assert_failed(result)
                self.assertRegex(result.stderr, r"macOS|Apple Silicon")
        self.assertEqual(self.calls(), [])

    def test_check_uses_compatible_python_fallback_without_downloading(self):
        result = self.run_script("install.sh", "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("python3.12", result.stdout)
        self.assertEqual(self.calls(), [])

    def test_explicit_old_python_is_rejected_without_silent_fallback(self):
        result = self.run_script("install.sh", "--check", PYTHON=str(self.bin / "python3"))
        self.assert_failed(result)
        self.assertIn("3.9", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_help_does_not_require_a_supported_platform(self):
        result = self.run_script("install.sh", "--help", TEST_OS="Linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--check", result.stdout)
        self.assertIn("PYTHON", result.stdout)
        self.assertEqual(self.calls(), [])

    def replace_download(self, fail_phase=None):
        self.work.joinpath("download.sh").write_text(
            '#!/bin/bash\nphase="${1:-base}"\necho "$phase" >> phases.txt\n' +
            (f'[[ "$phase" != "{fail_phase}" ]] || exit 22\n' if fail_phase else "") +
            'touch "done-$phase"\n')

    def test_install_runs_base_then_turbo8_from_a_path_with_spaces(self):
        self.replace_download()
        result = self.run_script("install.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.work / "phases.txt").read_text().splitlines(), ["base", "--turbo8"])
        self.assertTrue((self.work / "done-base").exists())
        self.assertTrue((self.work / "done---turbo8").exists())
        self.assertIn("Installation complete", result.stdout)

    def test_clean_install_executes_both_real_download_flows(self):
        result = self.run_script("install.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Installation complete", result.stdout)
        for filename in ("bin/sd-cli", "bin/libstable-diffusion.dylib", "bin/turbo8/sd-server",
                         "bin/turbo8/libstable-diffusion.dylib", "models/qwen-image-2.1-Q4_K_M.gguf",
                         "models/Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf", "models/mmproj-Qwen3VL-8B-Instruct-F16.gguf",
                         "models/qwen_image_2.1_vae_bf16.safetensors", "models/loras/fun-acc-4step.safetensors",
                         "models/upscalers/RealESRGAN_x4plus.pth", "models/Qwen-Image-2.1-Turbo-AD-Q4_K.gguf"):
            self.assertTrue((self.work / filename).exists(), filename)
        destinations = [call["dest"] for call in self.calls()]
        self.assertLess(destinations.index("models/qwen-image-2.1-Q4_K_M.gguf"),
                        destinations.index("models/Qwen-Image-2.1-Turbo-AD-Q4_K.gguf"))
        before = self.calls()
        rerun = self.run_script("install.sh")
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertEqual(self.calls(), before)

    def test_install_does_not_continue_or_claim_completion_after_a_phase_fails(self):
        for phase in ("base", "--turbo8"):
            with self.subTest(phase=phase):
                self.replace_download(fail_phase=phase)
                (self.work / "phases.txt").unlink(missing_ok=True)
                result = self.run_script("install.sh")
                self.assert_failed(result)
                expected = ["base"] if phase == "base" else ["base", "--turbo8"]
                self.assertTrue((self.work / "phases.txt").exists(), "installer did not run the base phase")
                self.assertEqual((self.work / "phases.txt").read_text().splitlines(), expected)

    def test_completed_default_install_is_skipped_when_rerun(self):
        first = self.run_script("download.sh")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertTrue((self.work / "bin/libstable-diffusion.dylib").exists())
        self.assertTrue(os.access(self.work / "bin/sd-server", os.X_OK))
        calls = self.calls()
        second = self.run_script("download.sh")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(self.calls(), calls, "completed files should not be downloaded again")

    def test_missing_base_shared_library_repairs_only_the_native_bundle(self):
        first = self.run_script("download.sh")
        self.assertEqual(first.returncode, 0, first.stderr)
        (self.work / "bin/libstable-diffusion.dylib").unlink()
        before = len(self.calls())
        repaired = self.run_script("download.sh")
        self.assertEqual(repaired.returncode, 0, repaired.stderr)
        self.assertTrue((self.work / "bin/libstable-diffusion.dylib").exists())
        self.assertEqual([c["dest"] for c in self.calls()[before:]], ["bin/sd.zip"])

    def test_partial_model_is_resumed_and_rechecked(self):
        self.assertEqual(self.run_script("download.sh").returncode, 0)
        model = self.work / "models/qwen-image-2.1-Q4_K_M.gguf"
        model.write_bytes(b"par")
        sizes_file = Path(self.env["TEST_SIZES"])
        sizes = json.loads(sizes_file.read_text())
        sizes[str(model.resolve())] = 3
        sizes_file.write_text(json.dumps(sizes))
        before = len(self.calls())
        result = self.run_script("download.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        downloads = self.calls()[before:]
        self.assertEqual([c["dest"] for c in downloads], ["models/qwen-image-2.1-Q4_K_M.gguf"])
        self.assertTrue(downloads[0]["resume"])

    def test_bad_full_model_is_removed_and_next_run_can_recover(self):
        self.assertEqual(self.run_script("download.sh").returncode, 0)
        filename = "qwen-image-2.1-Q4_K_M.gguf"
        self.assert_failed(self.run_script("download.sh", TEST_BAD_HASH=filename))
        self.assertFalse((self.work / "models" / filename).exists())
        result = self.run_script("download.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.work / "models" / filename).exists())

    def test_missing_assistant_shared_library_repairs_its_bundle(self):
        self.assertEqual(self.run_script("download.sh").returncode, 0)
        library = self.work / "bin/llama/llama-b11249/libmtmd.dylib"
        library.unlink()
        before = len(self.calls())
        result = self.run_script("download.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(library.exists())
        self.assertEqual([c["dest"] for c in self.calls()[before:]], ["bin/llama.tar.gz"])

    def test_missing_assistant_rpc_or_soname_alias_repairs_its_bundle(self):
        self.assertEqual(self.run_script("download.sh").returncode, 0)
        for filename in ("libggml-rpc.0.dylib", "libmtmd.0.dylib"):
            with self.subTest(filename=filename):
                library = self.work / "bin/llama/llama-b11249" / filename
                library.unlink()
                result = self.run_script("download.sh")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(library.exists(), "a required dynamic-link alias was not repaired")

    def test_nonempty_corrupt_engine_is_repaired_instead_of_reported_ready(self):
        self.assertEqual(self.run_script("download.sh").returncode, 0)
        executable = self.work / "bin/sd-server"
        original = executable.read_bytes()
        executable.write_bytes(b"corrupt but nonempty")
        result = self.run_script("download.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(executable.read_bytes(), original)

    def test_native_receipt_is_verified_by_real_shasum(self):
        self.assertEqual(self.run_script("download.sh").returncode, 0)
        directory = self.work / "bin"
        result = subprocess.run(["/usr/bin/shasum", "-a", "256", "-c", ".studio-files.sha256"],
                                cwd=directory, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("libstable-diffusion.dylib: OK", result.stdout)
        (directory / "sd-cli").write_bytes(b"corrupt but nonempty")
        result = subprocess.run(["/usr/bin/shasum", "-a", "256", "-c", ".studio-files.sha256"],
                                cwd=directory, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "real SHA verification must reject changed bytes")

    def test_interrupted_extraction_does_not_replace_installed_files(self):
        self.assertEqual(self.run_script("download.sh").returncode, 0)
        executable = self.work / "bin/sd-server"
        original = executable.read_bytes()
        (self.work / "bin/libstable-diffusion.dylib").unlink()
        self.assert_failed(self.run_script("download.sh", TEST_UNZIP_FAIL="1"))
        self.assertEqual(executable.read_bytes(), original)
        result = self.run_script("download.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.work / "bin/libstable-diffusion.dylib").exists())

    def test_turbo8_native_repair_preserves_existing_base_engine(self):
        first = self.run_script("download.sh", "--turbo8")
        self.assertEqual(first.returncode, 0, first.stderr)
        (self.work / "bin/sd-cli").write_text("existing base sentinel")
        (self.work / "bin/turbo8/libstable-diffusion.dylib").unlink()
        before = len(self.calls())
        repaired = self.run_script("download.sh", "--turbo8")
        self.assertEqual(repaired.returncode, 0, repaired.stderr)
        self.assertEqual((self.work / "bin/sd-cli").read_text(), "existing base sentinel")
        self.assertEqual([c["dest"] for c in self.calls()[before:]], ["bin/turbo8.zip"])

    def test_download_http_size_and_hash_failures_never_report_ready(self):
        for flag, filename in (("TEST_CURL_FAIL", "sd.zip"),
                               ("TEST_BAD_SIZE", "qwen-image-2.1-Q4_K_M.gguf"),
                               ("TEST_BAD_HASH", "qwen-image-2.1-Q4_K_M.gguf")):
            with self.subTest(flag=flag):
                self.assert_failed(self.run_script("download.sh", **{flag: filename}))

    def test_incomplete_native_archive_does_not_report_ready(self):
        self.assert_failed(self.run_script("download.sh", TEST_INCOMPLETE="1"))

    def test_direct_download_rejects_unsupported_macos(self):
        self.assert_failed(self.run_script("download.sh", TEST_MACOS="25.6"))
        self.assertEqual(self.calls(), [])

    def test_studio_selects_python_fallback_and_preserves_port_and_working_directory(self):
        result = self.run_script("studio.sh", "7899")
        self.assertEqual(result.returncode, 0, result.stderr)
        launches = [c for c in self.calls() if c["command"].startswith("python")]
        self.assertEqual(len(launches), 1, "studio did not use the selected Python")
        launch = launches[0]
        self.assertEqual(launch["command"], "python3.12")
        self.assertEqual(launch["args"], ["studio/server.py", "7899"])
        self.assertEqual(Path(launch["cwd"]).resolve(), self.work.resolve())

    def test_studio_accepts_explicit_python_path_with_spaces(self):
        result = self.run_script("studio.sh", PYTHON=str(self.bin / "Custom Python"))
        self.assertEqual(result.returncode, 0, result.stderr)
        launches = [c for c in self.calls() if c["command"] == "Custom Python"]
        self.assertEqual(len(launches), 1, "studio ignored the explicit Python")
        launch = launches[0]
        self.assertEqual(launch["args"], ["studio/server.py", "7860"])

    def test_double_click_wrappers_execute_scripts_without_executable_bits(self):
        result = self.run_script("Install.command", "--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), [])
        result = self.run_script("Start.command", "7898")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(any(c.get("args") == ["studio/server.py", "7898"] for c in self.calls()))


if __name__ == "__main__":
    unittest.main()
