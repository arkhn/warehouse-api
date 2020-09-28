from db import get_store

store = get_store()

print(f"Dropping ES index {store.search_engine.get_index_name()}...")
store.reset(mongo=False, es=True)
print("Done!")

print("Rebuilding ES index with mappings")
store.search_engine.create_es_index()
