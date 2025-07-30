import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from toolforge_weld.errors import ToolforgeError


class ToolforgeKubernetesConfigError(ToolforgeError):
    """Base class for exceptions related to the Kubernetes config."""


class KubernetesConfigFileNotFoundException(ToolforgeKubernetesConfigError):
    """Raised when a Kubernetes client is attempted to be created but the configuration file does not exist."""


class KubernetesConfigFileParsingException(ToolforgeKubernetesConfigError):
    """Raised when a Kubernetes client configuration file fails to parse."""


CONTAINER_SERVICE_ACCOUNT_TOKEN_FILE = Path(
    "/var/run/secrets/kubernetes.io/serviceaccount/token"
)
CONTAINER_CA_FILE = Path("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt")
CONTAINER_API_SERVER_URL = "https://kubernetes.default.svc"


@dataclass(frozen=True)
class Kubeconfig:
    current_server: str
    current_namespace: str

    client_cert_file: Optional[Path] = None
    client_key_file: Optional[Path] = None
    client_cert_data: Optional[str] = None
    client_key_data: Optional[str] = None
    token: Optional[str] = None
    ca_file: Optional[Path] = None

    @classmethod
    def from_path(cls, path: Path) -> "Kubeconfig":
        try:
            data = yaml.safe_load(path.read_text())
        except yaml.YAMLError as exc:
            raise KubernetesConfigFileParsingException(
                f"Failed to parse config file {path}"
            ) from exc

        current_context = _find_cfg_obj(data, "contexts", data["current-context"])
        current_cluster = _find_cfg_obj(data, "clusters", current_context["cluster"])
        current_user = _find_cfg_obj(data, "users", current_context["user"])

        client_cert_data = current_user.get("client-certificate-data", None)
        client_cert_file = (
            _resolve_file_path(path.parent, current_user["client-certificate"])
            if current_user.get("client-certificate", None)
            else None
        )

        client_key_data = current_user.get("client-key-data", None)
        client_key_file = (
            _resolve_file_path(path.parent, current_user["client-key"])
            if current_user.get("client-key", None)
            else None
        )

        token = current_user.get("token", None)

        if (
            not token
            and (not client_cert_file or not client_key_file)
            and (not client_cert_data or not client_key_data)
        ):
            raise ToolforgeKubernetesConfigError(
                "Either token or both client-cert and client-key (containing both paths, or cert contents) "
                "must be provided in the kubeconfig."
            )

        return cls(
            current_server=current_cluster["server"],
            client_cert_file=client_cert_file,
            client_key_file=client_key_file,
            client_cert_data=client_cert_data,
            client_key_data=client_key_data,
            token=current_user.get("token", None),
            current_namespace=current_context.get("namespace", "default"),
        )

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Kubeconfig":
        """Load the kubeconfig file from the given path or environment and standard locations."""
        if path is None:
            path = locate_config_file()

        if not path.exists():
            raise KubernetesConfigFileNotFoundException(str(path.resolve()))

        return cls.from_path(path=path)

    @classmethod
    def from_container_service_account(cls, *, namespace: str) -> "Kubeconfig":
        token = CONTAINER_SERVICE_ACCOUNT_TOKEN_FILE.read_text()

        return cls(
            current_server=CONTAINER_API_SERVER_URL,
            token=token,
            ca_file=CONTAINER_CA_FILE,
            current_namespace=namespace,
        )


def locate_config_file() -> Path:
    """Attempt to locate the Kubernetes config file for this user.

    Don't use directly, only public for backwards compatibility.
    """
    return Path(os.getenv("KUBECONFIG", "~/.kube/config")).expanduser()


def _find_cfg_obj(config, kind, name):
    """Lookup a named object in a config."""
    for obj in config[kind]:
        if obj["name"] == name:
            return obj[kind[:-1]]
    raise ToolforgeKubernetesConfigError(
        "Key {} not found in {} section of config".format(name, kind)
    )


def _resolve_file_path(base: Path, input: str) -> Path:
    input_path = Path(input).expanduser()
    if input_path.is_absolute():
        return input_path
    return (base / input_path).resolve()


def fake_kube_config() -> Kubeconfig:
    """Creates a fake Kubeconfig object for testing purposes."""
    return Kubeconfig(
        current_server="https://example.org",
        current_namespace="tool-test",
        client_cert_file=Path("/tmp/fake.crt"),
        client_key_file=Path("/tmp/fake.key"),
    )
