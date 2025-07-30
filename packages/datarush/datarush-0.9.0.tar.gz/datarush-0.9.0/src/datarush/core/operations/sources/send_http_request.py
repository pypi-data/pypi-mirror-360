"""Send HTTP request operation."""

from typing import Literal

import pandas as pd
import requests
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, StringMap, TextStr


class SendHttpRequestModel(BaseOperationModel):
    """Model for sending HTTP requests."""

    method: Literal["GET", "POST", "PUT", "DELETE"] = Field(
        title="Method", description="HTTP method to use"
    )
    url: str = Field(title="URL", description="Target URL")
    headers: StringMap = Field(
        title="Headers", description="Request headers", default_factory=StringMap
    )
    params: StringMap = Field(
        title="Query Parameters", description="Query parameters", default_factory=StringMap
    )
    body: TextStr = Field(
        title="Request Body",
        description="Request body (for POST or PUT only)",
        default=TextStr(""),
    )
    response_format: Literal["json", "raw"] = Field(
        title="Response Format",
        description="How to parse the response body into a dataframe",
        default="json",
    )
    output_table: str = Field(title="Output Table", description="Table to store response data")


class SendHttpRequest(Operation):
    """Send an HTTP request."""

    name = "send_http_request"
    title = "Send HTTP Request"
    description = "Send an HTTP request and parse the response into a table"
    model: SendHttpRequestModel

    def summary(self) -> str:
        """Return a summary of the operation."""
        return (
            f"Send {self.model.method} request to {self.model.url} "
            f"and store parsed {self.model.response_format} response in `{self.model.output_table}`"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Execute the HTTP request and parse the response."""
        method = self.model.method
        body = self.model.body if method in ["POST", "PUT"] else None

        response = requests.request(
            method=method,
            url=self.model.url,
            headers=self.model.headers,
            params=self.model.params,
            data=body,
        )

        if self.model.response_format == "raw":
            df = pd.DataFrame([{"body": response.text}])
        elif self.model.response_format == "json":
            try:
                parsed = response.json()
                if isinstance(parsed, list):
                    df = pd.DataFrame(parsed)
                else:
                    df = pd.DataFrame([parsed])
            except Exception as e:
                raise ValueError(f"Failed to parse JSON: {e}")
        else:
            raise ValueError(f"Unsupported response format: {self.model.response_format}")

        tableset.set_df(self.model.output_table, df)
        return tableset
