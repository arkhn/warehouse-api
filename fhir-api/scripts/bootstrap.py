from db import get_store

store = get_store()
store.bootstrap(depth=3)
