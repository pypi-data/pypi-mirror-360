from typing import Any, Literal, overload

import pydantic
from httpx import Timeout
from opsduty_client.client import AuthenticatedClient, Client


class Settings(pydantic.BaseModel):
    OPSDUTY_BASE_URL: str = pydantic.Field(default="https://opsduty.io")
    REQUEST_TIMEOUT: int = pydantic.Field(default=10)
    ACCESS_TOKEN: str | None = pydantic.Field(default=None)

    @classmethod
    def field_default(cls, name: str) -> Any:
        field = cls.model_fields[name]
        return field.default

    @overload
    def get_client(
        self, require_authentication: Literal[True]
    ) -> AuthenticatedClient | None: ...

    @overload
    def get_client(self, require_authentication: Literal[False]) -> Client: ...

    def get_client(
        self, require_authentication: Literal[True, False]
    ) -> AuthenticatedClient | Client | None:
        """
        Return the appropriate API client based on the provided settings.
        """

        if require_authentication:
            if self.ACCESS_TOKEN:
                return AuthenticatedClient(
                    base_url=self.OPSDUTY_BASE_URL,
                    token=self.ACCESS_TOKEN,
                    timeout=Timeout(float(self.REQUEST_TIMEOUT)),
                    raise_on_unexpected_status=True,
                )
            else:
                return None

        return Client(
            base_url=self.OPSDUTY_BASE_URL,
            timeout=Timeout(float(self.REQUEST_TIMEOUT)),
            raise_on_unexpected_status=True,
        )


settings = Settings()
