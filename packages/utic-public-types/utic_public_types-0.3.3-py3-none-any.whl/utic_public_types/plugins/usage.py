import uuid

from pydantic import AwareDatetime, BaseModel, Field, conint

SKU_CHARS = "[A-Za-z0-9_]"
SKU_FORMAT = "2.3.8.3"

SKU_CHUNKSIZES = list(map(int, SKU_FORMAT.split(".")))
SKU_LENGTH = sum(SKU_CHUNKSIZES) + len(SKU_CHUNKSIZES) - 1
SKU_REGEX = r"\.".join([f"{SKU_CHARS}{{{n}}}" for n in SKU_CHUNKSIZES])


class UnstructuredUsageRecord(BaseModel):
    sku: str = Field(
        title="SKU",
        min_length=SKU_LENGTH,
        max_length=SKU_LENGTH,
        pattern=f"^{SKU_REGEX}$",
        description="Some coordination is expected before moving a SKU into production."
        "Pattern is FAMILY.SUBFAMILY.PRODUCT.METRIC where each section is of "
        "length 2, 3, 8, and 3 respectively. Allowable chars are uppercase and "
        "lowercase alphabet plus 0-9 and underscore [A-Za-z0-9_]]",
        examples=[
            "1c.th3.atechars.too",
            "12.345.67890123.456",
            "Ab.cDe.FgHiJkLm.nOp",
            "al.pha._numeric._0_",
        ],
    )
    quantity: conint = Field(
        title="Quantity",
        ge=0,
        lt=2**64,
        description="Number of units. Meaning depends on the SKU. Must fit into int64.",
        examples=[0, 1, 47, 150_000],
    )
    item_uuid: uuid.UUID = Field(
        title="Item UUID",
        description="Unique identifier for the item being worked on which created the usage."
        "Take this value from provided inputs.",
        examples=[uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()],
    )
    subitem_id: conint = Field(
        title="Sub-Item Identifier",
        ge=0,
        lt=2**64,
        description="Refers to individual items within a work item. For example, "
        "the item_uuid might refer to a document, this subitem_id can "
        "uniquely refer to each section, page, image, etc. "
        "Take from input if provided, but if your plugin generates "
        "the subitems, you can create values for this field. "
        "No mechanism currently exists to prevent collisions. Authors beware.",
        examples=[0, 1, 47, 150_000],
    )
    timestamp: AwareDatetime = Field(
        title="Timestamp",
        description="Date and Time of when the usage took place. "
        "Many formats can be understood. See "
        "https://docs.pydantic.dev/2.0/usage/types/datetime/#validation-of-datetime-types",
    )
