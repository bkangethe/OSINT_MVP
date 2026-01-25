import asyncio
from osint import check_username, batch_lookup

# ---------------------------
# --- Configuration ---------
# ---------------------------

# Example single username to check
single_username = "john-doe"

# Example list of usernames for batch checking
batch_usernames = ["john-doe", "example123", "nonexistentuser"]

# Output files
output_csv = "results.csv"
output_json = "results.json"

# ---------------------------
# --- Run Single Username ---
# ---------------------------
print(f"Checking single username: {single_username}")
single_result = asyncio.run(check_username(single_username))
print(single_result)
print("\n")

# ---------------------------
# --- Run Batch Lookup ------
# ---------------------------
print(f"Running batch check for {len(batch_usernames)} usernames...")
batch_results = asyncio.run(batch_lookup(batch_usernames, output_csv=output_csv, output_json=output_json))

print("\nBatch results:")
for r in batch_results:
    print(r)

print(f"\n✅ Batch results saved to {output_csv} and {output_json}")
