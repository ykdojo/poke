import pyarrow as pa
import lance
import os

def write_lance_blobs():
    """Write binary data to Lance dataset with blob encoding"""
    
    dataset_path = "./test_simple_blobs.lance"
    
    # Clean up if exists
    if os.path.exists(dataset_path):
        import shutil
        shutil.rmtree(dataset_path)
    
    # Create simple test data - just binary strings
    test_data = [
        b"hello world",
        b"foo bar baz",
        b"testing lance blobs",
        b"this is binary data"
    ]
    
    print("Writing binary data:")
    for i, data in enumerate(test_data):
        print(f"  Row {i}: {data}")
        print(f"         (decoded: '{data.decode('utf-8')}')")
    
    # Create schema with blob encoding
    schema = pa.schema([
        pa.field("id", pa.int64()),
        pa.field("blob", 
                pa.large_binary(),
                metadata={"lance-encoding:blob": "true"})
    ])
    
    # Create PyArrow table
    table = pa.table({
        "id": list(range(len(test_data))),
        "blob": test_data
    }, schema=schema)
    
    # Write to Lance
    print(f"\nWriting to Lance dataset at {dataset_path}...")
    ds = lance.write_dataset(table, dataset_path, schema=schema)
    print(f"Written {len(ds)} rows")
    print("Write complete!\n")
    print("="*50)

def read_lance_blobs():
    """Read binary data from Lance dataset - fresh read from disk"""
    
    dataset_path = "./test_simple_blobs.lance"
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at {dataset_path}")
        return False
    
    # Fresh read - open dataset from path only
    print("\nReading Lance dataset from disk...")
    ds = lance.dataset(dataset_path)
    print(f"Opened dataset with {len(ds)} rows")
    print(f"Schema: {ds.schema}")
    
    # Read using blob API
    print("\nReading blobs using take_blobs API:")
    num_rows = len(ds)
    
    for i in range(num_rows):
        blobs = ds.take_blobs("blob", ids=[i])
        blob_file = blobs[0]
        
        # Read the blob content
        content = blob_file.read()
        
        print(f"  Row {i}: {content}")
        print(f"         (decoded: '{content.decode('utf-8')}')")
    
    # Also demonstrate regular table read
    print("\nReading using to_table():")
    table = ds.to_table()
    for i in range(len(table)):
        row_id = table["id"][i].as_py()
        blob_data = table["blob"][i]
        # Check what type we're getting
        if hasattr(blob_data, 'as_py'):
            blob_bytes = blob_data.as_py()
            if isinstance(blob_bytes, dict):
                print(f"  Row {row_id}: Got dict instead of bytes: {blob_bytes}")
            else:
                print(f"  Row {row_id}: {blob_bytes} (decoded: '{blob_bytes.decode('utf-8')}')")
        else:
            print(f"  Row {row_id}: Unexpected type: {type(blob_data)}")
    
    print("\n✅ Read complete!")
    return True

if __name__ == "__main__":
    try:
        # Write phase
        write_lance_blobs()
        
        # Read phase - completely separate, only uses file path
        read_lance_blobs()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()