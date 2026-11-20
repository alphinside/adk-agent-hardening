import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from wallet_agent import model_armor_plugin
from wallet_agent.model_armor_plugin import ModelArmorScreenPlugin, _regional_endpoint

REPO_ROOT = Path(__file__).resolve().parent.parent
STARTER_PLUGIN = REPO_ROOT / "wallet_agent" / "model_armor_plugin.py"
SOLUTION_PLUGIN = REPO_ROOT / "solution" / "files" / "model_armor_plugin.py"


def _load_solution_module():
    spec = importlib.util.spec_from_file_location(
        "solution_model_armor_plugin", SOLUTION_PLUGIN
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegionalEndpointTests(unittest.TestCase):
    def test_uses_standard_host_locally(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=False),
            patch.object(model_armor_plugin.mtls, "should_use_client_cert", return_value=False),
            patch.object(
                model_armor_plugin.mtls, "has_default_client_cert_source", return_value=False
            ),
        ):
            os.environ.pop("GOOGLE_API_USE_MTLS_ENDPOINT", None)
            self.assertEqual(
                _regional_endpoint("us-central1"),
                "modelarmor.us-central1.rep.googleapis.com",
            )

    def test_uses_mtls_host_under_agent_identity(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=False),
            patch.object(model_armor_plugin.mtls, "should_use_client_cert", return_value=True),
            patch.object(
                model_armor_plugin.mtls, "has_default_client_cert_source", return_value=True
            ),
        ):
            os.environ.pop("GOOGLE_API_USE_MTLS_ENDPOINT", None)
            self.assertEqual(
                _regional_endpoint("us-central1"),
                "modelarmor.us-central1.rep.mtls.googleapis.com",
            )

    def test_requires_client_cert_source_in_auto_mode(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=False),
            patch.object(model_armor_plugin.mtls, "should_use_client_cert", return_value=True),
            patch.object(
                model_armor_plugin.mtls, "has_default_client_cert_source", return_value=False
            ),
        ):
            os.environ.pop("GOOGLE_API_USE_MTLS_ENDPOINT", None)
            self.assertEqual(
                _regional_endpoint("us-central1"),
                "modelarmor.us-central1.rep.googleapis.com",
            )

    def test_respects_env_overrides(self) -> None:
        with (
            patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "never"}),
            patch.object(model_armor_plugin.mtls, "should_use_client_cert", return_value=True),
            patch.object(
                model_armor_plugin.mtls, "has_default_client_cert_source", return_value=True
            ),
        ):
            self.assertEqual(
                _regional_endpoint("us-central1"),
                "modelarmor.us-central1.rep.googleapis.com",
            )

        with (
            patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}),
            patch.object(model_armor_plugin.mtls, "should_use_client_cert", return_value=False),
            patch.object(
                model_armor_plugin.mtls, "has_default_client_cert_source", return_value=False
            ),
        ):
            self.assertEqual(
                _regional_endpoint("us-central1"),
                "modelarmor.us-central1.rep.mtls.googleapis.com",
            )


class ModelArmorScreenPluginInitTests(unittest.TestCase):
    def test_passes_regional_endpoint_to_client(self) -> None:
        captured: dict[str, object] = {}

        class _FakeClient:
            def __init__(self, *, client_options) -> None:
                captured["api_endpoint"] = client_options.api_endpoint

        env = {
            "GOOGLE_CLOUD_PROJECT": "test-project",
            "GOOGLE_CLOUD_LOCATION": "us-central1",
            "MODEL_ARMOR_TEMPLATE_ID": "wallet-guard",
        }
        with (
            patch.dict(os.environ, env, clear=False),
            patch.object(model_armor_plugin.mtls, "should_use_client_cert", return_value=True),
            patch.object(
                model_armor_plugin.mtls, "has_default_client_cert_source", return_value=True
            ),
            patch.object(model_armor_plugin.modelarmor_v1, "ModelArmorClient", _FakeClient),
        ):
            os.environ.pop("GOOGLE_API_USE_MTLS_ENDPOINT", None)
            ModelArmorScreenPlugin()

        self.assertEqual(
            captured["api_endpoint"],
            "modelarmor.us-central1.rep.mtls.googleapis.com",
        )


class SolutionParityTests(unittest.TestCase):
    def test_solution_carries_regional_endpoint_and_matches_starter_outside_todo(self) -> None:
        solution_mod = _load_solution_module()
        self.assertTrue(callable(getattr(solution_mod, "_regional_endpoint", None)))

        with (
            patch.dict(os.environ, {"GOOGLE_API_USE_MTLS_ENDPOINT": "always"}),
            patch.object(solution_mod.mtls, "should_use_client_cert", return_value=False),
            patch.object(solution_mod.mtls, "has_default_client_cert_source", return_value=False),
        ):
            self.assertEqual(
                solution_mod._regional_endpoint("us-central1"),
                "modelarmor.us-central1.rep.mtls.googleapis.com",
            )

        starter_src = STARTER_PLUGIN.read_text()
        solution_src = SOLUTION_PLUGIN.read_text()

        starter_before, starter_rest = starter_src.split("def with_decoded_base64(", 1)
        solution_before, solution_rest = solution_src.split("def with_decoded_base64(", 1)
        self.assertEqual(starter_before, solution_before)

        starter_todo, starter_after = starter_rest.split("def _regional_endpoint(", 1)
        _, solution_after = solution_rest.split("def _regional_endpoint(", 1)
        self.assertIn("# TODO:", starter_todo)
        self.assertEqual(starter_after, solution_after)


if __name__ == "__main__":
    unittest.main()
