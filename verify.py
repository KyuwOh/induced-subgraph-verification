#!/usr/bin/env python3
"""
Exact verification of f_k(G) for a bipartite graph G.

Input format: JSON containing
  - name: graph name
  - k: modulus
  - left: labels of the left bipartition
  - right: labels of the right bipartition
  - biadjacency: 0/1 matrix with rows indexed by left and columns by right

The search is exhaustive.  It uses the bipartite structure to avoid
iterating over all 2^n vertex subsets directly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Tuple


def load_graph(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    name = data.get("name", Path(path).stem)
    k = int(data["k"])
    left = list(data["left"])
    right = list(data["right"])
    M = data["biadjacency"]

    if len(M) != len(left):
        raise ValueError("Number of matrix rows does not match len(left).")
    if any(len(row) != len(right) for row in M):
        raise ValueError("Number of matrix columns does not match len(right).")
    if any(x not in (0, 1) for row in M for x in row):
        raise ValueError("The biadjacency matrix must contain only 0 and 1.")

    return name, k, left, right, M


def masks_from_matrix(M: List[List[int]]) -> Tuple[List[int], List[int]]:
    a = len(M)
    b = len(M[0])

    row_masks = []
    for row in M:
        mask = 0
        for j, value in enumerate(row):
            if value:
                mask |= 1 << j
        row_masks.append(mask)

    col_masks = []
    for j in range(b):
        mask = 0
        for i in range(a):
            if M[i][j]:
                mask |= 1 << i
        col_masks.append(mask)

    return row_masks, col_masks


def labels_from_mask(labels: List[str], mask: int) -> List[str]:
    return [label for i, label in enumerate(labels) if mask & (1 << i)]


def verify_fk(k: int, M: List[List[int]]):
    """
    Return (f_k(G), number_of_maximum_witnesses, one_witness).

    A witness is represented by a pair (x_mask, y_mask), where x_mask
    selects vertices on the left and y_mask selects vertices on the right.

    For fixed X on the left, a vertex y on the right may belong to a
    feasible witness only if deg_X(y) == 1 (mod k).  We enumerate exactly
    the subsets of those eligible right-side vertices and then test the
    left-side congruences.  Hence every feasible induced subgraph is
    checked, but many impossible pairs (X,Y) are skipped.
    """
    a = len(M)
    b = len(M[0])
    row_masks, col_masks = masks_from_matrix(M)

    # good_left[y_mask] is the set of left vertices x for which
    # deg_Y(x) == 1 (mod k).
    good_left = [0] * (1 << b)
    for y_mask in range(1 << b):
        mask = 0
        for i, row_mask in enumerate(row_masks):
            degree = (row_mask & y_mask).bit_count()
            if degree % k == 1:
                mask |= 1 << i
        good_left[y_mask] = mask

    best = 0
    number_of_best = 0
    best_witness = (0, 0)

    # A nonempty 1 mod k induced subgraph must meet both bipartition
    # classes, so x_mask = 0 and y_mask = 0 can be omitted.
    for x_mask in range(1, 1 << a):

        # eligible_right is the set of right vertices y satisfying
        # deg_X(y) == 1 (mod k).
        eligible_right = 0
        for j, col_mask in enumerate(col_masks):
            degree = (col_mask & x_mask).bit_count()
            if degree % k == 1:
                eligible_right |= 1 << j

        # Any feasible Y must be a submask of eligible_right.
        y_mask = eligible_right
        while y_mask:
            # The right-side congruences already hold because
            # y_mask is a subset of eligible_right.
            # The remaining condition is that every x in X belongs
            # to good_left[y_mask].
            if x_mask & ~good_left[y_mask] == 0:
                size = x_mask.bit_count() + y_mask.bit_count()

                if size > best:
                    best = size
                    number_of_best = 1
                    best_witness = (x_mask, y_mask)
                elif size == best:
                    number_of_best += 1

            y_mask = (y_mask - 1) & eligible_right

    return best, number_of_best, best_witness


def main():
    parser = argparse.ArgumentParser(
        description="Exactly compute f_k(G) for a bipartite graph."
    )
    parser.add_argument("graph", help="Path to a graph JSON file.")
    args = parser.parse_args()

    name, k, left, right, M = load_graph(args.graph)
    best, count, (x_mask, y_mask) = verify_fk(k, M)

    left_witness = labels_from_mask(left, x_mask)
    right_witness = labels_from_mask(right, y_mask)

    print(f"Graph: {name}")
    print(f"k = {k}")
    print(f"|V(G)| = {len(left) + len(right)}")
    print(f"f_k(G) = {best}")
    print(f"number of maximum witnesses = {count}")
    print("one maximum witness:")
    print("  left :", left_witness)
    print("  right:", right_witness)


if __name__ == "__main__":
    main()
