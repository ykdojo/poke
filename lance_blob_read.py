import lance

# Open the Lance dataset
dataset_path = "./youtube.lance"
print(f"Opening Lance dataset from {dataset_path}...")
ds = lance.dataset(dataset_path)

print(f"Dataset info:")
print(f"  - Number of rows: {len(ds)}")
print(f"  - Schema: {ds.schema}")

# Read blob data using take_blobs
print("\nFetching blob data from row with id=0...")
blobs = ds.take_blobs("video", ids=[0])

# Get the first (and only) blob
blob = blobs[0]
print(f"Blob type: {type(blob)}")
print(f"Blob is a file-like object: {hasattr(blob, 'read')}")

# Read some bytes to verify it works
sample_bytes = blob.read(100)
print(f"First 100 bytes of video (hex): {sample_bytes[:20].hex()}...")

# Reset position
blob.seek(0)

# Get the full size
blob.seek(0, 2)  # Seek to end
size = blob.tell()
blob.seek(0)  # Reset to beginning
print(f"Blob size: {size:,} bytes")

print("\nBlob data successfully retrieved as a lazy file-like object!")