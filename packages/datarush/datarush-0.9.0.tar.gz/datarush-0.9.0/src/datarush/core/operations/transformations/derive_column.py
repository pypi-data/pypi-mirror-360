"""Derive Column operation using Jinja2 expressions."""

from jinja2 import Template
from pydantic import Field

from datarush.core.dataflow import Operation, Tableset
from datarush.core.types import BaseOperationModel, TableStr


class DeriveColumnModel(BaseOperationModel):
    """Model for DeriveColumn operation."""

    table: TableStr = Field(title="Table", description="Table to modify")
    target_column: str = Field(title="Target Column", description="Name of the new column")
    template: str = Field(
        title="Jinja Template",
        description="Jinja template that uses row fields to compute a value",
    )


class DeriveColumn(Operation):
    """Derive a new column using a Jinja2 template evaluated per row."""

    name = "derive_column"
    title = "Derive Column"
    description = "Create a new column by rendering a Jinja2 template for each row"
    model: DeriveColumnModel

    def summary(self) -> str:
        """Provide operation summary."""
        return (
            f"Derive column **{self.model.target_column}** in `{self.model.table}` "
            "from Jinja template"
        )

    def operate(self, tableset: Tableset) -> Tableset:
        """Run operation."""
        df = tableset.get_df(self.model.table)
        template = Template(self.model.template)

        df[self.model.target_column] = df.apply(
            lambda row: template.render(**row.to_dict(), **self._template_context), axis=1
        )

        tableset.set_df(self.model.table, df)
        return tableset
