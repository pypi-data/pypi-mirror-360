import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from collections import Counter

def save_confusion_heatmap(confusion_list, output_folder, filename, title, cmap, xticklabels, yticklabels):
    agg = {'TP': 0, 'FP': 0, 'FN': 0, 'TN': 0}
    for cm in confusion_list:
        for k in agg:
            agg[k] += cm[k]
    matrix = np.array([[agg['TP'], agg['FP']], [agg['FN'], agg['TN']]])
    plt.figure(figsize=(4, 3))
    sns.heatmap(matrix, annot=True, fmt='d', cmap=cmap, xticklabels=xticklabels, yticklabels=yticklabels)
    plt.title(title)
    plt.tight_layout()
    out_path = os.path.join(output_folder, filename)
    plt.savefig(out_path)
    plt.close()
    print(f'{title} saved to: {out_path}')

def save_multiclass_confusion_heatmap(counter, output_folder, filename, title, cmap):
    classes = ['correct', 'insertion', 'substitution', 'deletion/omission', 'semantic hallucination', 'noise-induced hallucination']
    values = [counter.get(cls, 0) for cls in classes]
    matrix = np.array(values).reshape(1, -1)
    plt.figure(figsize=(10, 5))
    sns.heatmap(matrix, annot=True, fmt='d', cmap=cmap, xticklabels=classes, yticklabels=['Count'])
    plt.title(title)
    plt.tight_layout()
    out_path = os.path.join(output_folder, filename)
    plt.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close()
    print(f'{title} saved to: {out_path}') 