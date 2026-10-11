"""Regression checks at the queue, native request and model process boundaries."""
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "studio"))
import engine
import server


OFFICIAL_SIGMAS = [1.0, 0.978453, 0.95418, 0.926626, 0.89508,
                   0.845148, 0.704534, 0.414568, 0.0]


class Turbo8Tests(unittest.TestCase):
    def setUp(self):
        server.JOBS.clear()
        server.ORDER.clear()

    def tearDown(self):
        server.JOBS.clear()
        server.ORDER.clear()

    def submit_job(self, **changes):
        spec = dict(mode="gen", prompt="a red teapot", preset="turbo8", turbo=True,
                    width=512, height=512, steps=24, cfg=7, sampler="heun",
                    scheduler="karras", flow_shift=3, fast=True, img_cfg=4,
                    negative="blur", seed=123)
        spec.update(changes)
        # Model presence and image dimensions are external to parameter normalization.
        with patch.object(engine, "turbo8_available", return_value=True, create=True), \
                patch.object(server, "image_size", return_value=(768, 768)):
            job = server.JOBS[server.submit(spec)[0]]
        job.update(ref_paths=[], init_path=None, mask_path=None)
        return job

    def test_new_preset_enforces_parameters_for_generate_and_edit(self):
        for mode in ("gen", "edit"):
            with self.subTest(mode=mode):
                job = self.submit_job(mode=mode, refs=["test-reference.png"] if mode == "edit" else [])
                self.assertEqual(job.get("preset"), "turbo8")
                self.assertFalse(job["turbo"])
                self.assertEqual((job["steps"], job["cfg"], job["sampler"]), (8, 1.0, "euler"))
                self.assertEqual((job["fast"], job["img_cfg"], job["flow_shift"], job["negative"]),
                                 (False, None, None, ""))

    def test_warm_request_uses_official_grid_at_both_sizes_without_lora(self):
        for size in (512, 768):
            job = self.submit_job(width=size, height=size)
            with patch.object(engine, "turbo_sigmas", side_effect=AssertionError("4-step grid used")):
                body = server.engine_body(job)
            self.assertEqual(body["sample_params"]["custom_sigmas"], OFFICIAL_SIGMAS)
            self.assertEqual(body["sample_params"]["sample_steps"], 8)
            self.assertEqual(body["sample_params"]["guidance"], {"txt_cfg": 1.0})
            self.assertNotIn("lora", body)
            self.assertNotIn("cache_mode", body)

    def test_cli_selects_new_model_grid_and_preserves_edit_mask_inputs(self):
        job = self.submit_job(mode="edit", refs=["test-reference.png"], preview=True)
        job.update(ref_paths=["reference.png"], init_path="init.png", mask_path="mask.png")
        with patch.object(engine, "turbo_sigmas", side_effect=AssertionError("4-step grid used")):
            cmd = server.cli_cmd(job, "result.png", "preview.png")
        value = lambda flag: cmd[cmd.index(flag) + 1]
        self.assertTrue(value("--diffusion-model").endswith("models/Qwen-Image-2.1-Turbo-AD-Q4_K.gguf"))
        self.assertEqual([float(s) for s in value("--sigmas").split(",")], OFFICIAL_SIGMAS)
        self.assertEqual(value("--steps"), "8")
        self.assertEqual(value("--llm_vision"), engine.VISION)
        self.assertEqual(value("-r"), "reference.png")
        self.assertEqual(value("--mask"), "mask.png")
        self.assertEqual(value("-i"), "init.png")
        self.assertNotIn("<lora:", value("-p"))

    def test_existing_turbo_still_uses_four_step_lora_and_size_matched_grid(self):
        with patch.object(engine, "turbo_available", return_value=True):
            job = self.submit_job(preset="turbo", width=768, height=768)
        self.assertEqual((job["steps"], job["cfg"], job["sampler"]), (4, 1.0, "euler"))
        body = server.engine_body(job)
        self.assertEqual(body["sample_params"]["custom_sigmas"],
                         [1.0, 0.859204, 0.667076, 0.389287, 0.0])
        self.assertEqual(body["lora"], [{"path": "fun-acc-4step.safetensors", "multiplier": 1.0}])

    def test_missing_turbo8_does_not_silently_run_full_model(self):
        with patch.object(engine, "turbo8_available", return_value=False, create=True):
            with self.assertRaisesRegex(ValueError, "Turbo 8-step"):
                server.submit(dict(prompt="test", preset="turbo8"))
        self.assertEqual(server.ORDER, [])

    def test_warm_engine_restarts_when_diffusion_model_changes(self):
        warm = engine.WarmEngine()
        # Keep actual start/model comparison; replace native process and readiness I/O only.
        with patch.object(engine.subprocess, "Popen") as popen, \
                patch.object(warm, "_free_port", return_value=19999), \
                patch.object(warm, "_get", return_value={}), \
                patch.object(engine.threading.Thread, "start"), \
                patch.object(engine.os, "killpg"):
            popen.return_value.poll.return_value = None
            warm.start(engine.DIFFUSION)
            warm.start(engine.DIFFUSION)
            self.assertEqual(popen.call_count, 1)
            warm.start(os.path.join(engine.MODELS, "Qwen-Image-2.1-Turbo-AD-Q4_K.gguf"))
            self.assertEqual(popen.call_count, 2)
            cmd = popen.call_args.args[0]
            self.assertTrue(cmd[cmd.index("--diffusion-model") + 1].endswith("Turbo-AD-Q4_K.gguf"))
            warm.stop()


if __name__ == "__main__":
    unittest.main()
