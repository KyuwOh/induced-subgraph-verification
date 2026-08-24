# Induced Degree Residue Verification

This repository contains exact computational verification for the
bipartite counterexamples used in the paper.

For a bipartite graph `G` and an integer `k`, the script computes

\[
f_k(G)=\max\{|S| : d_{G[S]}(v)\equiv 1 \pmod{k}
\text{ for every }v\in S\}.
\]

The search is exhaustive, but uses the bipartite structure to avoid
enumerating all `2^n` vertex subsets directly.

## Requirements

Python 3.8 or later. No third-party packages are required.

## Usage

```bash
python verify.py graph_k3.json
python verify.py graph_k4.json
```

Expected maximum values:

```text
G3: f_3(G3) = 5
G4: f_4(G4) = 6
```

The program also prints one maximum witness and the number of maximum
witnesses found.

## Adding another graph

Create another JSON file with the same format:

```json
{
  "name": "G",
  "k": 3,
  "left": ["a1", "a2"],
  "right": ["b1", "b2"],
  "biadjacency": [
    [1, 0],
    [0, 1]
  ]
}
```

Rows of `biadjacency` correspond to `left`, and columns correspond to
`right`.

## Method

For each subset `X` of the left bipartition, the program first computes
the right-side vertices `y` satisfying

`deg_X(y) == 1 (mod k)`.

Any feasible right-side set `Y` must be a subset of this set. The
program enumerates these submasks and checks the corresponding
left-side congruences. Thus every feasible induced subgraph is checked
exactly, while impossible pairs are skipped.

## Reproducibility

The graph data are stored explicitly as biadjacency matrices in the
JSON files. No randomness is used.
