from search.indexer import MiniSearchEngine

engine = MiniSearchEngine()
engine.build_index()

result = engine.search("python search engine")
print(result)
