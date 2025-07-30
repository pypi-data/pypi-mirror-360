import pandas as pd

from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric._token_provider import SynapseTokenProvider


def list_apps() -> pd.DataFrame:
    """
    List all the Power BI apps.

    Returns
    =======
    pandas.DataFrame
        DataFrame with one row per app.
    """
    rest_api = _PBIRestAPI(token_provider=SynapseTokenProvider())

    payload = rest_api.list_apps()

    df = rename_and_validate_from_records(payload, [
                               ("id",          "App Id",       "str"),
                               ("name",        "App Name",     "str"),
                               ("lastUpdate",  "Last Update",  "datetime64[ns]"),
                               ("description", "Description",  "str"),
                               ("publishedBy", "Published By", "str"),
                               ("workspaceId", "Workspace Id", "str")])

    return df
