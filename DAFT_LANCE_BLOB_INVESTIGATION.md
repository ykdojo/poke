# Daft Lance Blob Issue Investigation

## Issue Summary
**GitHub Issue**: https://github.com/Eventual-Inc/Daft/issues/4939  
**PR with Fix**: https://github.com/Eventual-Inc/Daft/pull/4940

### Problem
When writing to Lance using Daft's `write_lance()` with blob metadata, the data is written using Legacy binary encoding instead of the required struct/blob encoding. This causes a panic when trying to use Lance's `take_blobs()` API.

### Error Reproduced
```
PanicException: Expected a struct encoding because we have a struct field 
in the schema but got the encoding Legacy(ArrayEncoding { array_encoding: 
Some(Binary(Binary {...})) })
```

## Current Setup

### Environment
- Python 3.13 virtual environment at `.venv/`
- Installed packages:
  - `daft==0.5.11`
  - `pylance==0.32.1` 
  - `pyarrow==21.0.0`
  - Other dependencies in `requirements.txt`

### Test Files Created
1. **`test_daft_lance_issue.py`** - Reproduces the issue
2. **`lance_blob_simple_test.py`** - Shows working Lance blob API directly
3. **`lance_blob_write.py`** and **`lance_blob_read.py`** - Video blob examples

### Key Finding
The issue is that while Daft preserves the schema metadata (`"lance-encoding:blob": "true"`), it doesn't actually encode the data in the blob format that Lance expects.

## Next Steps: Building and Testing PR #4940

### 1. Set Up Daft Development Environment

Since we need to test PR #4940, we need to:

1. **Clone Daft repository**
   ```bash
   git clone https://github.com/Eventual-Inc/Daft.git
   cd Daft
   ```

2. **Check build requirements**
   - Look for `setup.py`, `pyproject.toml`, or build documentation
   - Check if Rust toolchain is needed (Daft has Rust components)
   - Review `CONTRIBUTING.md` or development docs

3. **Build baseline (main branch)**
   ```bash
   git checkout main
   # Build commands will depend on project structure
   # Likely: pip install -e . or similar
   ```

4. **Test baseline works**
   - Run our `test_daft_lance_issue.py` with the built version
   - Confirm it still reproduces the issue

### 2. Test PR #4940

1. **Fetch and checkout PR**
   ```bash
   git fetch origin pull/4940/head:pr-4940
   git checkout pr-4940
   ```

2. **Build PR version**
   ```bash
   # Rebuild with PR changes
   # Same build command as baseline
   ```

3. **Test if fix works**
   - Run `test_daft_lance_issue.py` again
   - Verify that `take_blobs()` no longer panics
   - Check that blob data can be read correctly

### 3. What to Verify in PR #4940

Based on the issue, the PR should:
- Ensure Daft writes data using proper blob/struct encoding when `lance-encoding:blob` metadata is present
- Not just preserve metadata but actually use the correct encoding format
- Make the written data compatible with Lance's blob API

### 4. Test Script to Run

```python
# After building PR #4940, run this to verify the fix
import os
import shutil
import pyarrow as pa
import daft
from daft import Schema
import lance

LANCE_PATH = "./test_pr_fix.lance"

# Clean up
if os.path.exists(LANCE_PATH):
    shutil.rmtree(LANCE_PATH)

# Create schema with blob metadata
schema = pa.schema([
    pa.field("blob", pa.large_binary(), metadata={"lance-encoding:blob": "true"}),
])

# Create and write Daft dataframe
df = daft.from_pydict({"blob": [b"foo", b"bar"]})
daft_schema = Schema.from_pyarrow_schema(schema)
df.write_lance(LANCE_PATH, schema=daft_schema)

# Test if blob API works now
ds = lance.dataset(LANCE_PATH)
try:
    blobs = ds.take_blobs("blob", [0])
    content = blobs[0].read()
    print(f"✅ SUCCESS! Blob content: {content}")
    print("PR #4940 fixes the issue!")
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("PR #4940 does not fix the issue")
```

## Important Notes

- We're on branch `lance-blob-experiments` with our test files
- The issue is confirmed and reproducible
- We need to build Daft from source to test the PR
- May need Rust toolchain since Daft has Rust components
- Check Daft's CI/build configuration for exact build steps

## Commands Summary

```bash
# Current branch
git branch  # lance-blob-experiments

# Files created
ls *.py  # test_daft_lance_issue.py, lance_blob_*.py, test_pyarrow.py

# Virtual environment
source .venv/bin/activate

# Test reproduction
python test_daft_lance_issue.py  # Should show the panic error
```