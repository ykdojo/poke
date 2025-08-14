import pyarrow as pa

schema = pa.schema(
    [
        pa.field("id", pa.int64()),
        pa.field("video",
            pa.large_binary(),
            metadata={"lance-encoding:blob": "true"}
        ),
    ]
)