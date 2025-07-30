from typing import Optional, Union
from uuid import UUID

import pandas as pd

from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy._utils._log import log
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric._token_provider import SynapseTokenProvider


@log
def list_dataflows(workspace: Optional[Union[str, UUID]] = None) -> pd.DataFrame:
    """
    List all the Power BI dataflows.

    Please see `Dataflows - Get Dataflows <https://learn.microsoft.com/en-us/rest/api/power-bi/dataflows/get-dataflows>`_
    for more details.

    Parameters
    ----------
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    =======
    pandas.DataFrame
        DataFrame with one row per data flow.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    rest_api = _PBIRestAPI(token_provider=SynapseTokenProvider())
    payload = rest_api.list_dataflows(workspace_client.get_workspace_name(), workspace_client.get_workspace_id())
    df = rename_and_validate_from_records(payload, [
        ("objectId",     "Dataflow Id",   "str"),
        ("name",         "Dataflow Name", "str"),
        ("description",  "Description",   "str"),
        ("configuredBy", "Configured By", "str")
    ])
    return df


@log
def list_dataflow_storage_accounts() -> pd.DataFrame:
    """
    List a list of dataflow storage accounts that the user has access to.

    Please see `Dataflow Storage Accounts - Get Dataflow Storage Accounts <https://learn.microsoft.com/en-us/rest/api/power-bi/dataflow-storage-accounts/get-dataflow-storage-accounts>`_
    for more details.

    Returns
    =======
    pandas.DataFrame
        DataFrame with one row per dataflow storage account.
    """
    client = _PBIRestAPI(token_provider=SynapseTokenProvider())
    payload = client.list_dataflow_storage_accounts()
    df = rename_and_validate_from_records(payload, [
        ("id",        "Dataflow Storage Account Id",   "str"),
        ("name",      "Dataflow Storage Account Name", "str"),
        ("isEnabled", "Is Enabled",                    "bool")])

    return df
