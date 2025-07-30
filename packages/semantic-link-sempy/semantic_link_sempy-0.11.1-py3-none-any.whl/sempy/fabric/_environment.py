import os
from typing import Optional, Dict, Any
from urllib.parse import quote, urlparse

fs_client: Optional[Any] = None
environment: Optional[str] = None
on_fabric: Optional[bool] = None
on_jupyter: Optional[bool] = None
on_aiskill: Optional[bool] = None
jupyter_config: Optional[Dict[str, str]] = None


def get_workspace_id() -> str:
    """
    Return workspace id or default Lakehouse's workspace id.

    Returns
    -------
    str
        Workspace id guid if no default Lakehouse is set; otherwise, the default Lakehouse's workspace id guid.
    """
    return _get_fabric_context("trident.workspace.id")


def get_lakehouse_id() -> str:
    """
    Return lakehouse id of the lakehouse that is connected to the workspace.

    Returns
    -------
    str
        Lakehouse id guid.
    """
    return _get_fabric_context("trident.lakehouse.id")


def get_notebook_workspace_id() -> str:
    """
    Return notebook workspace id.

    Returns
    -------
    str
        Workspace id guid.
    """
    return _get_fabric_context("trident.artifact.workspace.id")


def get_artifact_id() -> str:
    """
    Return artifact id.

    Returns
    -------
    str
        Artifact (most commonly notebook) id guid.
    """
    return _get_fabric_context("trident.artifact.id")


def _get_artifact_type() -> str:
    """
    Return artifact type.

    Returns
    -------
    str
        Artifact type e.g. "SynapseNotebook".
    """
    return _get_fabric_context('trident.artifact.type')


def _get_onelake_endpoint() -> str:
    """
    Return onelake endpoint for the lakehouse.

    Returns
    -------
    str
        Onelake endpoint.
    """
    # e.g. abfss://<workspaceid>@<hostname>/
    domain = urlparse(_get_fabric_context("fs.defaultFS")).netloc
    return domain.split("@")[-1]


def _get_fabric_context(key: str) -> str:
    """
    Retrieves the value from the Fabric context.

    Parameters
    ----------
    key : str
        The key for the Fabric context value.

    Returns
    -------
    str
        The retrieved value associated with the given key
    """
    if not _on_fabric():
        return ""

    global jupyter_config
    jupyter_config = jupyter_config or {}

    if key not in jupyter_config:
        try:
            from synapse.ml.internal_utils.session_utils import get_fabric_context  # type: ignore
            jupyter_config.update(get_fabric_context())
        except (ImportError, AttributeError):
            return ""

    return jupyter_config.get(key, "")


def _get_pbi_uri() -> str:
    return _get_fabric_rest_endpoint().replace("https://", "powerbi://")


def _get_fabric_rest_endpoint() -> str:
    from synapse.ml.fabric.service_discovery import get_fabric_env_config
    from sempy.fabric._utils import normalize_url
    url = normalize_url(get_fabric_env_config(with_tokens=False).fabric_env_config.shared_host)
    # always end with "/" to avoid joining issues
    return url.rstrip("/") + "/"


def _get_workspace_url(workspace: str) -> str:
    url = f"{_get_pbi_uri()}v1.0/myorg/"
    if workspace == "My workspace":
        return url
    else:
        return f"{url}{quote(workspace, safe='')}"


def _get_workspace_path(workspace_name: str, workspace_id: str):
    if workspace_name == "My workspace":
        # retrieving datasets from "My workspace" (does not have a group GUID) requires a different query
        return "v1.0/myorg/"
    else:
        return f"v1.0/myorg/groups/{workspace_id}/"


def _get_onelake_abfss_path(workspace_id: Optional[str] = None, dataset_id: Optional[str] = None) -> str:
    workspace_id = get_workspace_id() if workspace_id is None else workspace_id
    dataset_id = get_lakehouse_id() if dataset_id is None else dataset_id
    onelake_endpoint = _get_onelake_endpoint()
    return f"abfss://{workspace_id}@{onelake_endpoint}/{dataset_id}"


def _get_environment() -> str:

    global environment

    if environment is None:

        if _on_fabric():
            environment = _get_fabric_context("spark.trident.pbienv")

        if not environment:
            environment = 'msit'

        environment = environment.lower().strip()

    return environment


def _on_fabric() -> bool:
    """True if running on Fabric (spark or jupyter or ai skill)"""
    global on_fabric
    if on_fabric is None:
        on_fabric = "AZURE_SERVICE" in os.environ or _on_jupyter() or _on_aiskill()
    return on_fabric


def _on_jupyter() -> bool:
    global on_jupyter
    if on_jupyter is None:
        on_jupyter = os.environ.get("MSNOTEBOOKUTILS_RUNTIME_TYPE", "").lower() == "jupyter"
    return on_jupyter


def _on_aiskill() -> bool:
    global on_aiskill
    if on_aiskill is None:
        on_aiskill = os.environ.get("trident.aiskill.env", "").lower() == "true"
    return on_aiskill


def _get_fabric_run_id() -> str:
    return _get_fabric_context("trident.aiskill.fabric_run_id") or ""


def _get_root_activity_id() -> str:
    return _get_fabric_context("trident.aiskill.root_activity_id") or ""
