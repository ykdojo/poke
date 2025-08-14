"""
Reproduce Daft issue #4939 with Lance blob encoding
https://github.com/Eventual-Inc/Daft/issues/4939

ERROR REPRODUCED:
When writing to Lance using Daft's write_lance() with blob metadata,
the data is written using Legacy binary encoding instead of the required
struct/blob encoding. This causes a panic when trying to use Lance's 
take_blobs() API:

PanicException: Expected a struct encoding because we have a struct field 
in the schema but got the encoding Legacy(ArrayEncoding { array_encoding: 
Some(Binary(Binary {...})) })

The issue is that while Daft preserves the schema metadata 
("lance-encoding:blob": "true"), it doesn't actually encode the data 
in the blob format that Lance expects.
"""

import os
import shutil
import pyarrow as pa
import daft
from daft import Schema

LANCE_PATH = "./daft_lance_test.lance"

def test_daft_write_lance_with_blob():
    """Test writing Lance dataset with blob encoding using Daft"""
    
    print("=" * 60)
    print("Testing Daft write_lance with blob encoding")
    print("=" * 60)
    
    # Clean up if exists
    if os.path.exists(LANCE_PATH):
        shutil.rmtree(LANCE_PATH)
        print(f"Cleaned up existing {LANCE_PATH}")
    
    # Step 1: Create PyArrow schema with blob metadata
    print("\n1. Creating PyArrow schema with blob metadata...")
    schema = pa.schema([
        pa.field("blob", pa.large_binary(), metadata={"lance-encoding:blob": "true"}),
    ])
    print(f"   Schema: {schema}")
    
    # Step 2: Create Daft dataframe
    print("\n2. Creating Daft dataframe...")
    df = daft.from_pydict({
        "blob": [b"foo", b"bar"],
    })
    print(f"   DataFrame created with {df.count()} rows")
    print(f"   DataFrame schema: {df.schema()}")
    
    # Step 3: Write to Lance using Daft with explicit schema
    print("\n3. Writing to Lance with Daft...")
    try:
        # Convert PyArrow schema to Daft schema
        daft_schema = Schema.from_pyarrow_schema(schema)
        print(f"   Daft schema: {daft_schema}")
        
        # Write to Lance
        df.write_lance(LANCE_PATH, schema=daft_schema)
        print(f"   ✓ Successfully wrote to {LANCE_PATH}")
        return True
        
    except Exception as e:
        print(f"   ✗ Error writing with Daft: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("Reproducing Daft issue #4939")
    print("https://github.com/Eventual-Inc/Daft/issues/4939\n")
    
    # Test Daft write_lance
    success = test_daft_write_lance_with_blob()
    
    # Summary
    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    if success:
        print("✓ Write completed successfully")
    else:
        print("✗ Write failed")