import numpy as np
from difflib import SequenceMatcher
from typing import Dict, Any

def calculate_similarity(text1: str, text2: str) -> float:
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

def calculate_levenshtein_distance(text1: str, text2: str) -> int:
    size_x = len(text1) + 1
    size_y = len(text2) + 1
    matrix = np.zeros((size_x, size_y))
    for x in range(size_x):
        matrix[x, 0] = x
    for y in range(size_y):
        matrix[0, y] = y
    for x in range(1, size_x):
        for y in range(1, size_y):
            if text1[x-1] == text2[y-1]:
                matrix[x, y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix[x, y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1] + 1,
                    matrix[x, y-1] + 1
                )
    return int(matrix[size_x-1, size_y-1])

def calculate_wer_components(reference: str, hypothesis: str) -> dict:
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()
    n = len(ref_words)
    m = len(hyp_words)
    dp = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    op_matrix = [['' for _ in range(m + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
                op_matrix[i][j] = 'OK'
            else:
                substitution = dp[i - 1][j - 1] + 1
                insertion = dp[i][j - 1] + 1
                deletion = dp[i - 1][j] + 1
                min_op = min(substitution, insertion, deletion)
                dp[i][j] = min_op
                if min_op == substitution:
                    op_matrix[i][j] = 'S'
                elif min_op == insertion:
                    op_matrix[i][j] = 'I'
                else:
                    op_matrix[i][j] = 'D'
    i, j = n, m
    S = D = I = 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and op_matrix[i][j] == 'OK':
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and op_matrix[i][j] == 'S':
            S += 1
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or op_matrix[i][j] == 'I'):
            I += 1
            j -= 1
        elif i > 0 and (j == 0 or op_matrix[i][j] == 'D'):
            D += 1
            i -= 1
        else:
            break
    wer = (S + D + I) / max(1, len(ref_words))
    return {'WER': wer, 'Substitutions': S, 'Deletions': D, 'Insertions': I, 'N': len(ref_words)} 