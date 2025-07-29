import numpy as np
from difflib import SequenceMatcher
from collections import Counter
from typing import Dict, Any

def binary_confusion_matrix(reference: str, hypothesis: str) -> dict:
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()
    n = len(ref_words)
    m = len(hyp_words)
    dp = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i][j - 1], dp[i - 1][j])
    i, j = n, m
    TP = FP = FN = TN = 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_words[i - 1] == hyp_words[j - 1]:
            TP += 1
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            FP += 1
            FN += 1
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j] == dp[i][j - 1] + 1):
            FP += 1
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j] == dp[i - 1][j] + 1):
            FN += 1
            i -= 1
        else:
            break
    TN = 0
    return {'TP': TP, 'FP': FP, 'FN': FN, 'TN': TN}

def multiclass_confusion_matrix(reference: str, hypothesis: str, clean_hypothesis: str = '', semantic_threshold: float = 0.7) -> Counter:
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()
    clean_words = clean_hypothesis.strip().split() if clean_hypothesis else []
    n = len(ref_words)
    m = len(hyp_words)
    dp = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i][j - 1], dp[i - 1][j])
    i, j = n, m
    labels = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_words[i - 1] == hyp_words[j - 1]:
            labels.append('correct')
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            sim = SequenceMatcher(None, ref_words[i-1], hyp_words[j-1]).ratio()
            if sim >= semantic_threshold:
                labels.append('semantic hallucination')
            else:
                labels.append('substitution')
            i -= 1
            j -= 1
        elif j > 0 and (i == 0 or dp[i][j] == dp[i][j - 1] + 1):
            word = hyp_words[j-1]
            if clean_hypothesis and word not in clean_words:
                labels.append('noise-induced hallucination')
            else:
                labels.append('insertion')
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j] == dp[i - 1][j] + 1):
            labels.append('deletion/omission')
            i -= 1
        else:
            break
    return Counter(labels) 