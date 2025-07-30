# Recallio Python Client

A lightweight Python wrapper for the [Recallio](https://app.recallio.ai) API.

## Installation

```bash
pip install recallio
```

## Usage

```python
from recallio import (
    RecallioClient,
    MemoryWriteRequest,
    MemoryRecallRequest,
    RecallSummaryRequest,
    GraphAddRequest,
    GraphSearchRequest,
    MemoryExportRequest,
)

client = RecallioClient(api_key="YOUR_RECALLIO_API_KEY")

req = MemoryWriteRequest(
    userId="user_123",
    projectId="project_abc",
    content="The user prefers dark mode and wants notifications disabled on weekends",
    consentFlag=True,
)

memory = client.write_memory(req)
print(memory.id)

# recall memories
recall_req = MemoryRecallRequest(
    projectId="project_abc",
    userId="user_123",
    query="dark mode",
    scope="user",
    reRank=True,
)
results = client.recall_memory(recall_req)
for m in results:
    print(m.content, m.similarityScore)

# summarized recall
summary_req = RecallSummaryRequest(
    projectId="project_abc",
    userId="user_123",
    scope="user",
)
summary = client.recall_summary(summary_req)
print(summary.content)

# add data to the knowledge graph
graph_req = GraphAddRequest(
    data="John works at OpenAI in San Francisco",
    user_id="user_123",
    project_id="project_abc",
)
client.add_graph_memory(graph_req)

# search the graph
search_req = GraphSearchRequest(
    query="Where does John work?",
    user_id="user_123",
)
graph_results = client.search_graph_memory(search_req)
for r in graph_results:
    print(r.source, r.relationship, r.destination)

# export memories as JSON
export_req = MemoryExportRequest(
    type="fact",
    format="json",
    userId="user_123",
)
json_data = client.export_memory(export_req)
print(json_data)
```
