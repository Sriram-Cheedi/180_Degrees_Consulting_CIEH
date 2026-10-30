
import sys

from src.database.council_metadata import update_council_name


if len(sys.argv) != 3:
    raise SystemExit(
        'Usage: python set_council_name.py RESPONSE_ID "Council Name"'
    )

response_id = int(sys.argv[1])
council_name = sys.argv[2]

update_council_name(response_id, council_name)

print(f"Council updated for response {response_id}: {council_name}")
