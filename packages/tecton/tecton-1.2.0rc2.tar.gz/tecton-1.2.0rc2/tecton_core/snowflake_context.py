import logging
from typing import Any
from typing import Dict

from tecton_core import errors


logger = logging.getLogger(__name__)


class SnowflakeContext:
    """
    Get access to Snowflake connection and session.
    """

    _current_context_instance = None
    _session = None
    _params = None

    def __init__(self, connection_params):
        self._params = connection_params
        from snowflake.snowpark import Session

        self._session = Session.builder.configs(connection_params).create()

    def get_session(self):
        if self._session is None:
            raise errors.SNOWFLAKE_CONNECTION_NOT_SET
        return self._session

    def get_connection_params(self):
        if self._params is None:
            raise errors.SNOWFLAKE_CONNECTION_NOT_SET
        return self._params

    def get_connection(self):
        import snowflake.connector

        if self._params is None:
            raise errors.SNOWFLAKE_CONNECTION_NOT_SET

        return snowflake.connector.connect(**self._params)

    @classmethod
    def is_initialized(cls):
        return cls._current_context_instance is not None

    @classmethod
    def get_instance(cls) -> "SnowflakeContext":
        """
        Get the singleton instance of SnowflakeContext.
        """
        # If the instance doesn't exist, raise the error to instruct user to set connection first. Otherwise
        # return the current snowflake context.
        if cls._current_context_instance is not None:
            return cls._current_context_instance
        else:
            raise errors.SNOWFLAKE_CONNECTION_NOT_SET

    @classmethod
    def set_connection_params(cls, params: Dict[str, Any]) -> "SnowflakeContext":
        logger.debug("Generating new Snowflake session")
        # validate snowflake connection
        if not isinstance(params, dict):
            msg = "Connection params must be a dict"
            raise TypeError(msg)

        if not params.get("database"):
            msg = "database"
            raise errors.MISSING_SNOWFAKE_CONNECTION_REQUIREMENTS(msg)
        if not params.get("warehouse"):
            msg = "warehouse"
            raise errors.MISSING_SNOWFAKE_CONNECTION_REQUIREMENTS(msg)
        if not params.get("schema"):
            msg = "schema"
            raise errors.MISSING_SNOWFAKE_CONNECTION_REQUIREMENTS(msg)

        cls._current_context_instance = cls(params)
        return cls._current_context_instance
