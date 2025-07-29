"""
Module: advanced_search_example.py

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

from ai_prishtina_milvus_client import AdvancedSearch, SearchConfig

client = ...  # Your Milvus client instance
search_config = SearchConfig(metric_type="L2", top_k=5)
search = AdvancedSearch(client, search_config)
vectors = [[0.1] * 128]
# results = search.hybrid_search(vectors=vectors, text_query="example")
# print(results)
print("AdvancedSearch ready for hybrid search.") 