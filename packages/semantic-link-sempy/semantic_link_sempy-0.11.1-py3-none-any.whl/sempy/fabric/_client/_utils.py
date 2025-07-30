from pathlib import Path
from typing import Callable, Optional, Union
from threading import RLock
import uuid

import pandas as pd

from sempy.fabric._token_provider import create_on_access_token_expired_callback, TokenProvider
from sempy._utils._dotnet import _init_dotnet_runtime
from sempy._utils._log import log_xmla


_analysis_services_initialized = False
_analysis_services_initialized_lock: RLock = RLock()


def _init_analysis_services() -> None:
    global _analysis_services_initialized

    if _analysis_services_initialized:
        return

    with _analysis_services_initialized_lock:

        if _analysis_services_initialized:
            return

        my_path = Path(__file__).parent
        sempy_root = my_path / ".." / ".."
        runtime_config = sempy_root / "dotnet.runtime.config.json"
        assembly_path = sempy_root / "lib"
        assemblies = list(
            map(
                lambda assembly_file: assembly_path / assembly_file,
                [
                    "Microsoft.AnalysisServices.Tabular.dll",
                    "Microsoft.AnalysisServices.AdomdClient.dll",
                    "Microsoft.Fabric.SemanticLink.XmlaTools.dll"
                ]
            )
        )

        _init_dotnet_runtime(runtime_config, assemblies=assemblies)
        _analysis_services_initialized = True


@log_xmla
def _create_tom_server(connection_string: str, token_provider: TokenProvider):
    import Microsoft.AnalysisServices.Tabular as TOM
    from Microsoft.AnalysisServices import AccessToken
    from System import Func

    tom_server = TOM.Server()

    get_access_token = create_on_access_token_expired_callback(token_provider)

    tom_server.AccessToken = get_access_token(None)
    tom_server.OnAccessTokenExpired = Func[AccessToken, AccessToken](get_access_token)

    tom_server.Connect(connection_string)

    return tom_server


def _odata_quote(s: str) -> str:
    # https://stackoverflow.com/questions/4229054/how-are-special-characters-handled-in-an-odata-query

    return (s.replace("'", "''")
             .replace("%", "%25")
             .replace("+", "%2B")
             .replace("/", "%2F")
             .replace("?", "%3F")
             .replace("#", "%23")
             .replace("&", "%26"))


def _build_adomd_connection_string(
        datasource: str,
        initial_catalog: Optional[str] = None,
        readonly: bool = True,
        role: Optional[str] = None,
        effective_user_name: Optional[str] = None,
) -> str:
    """
    Build ADOMD Connection string

    Parameters
    ----------
    datasource : str
        The data source string (e.g. a workspace url).
    initial_catalog : str
        Optional initial catalog (e.g. the dataset name).
    readonly : bool
        If true the connection is read-only and can connect to read-only replicas. Default to true.
    role : str, default=None
        The role to impersonate. Cannot be used with effective_user_name.
    effective_user_name : str, default=None
        The effective user name to impersonate. Cannot be used with role.
    """

    # check for conflicting parameters
    if role is not None and effective_user_name is not None:
        raise ValueError("Cannot set both role and effective_user_name.")

    # build datasource
    if readonly:
        datasource += "?readonly"

    # escape data source
    datasource = datasource.replace('"', '""')

    connection_str = f'DataSource="{datasource}"'

    if initial_catalog is not None:
        initial_catalog = initial_catalog.replace('"', '""')

        connection_str += f';Initial Catalog="{initial_catalog}"'

    if role is not None:
        role = role.replace('"', '""')

        connection_str += f';Roles="{role}"'

    if effective_user_name is not None:
        effective_user_name = effective_user_name.replace('"', '""')

        connection_str += f';EffectiveUserName="{effective_user_name}"'

    connection_str += ";Application Name=SemPy;Protocol Format=XML; Transport Compression=None"

    return connection_str


def _format_dax_object_name(table: Union[str, pd.Series], column: Union[str, pd.Series]) -> Union[str, pd.Series]:
    """
    Format table/column combinations to the 'Table Name'[Column Name] format.

    Parameters
    ----------
    table : Union[str, pd.Series]
        The table name(s), either as a string or a Pandas Series of strings.
    column : Union[str, pd.Series]
        The column name(s), either as a string or a Pandas Series of strings.

    Returns
    -------
    Union[str, pd.Series]
        A string if both inputs are strings, otherwise a Pandas Series.
    """
    return "'" + table + "'[" + column + "]"


def _format_relationship_name(
    from_table: Union[str, pd.Series],
    from_column: Union[str, pd.Series],
    to_table: Union[str, pd.Series],
    to_column: Union[str, pd.Series]
) -> Union[str, pd.Series]:
    """
    Formats a relationship's table/columns into a fully qualified name.

    Parameters
    ----------
    from_table : Union[str, pd.Series]
        The name of the table on the 'from' side of the relationship.
    from_column : Union[str, pd.Series]
        The name of the column on the 'from' side of the relationship.
    to_table : Union[str, pd.Series]
        The name of the table on the 'to' side of the relationship.
    to_column : Union[str, pd.Series]
        The name of the column on the 'to' side of the relationship.

    Returns
    -------
    Union[str, pd.Series]
        The fully qualified relationship name.
    """

    return (
        _format_dax_object_name(from_table, from_column)
        + " -> "
        + _format_dax_object_name(to_table, to_column)
    )


def generate_guid():

    return str(uuid.uuid4())


def dotnet_isinstance(dotnet_ins, dotnet_type):
    from System import Object
    import clr

    if not isinstance(dotnet_ins, Object) or not issubclass(dotnet_type, Object):
        return False

    dotnet_type_name = str(clr.GetClrType(dotnet_type))
    ins_type = dotnet_ins.GetType()

    while ins_type is not None:
        if ins_type.IsGenericType:
            ins_type_name = str(ins_type.GetGenericTypeDefinition())
        else:
            ins_type_name = str(ins_type)
        if ins_type_name == dotnet_type_name:
            return True
        ins_type = ins_type.BaseType

    return False


def shared_docstring_params(**kwargs) -> Callable:
    def decorator(func: Callable) -> Callable:
        if func.__doc__:
            func.__doc__ = func.__doc__.format(**kwargs)
        return func
    return decorator
