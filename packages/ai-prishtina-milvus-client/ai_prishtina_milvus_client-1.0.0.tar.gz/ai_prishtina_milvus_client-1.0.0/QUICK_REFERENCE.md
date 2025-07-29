# AI Prishtina Milvus Client - Quick Reference

## 🚀 **Installation**
```bash
pip install ai-prishtina-milvus-client
```

## ⚡ **Quick Start**
```python
import asyncio
from ai_prishtina_milvus_client import AsyncMilvusClient

async def main():
    client = AsyncMilvusClient({"host": "localhost", "port": 19530})
    await client.connect()
    
    # Create collection
    await client.create_collection("my_collection", dimension=128)
    
    # Insert vectors
    vectors = [[0.1] * 128 for _ in range(100)]
    ids = await client.insert("my_collection", vectors)
    
    # Search
    results = await client.search("my_collection", [vectors[0]], top_k=5)
    
    await client.disconnect()

asyncio.run(main())
```

## 📋 **Common Operations**

### **Collections**
```python
# Create
await client.create_collection("collection", dimension=768, index_type="HNSW")

# List
collections = await client.list_collections()

# Check existence
exists = await client.has_collection("collection")

# Drop
await client.drop_collection("collection")
```

### **Vectors**
```python
# Insert
ids = await client.insert("collection", vectors, metadata)

# Search
results = await client.search("collection", query_vectors, top_k=10)

# Get by IDs
vectors = await client.get("collection", ids=[1, 2, 3])

# Delete
await client.delete("collection", filter_expression="id in [1, 2, 3]")

# Count
count = await client.count("collection")
```

### **Indexes**
```python
# Create index
await client.create_index("collection", index_params={
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 200}
})

# Drop index
await client.drop_index("collection")
```

## 🔧 **Configuration Examples**

### **Basic Config**
```python
config = {
    "host": "localhost",
    "port": 19530,
    "timeout": 30
}
```

### **Advanced Config**
```python
config = {
    "host": "localhost",
    "port": 19530,
    "secure": True,
    "username": "admin",
    "password": "password",
    "pool_size": 10,
    "max_retries": 3,
    "validate_vectors": True
}
```

### **From Environment**
```python
# Set environment variables
export MILVUS_HOST=localhost
export MILVUS_PORT=19530

# Load automatically
client = AsyncMilvusClient.from_env()
```

## 🔍 **Index Types**

| Index Type | Use Case | Memory | Speed | Accuracy |
|------------|----------|---------|-------|----------|
| IVF_FLAT | Balanced | Medium | Medium | High |
| HNSW | High accuracy | High | Fast | Highest |
| IVF_SQ8 | Large datasets | Low | Medium | Medium |
| ANNOY | Memory efficient | Low | Fast | Medium |

## 📊 **Metric Types**

| Metric | Description | Use Case |
|--------|-------------|----------|
| L2 | Euclidean distance | General purpose |
| IP | Inner product | Normalized vectors |
| COSINE | Cosine similarity | Text embeddings |
| HAMMING | Hamming distance | Binary vectors |

## 🎯 **Search Parameters**

### **IVF_FLAT**
```python
search_params = {"nprobe": 10}  # 1-nlist
```

### **HNSW**
```python
search_params = {"ef": 64}  # 1-32768
```

### **IVF_SQ8**
```python
search_params = {"nprobe": 10}  # 1-nlist
```

## 🔒 **Security**
```python
from ai_prishtina_milvus_client.security import SecurityManager

# Initialize
security = SecurityManager(config={"encryption_key": "key"})

# Create user
await security.create_user("user", "password", ["read", "write"])

# Authenticate
token = await security.authenticate("user", "password")

# Encrypt data
encrypted = security.encrypt_data("sensitive_data")
```

## 📈 **Monitoring**
```python
from ai_prishtina_milvus_client.monitoring import MetricsCollector

# Initialize
metrics = MetricsCollector(config={"prometheus_gateway": "localhost:9091"})

# Time operations
with metrics.timer("search_operation"):
    results = await client.search(collection, vectors, top_k=10)

# Custom metrics
metrics.increment_counter("custom_searches")
metrics.set_gauge("active_connections", 5)
```

## 🌊 **Streaming**
```python
from ai_prishtina_milvus_client.streaming import KafkaStreamProcessor

# Initialize
processor = KafkaStreamProcessor(milvus_config, kafka_config)

# Produce
await processor.produce_message("topic", stream_message)

# Consume
async for message in processor.consume_messages("topic"):
    await processor.process_message(message)
```

## ❌ **Error Handling**
```python
from ai_prishtina_milvus_client.exceptions import (
    MilvusException,
    ConnectionError,
    CollectionNotFoundError,
    VectorDimensionError
)

try:
    await client.search("collection", vectors, top_k=10)
except CollectionNotFoundError:
    # Handle missing collection
    await client.create_collection("collection", dimension=768)
except VectorDimensionError as e:
    # Handle dimension mismatch
    print(f"Expected dimension: {e.expected}, got: {e.actual}")
except ConnectionError:
    # Handle connection issues
    await client.reconnect()
```

## 🧪 **Testing**
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires Docker)
docker-compose up -d
pytest tests/integration/ -v

# Performance tests
python tests/performance/benchmark.py
```

## 📚 **Resources**

- **Documentation**: https://docs.ai-prishtina.com/milvus-client
- **Examples**: https://github.com/ai-prishtina/milvus-client-examples
- **Issues**: https://github.com/ai-prishtina/milvus-client/issues
- **Discussions**: https://github.com/ai-prishtina/milvus-client/discussions

## 💡 **Tips**

1. **Use batch operations** for large datasets (1000+ vectors)
2. **Choose HNSW index** for high-accuracy searches
3. **Use IVF_SQ8** for memory-constrained environments
4. **Enable connection pooling** for high concurrency
5. **Implement proper error handling** with retries
6. **Monitor performance** with metrics collection
7. **Use environment variables** for configuration
8. **Validate vector dimensions** before insertion
9. **Use partitions** for large collections
10. **Enable encryption** for sensitive data

## 🔧 **Common Patterns**

### **Batch Processing**
```python
batch_size = 1000
for i in range(0, len(vectors), batch_size):
    batch = vectors[i:i+batch_size]
    await client.insert(collection, batch)
```

### **Error Retry**
```python
import asyncio

async def retry_operation(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

### **Connection Management**
```python
async with AsyncMilvusClient(config) as client:
    # Operations here
    pass  # Automatic cleanup
```
