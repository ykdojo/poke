import pyarrow as pa
import lance
import urllib.request
import os

# Step 1: Define the schema with blob metadata
schema = pa.schema(
    [
        pa.field("id", pa.int64()),
        pa.field("video",
            pa.large_binary(),
            metadata={"lance-encoding:blob": "true"}
        ),
    ]
)

# Step 2: Download sample video file
video_file = "sample_video.mp4"
if not os.path.exists(video_file):
    print("Downloading sample video...")
    urllib.request.urlretrieve(
        "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
        video_file
    )
    print(f"Downloaded {video_file}")
else:
    print(f"Using existing {video_file}")

# Step 3: Read the video file content
print("Reading video file...")
with open(video_file, 'rb') as f:
    video_data = f.read()
print(f"Video size: {len(video_data):,} bytes")

# Step 4: Create PyArrow table with blob data
print("Creating PyArrow table with blob data...")
table = pa.table({
    "id": [1],
    "video": [video_data],
}, schema=schema)

# Step 5: Write to Lance dataset
dataset_path = "./youtube.lance"
print(f"Writing to Lance dataset at {dataset_path}...")
ds = lance.write_dataset(
    table,
    dataset_path,
    schema=schema
)

print(f"Successfully created Lance dataset with blob data!")
print(f"Dataset has {len(ds)} row(s)")
print(f"Schema: {ds.schema}")