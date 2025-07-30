from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

import toolforge_weld.kubernetes_config
from toolforge_weld.kubernetes_config import Kubeconfig


def get_dummy_kubeconfig_data() -> Dict[str, Any]:
    return {
        "kind": "Config",
        "users": [
            {
                "name": "tf-wm-lol",
                "user": {
                    "client-certificate": "../.toolskube/client.crt",
                    "client-key": "../.toolskube/client.key",
                },
            }
        ],
        "current-context": "toolforge",
        "contexts": [
            {
                "name": "toolforge",
                "context": {
                    "cluster": "toolforge",
                    "namespace": "tool-wm-lol",
                    "user": "tf-wm-lol",
                },
            }
        ],
        "clusters": [
            {
                "cluster": {
                    "certificate-authority-data": "somebunchofcertificatedata=",
                    "server": "https://k8s.svc.tools.eqiad1.wikimedia.cloud:6443",
                },
                "name": "toolforge",
            }
        ],
        "apiVersion": "v1",
    }


@pytest.fixture
def tmp_kubeconfig(tmp_path: Path) -> Path:
    path = tmp_path / "dummy_file.yaml"
    return path


@pytest.fixture
def tmp_token(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    token = "asdf"

    token_file = tmp_path / "token"
    token_file.write_text(token)

    monkeypatch.setattr(
        toolforge_weld.kubernetes_config,
        "CONTAINER_SERVICE_ACCOUNT_TOKEN_FILE",
        token_file,
    )

    return token


def test_kubeconfig_load_loads_from_given_path(tmp_kubeconfig: Path):
    tmp_kubeconfig.write_text(yaml.dump(get_dummy_kubeconfig_data()))

    my_kubeconfig = Kubeconfig.load(path=tmp_kubeconfig)

    assert (
        my_kubeconfig.client_cert_file
        == tmp_kubeconfig.parent.parent / ".toolskube/client.crt"
    )
    assert (
        my_kubeconfig.client_key_file
        == tmp_kubeconfig.parent.parent / ".toolskube/client.key"
    )
    assert my_kubeconfig.ca_file is None
    assert my_kubeconfig.token is None
    assert my_kubeconfig.current_namespace == "tool-wm-lol"
    assert (
        my_kubeconfig.current_server
        == "https://k8s.svc.tools.eqiad1.wikimedia.cloud:6443"
    )


def test_kubeconfig_load_loads_from_user_home(
    tmp_kubeconfig: Path, monkeypatch: pytest.MonkeyPatch
):
    tmp_kubeconfig.write_text(yaml.dump(get_dummy_kubeconfig_data()))

    def path_mock(path_str: str):
        if path_str == "~/.kube/config":
            return tmp_kubeconfig
        else:
            return Path(path_str)

    monkeypatch.setattr(toolforge_weld.kubernetes_config, "Path", path_mock)
    monkeypatch.delenv("KUBECONFIG", raising=False)

    my_kubeconfig = Kubeconfig.load()

    assert (
        my_kubeconfig.client_cert_file
        == tmp_kubeconfig.parent.parent / ".toolskube/client.crt"
    )
    assert (
        my_kubeconfig.client_key_file
        == tmp_kubeconfig.parent.parent / ".toolskube/client.key"
    )
    assert my_kubeconfig.current_namespace == "tool-wm-lol"
    assert (
        my_kubeconfig.current_server
        == "https://k8s.svc.tools.eqiad1.wikimedia.cloud:6443"
    )


def test_kubeconfig_load_loads_from_env_var(
    tmp_kubeconfig: Path, monkeypatch: pytest.MonkeyPatch
):
    tmp_kubeconfig.write_text(yaml.dump(get_dummy_kubeconfig_data()))
    monkeypatch.setenv("KUBECONFIG", str(tmp_kubeconfig))

    my_kubeconfig = Kubeconfig.load()

    assert (
        my_kubeconfig.client_cert_file
        == tmp_kubeconfig.parent.parent / ".toolskube/client.crt"
    )
    assert (
        my_kubeconfig.client_key_file
        == tmp_kubeconfig.parent.parent / ".toolskube/client.key"
    )
    assert my_kubeconfig.current_namespace == "tool-wm-lol"
    assert (
        my_kubeconfig.current_server
        == "https://k8s.svc.tools.eqiad1.wikimedia.cloud:6443"
    )


def test_kubeconfig_load_from_token_file(tmp_token: str):
    my_kubeconfig = Kubeconfig.from_container_service_account(namespace="tf-public")

    assert my_kubeconfig.token == tmp_token
    assert (
        str(my_kubeconfig.ca_file)
        == "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
    )
    assert my_kubeconfig.current_server == "https://kubernetes.default.svc"
    assert my_kubeconfig.current_namespace == "tf-public"

    assert my_kubeconfig.client_cert_file is None
    assert my_kubeconfig.client_key_file is None


def test_kubeconfig_load_invalid_syntax(tmp_path: Path):
    tmp_file = tmp_path / "invalid.yaml"
    tmp_file.write_text("not: valid: yaml")

    with pytest.raises(
        toolforge_weld.kubernetes_config.KubernetesConfigFileParsingException
    ):
        assert Kubeconfig.load(path=tmp_file) is None
