# Diversity Metrics - Explained

## Overview

The system calculates the **Diversity Score** to measure how semantically different solutions are from each other.

---

## Diversity Score Explained

### What It Measures
How semantically different the solutions are from each other.

### Formula
```
Diversity = Average of all pairwise cosine distances
           = Mean(distance(solution_i, solution_j)) for all i < j
```

### How To Verify It

**Example from your test:**
- Solar Panels on Roofs
- Community Wind Farm
- **Result: Diversity = 0.249**

**Why 0.249?**
- These two solutions are **similar in domain** (both renewable energy)
- Both talk about infrastructure/generation
- They're **not vastly different** in semantic space
- Range: 0.0 (identical) → 1.0 (completely different)

**What would increase diversity?**
- Mix renewable energy WITH energy storage WITH consumption reduction
- Example: Solar + Battery storage + Smart home efficiency
- Expected diversity: ~0.35-0.45

### Testing It Yourself
Try analyzing:
1. **Low diversity** (expect 0.1-0.2):
   - "Solar panels on roofs"
   - "Solar panels on floating systems"

2. **High diversity** (expect 0.6-0.8):
   - "Solar panels for energy"
   - "Reduce consumption with smart meters"
   - "Plant trees to lower temperature"

---

## How It Works

### Step 1: Embedding Generation
- Convert each solution to a 384-dimensional vector using all-MiniLM-L6-v2
- Process both title and description together
- Captures semantic meaning

### Step 2: Distance Calculation
- Compute cosine distance between all solution pairs
- Distance = 1 - cosine_similarity (ranging 0 to 1)

### Step 3: Average for Diversity
- Compute mean across all pairwise distances
- Result is final diversity score (0-1)

---

## Validation

Results include validation checks (typically 4-8 checks passed):

✅ Score is between 0-1
✅ No NaN or infinity values
✅ Valid solution format
✅ Proper embedding computation
✅ Reasonable score range
✅ Metadata completeness

---

## Test Cases

### Test 1: Identical Solutions (Diversity should be ~0.0)
```
Solution 1: "Solar panels generate clean energy"
Solution 2: "Solar panels generate clean energy"
Expected Diversity: 0.0 (identical)
```

### Test 2: Completely Different (Diversity should be ~1.0)
```
Solution 1: "Solar energy from sun"
Solution 2: "Breeding dolphins for entertainment"
Expected Diversity: 0.9+ (nothing in common)
```

### Test 3: Similar but Different (Diversity should be ~0.3-0.4)
```
Solution 1: "Install solar panels on roofs"
Solution 2: "Install solar panels on farmland"
Expected Diversity: 0.2-0.3 (same concept, different location)
```

### Test 4: Diverse Renewable Approaches (Diversity should be ~0.5-0.6)
```
Solution 1: "Build solar farms in deserts"
Solution 2: "Install offshore wind turbines"
Solution 3: "Develop geothermal heating systems"
Expected Diversity: 0.45-0.55 (different technologies, same domain)
```

---

## Interpreting Your Results

**Low Diversity (0.0-0.2):** Solutions are very similar
- All in same domain
- Similar concepts/approaches
- Lacks variety
