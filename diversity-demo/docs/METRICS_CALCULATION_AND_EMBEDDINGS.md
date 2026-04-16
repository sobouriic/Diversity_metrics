# Metrics, Calculations, and Embeddings

## 1) What the system measures

The system returns one primary metric:

- `diversity_score` in `[0, 1]`

Interpretation:
- `0.0` means solutions are semantically very similar
- `1.0` means solutions are semantically very different

## 2) Input normalization

Each solution is represented as:

```json
{
  "title": "string",
  "description": "string"
}
```

For scoring, each solution text is built as:

`"<title>. <description>"`

If mission/goal context is provided, they are prepended to each solution text.

## 3) Embedding model

The backend uses:
- `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional embedding vectors

Pipeline:
1. Convert each solution text to an embedding vector
2. Build pairwise cosine-distance matrix
3. Aggregate pairwise distances into one score

## 4) Diversity formula

For `N` solutions (`N >= 2`), diversity is:

\[
D = \frac{1}{\binom{N}{2}} \sum_{i<j} \text{cosine\_distance}(e_i, e_j)
\]

Where:
- `e_i` is embedding vector of solution `i`
- `cosine_distance = 1 - cosine_similarity`

Only the upper triangle (`i < j`) is used to avoid duplicate/self pairs.

## 5) Validation and safety checks

Validation includes:
- Input schema checks (types, required fields, min/max lengths)
- Minimum and maximum solution counts
- Payload size checks
- Range clamping to keep score in `[0, 1]`
- JSON/body validation with structured error responses

Standard error shape:

```json
{
  "detail": "human-readable message",
  "error_code": "machine_code",
  "request_id": "trace_id"
}
```

## 6) Idea-tree support

`/api/analyze` accepts either:
- `solutions` list (manual mode), or
- tree payload (`tree`, `idea_tree`, or `posts`)

When tree input is used, the backend recursively extracts nodes where:

`type == "solution"`

Each extracted node is normalized to `{id, title, description}` before scoring.

## 7) Practical reading guide

- `0.00 - 0.20`: highly overlapping ideas
- `0.20 - 0.50`: moderate variety
- `0.50 - 1.00`: strong conceptual diversity

This metric captures semantic spread, not quality or feasibility.
