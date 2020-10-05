from db import get_store

store = get_store()
for r in store.resources:
    print(f"Disabling collection validator for resource {r}...")
    res = store.db.command({"collMod": r, "validator": {}})
    print(f"Done! ({res})")
