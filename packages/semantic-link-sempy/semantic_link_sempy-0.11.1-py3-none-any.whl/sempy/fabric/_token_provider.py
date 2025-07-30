from abc import ABC, abstractmethod
import datetime
import jwt
from typing import Callable, Literal


class TokenProvider(ABC):
    """
    Abstract base class for logic that acquires auth tokens.
    """
    @abstractmethod
    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi") -> str:
        """
        Get implementation specific token.

        Returns
        -------
        str
            Auth token.
        """
        raise NotImplementedError


class ConstantTokenProvider(TokenProvider):
    """
    Wrapper around a token that was externally acquired by the user.

    Parameters
    ----------
    token : str
        Token that will be supplied upon requst.
    """
    def __init__(self, pbi_token, storage_token=None, sql_token=None):
        self.token_dict = {
            "pbi": pbi_token,
            "storage": storage_token,
            "sql": sql_token
        }

    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi"):
        """
        Get token.

        Returns
        -------
        str
            Fixed token provided by user during instantiation.
        """
        return self.token_dict.get(audience)


class SynapseTokenProvider(TokenProvider):
    """
    Acquire an auth token from within a Trident workspace.
    """
    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi"):
        """
        Get token from within a Trident workspace.

        Returns
        -------
        str
            Token acquired from Trident libraries.
        """
        return _get_token(audience=audience)


def _get_token(audience: Literal["pbi", "storage", "sql"]) -> str:
    """
    Get token of the specified audience from Fabric token library.

    Some old VHDs on Fabric may not have the latest `token_utils`, so we add
    a fallback try-catch to switch to the legacy method.

    We should remove getting from `PyTridentTokenLibrary` in the future.
    """
    if audience not in ("pbi", "storage", "sql"):
        raise ValueError(f"Invalid token audience: {audience}")
    try:
        # This is to patch token_utils to support sql token, which is not necessary in newer versions of token_utils.
        from synapse.ml.fabric.token_utils import TokenServiceClient
        TokenServiceClient.resource_mapping['sql'] = 'sql'

        from synapse.ml.fabric.token_utils import TokenUtils
        token_utils = TokenUtils()
        match audience:
            case "storage":
                return token_utils.get_storage_token()
            case "sql":
                return token_utils.get_access_token("sql")
            case "pbi":
                if hasattr(token_utils, "get_ml_aad_token"):
                    return token_utils.get_ml_aad_token()
                else:
                    return token_utils.get_aad_token()
    except ImportError:
        try:
            from trident_token_library_wrapper import PyTridentTokenLibrary
            return PyTridentTokenLibrary.get_access_token(audience)
        except ImportError:
            raise RuntimeError("No token_provider specified and unable to obtain token from the environment")


def _get_token_expiry_raw_timestamp(token: str) -> int:
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("exp", 0)
    except jwt.DecodeError:
        # Token is not a valid token (ex: using myToken in tests)
        return 0


def _get_token_seconds_remaining(token: str) -> int:
    exp_time = _get_token_expiry_raw_timestamp(token)
    now_epoch = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds()
    return int(exp_time - now_epoch)


def _get_token_expiry_utc(token: str) -> str:
    exp_time = _get_token_expiry_raw_timestamp(token)
    return str(datetime.datetime.utcfromtimestamp(exp_time))


def create_on_access_token_expired_callback(token_provider: TokenProvider) -> Callable:
    from System import DateTimeOffset
    from Microsoft.AnalysisServices import AccessToken

    # convert seconds to .NET date time
    def get_token_expiration_datetime(token):

        seconds = _get_token_seconds_remaining(token)

        return DateTimeOffset.UtcNow.AddSeconds(seconds)

    def get_access_token(old_token):
        token = token_provider()

        expiration = get_token_expiration_datetime(token)

        return AccessToken(token, expiration)

    return get_access_token
