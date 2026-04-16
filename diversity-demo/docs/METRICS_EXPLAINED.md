# Diversity Metric Explained

## Quick Definition

The `diversity_score` measures how semantically different the submitted solutions are.

- Range: `0.0` to `1.0`
- Higher score means more conceptual spread

## Fast Interpretation

- `0.00 - 0.20`: ideas are very similar
- `0.20 - 0.50`: moderate variation
- `0.50 - 1.00`: high diversity

## What it does not measure

- Not a quality score
- Not a feasibility score
- Not a business impact score

It is only semantic diversity.

## How it is computed

1. Embed each solution text using `all-MiniLM-L6-v2`
2. Compute pairwise cosine distances
3. Take mean of all unique pairs

For full technical detail (formula, validation, error model), see:

- [`METRICS_CALCULATION_AND_EMBEDDINGS.md`](./METRICS_CALCULATION_AND_EMBEDDINGS.md)
