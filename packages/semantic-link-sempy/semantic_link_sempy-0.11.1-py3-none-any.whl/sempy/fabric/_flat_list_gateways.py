import pandas as pd

from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric._token_provider import SynapseTokenProvider


def list_gateways() -> pd.DataFrame:
    """
    List all the Power BI gateways.

    Returns
    =======
    pandas.DataFrame
        DataFrame with one row per gateway.
    """
    rest_api = _PBIRestAPI(token_provider=SynapseTokenProvider())
    payload = rest_api.list_gateways()

    df = rename_and_validate_from_records(payload, [
                               ("id",   "Gateway Id",    "str"),
                               ("name", "Gateway Name",  "str"),
                               ("type", "Gateway Type",  "str")])

    return df
