#!/usr/bin/env python3
"""
Classification metrics used throughout the paper's Results section:
accuracy, precision, recall, F1, false positive rate, false negative
rate, and the VD-S metric (Ding et al., PrimeVul).

Reproduces Tables 6, 7, and 8.

Usage as a script:
  python compute_classification_metrics.py

Or import the functions directly:
  from compute_classification_metrics import classification_row, vds_row
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
)

LLM_MODELS = ['codellama', 'starcoder2', 'deepseek', 'mistral', 'wizardcoder']
STATIC_TOOLS = ['flawfinder', 'cppcheck', 'semgrep', 'infer', 'codeql']
STAGES = ['stage1', 'stage2', 'stage3', 'stage4']


def classification_row(y_true, y_pred):
    """Compute accuracy, precision, recall, F1, FPR, FNR for one prediction column."""
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
    return {
        'acc': round(acc, 3), 'prec': round(prec, 3), 'rec': round(rec, 3),
        'f1': round(f1, 3), 'fpr': round(fpr, 3), 'fnr': round(fnr, 3)
    }


def vds_row(y_true, y_pred, fpr_threshold=0.05):
    """
    Vulnerability Detection Score (Ding et al., PrimeVul): FNR at a
    constrained FPR. Returns 'N/A' if the FPR threshold is not met.
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else np.nan
    eligible = fpr <= fpr_threshold
    vds = round(fnr, 3) if (eligible and not np.isnan(fnr)) else 'N/A'
    return {
        'fpr': round(fpr, 3),
        'vds': vds,
        'eligible': 'Yes' if (eligible and vds != 'N/A') else 'No'
    }


def build_table6(llm_master):
    """Table 6: LLM classification performance across all 4 SDLC stages."""
    rows = []
    for model in LLM_MODELS:
        for stage in STAGES:
            sub = llm_master[llm_master['stage_name'] == stage]
            row = classification_row(sub['ground_truth'], sub[f'{model}_pred'])
            rows.append({'model': model, 'stage': stage, **row})
    return pd.DataFrame(rows)


def build_table7(static_master, native_stage=3):
    """
    Table 7: static tool classification performance. Static tools are
    code-only and confirmed stage-invariant, so a single measurement per
    tool is reported using the native stage's data.
    """
    sub = static_master[static_master['stage'] == native_stage]
    rows = []
    for tool in STATIC_TOOLS:
        row = classification_row(sub['ground_truth'], sub[f'{tool}_pred'])
        rows.append({'tool': tool, **row})
    return pd.DataFrame(rows)


def build_table8(llm_master, fpr_threshold=0.05):
    """Table 8: VD-S metric across all models and stages."""
    rows = []
    for model in LLM_MODELS:
        for stage in STAGES:
            sub = llm_master[llm_master['stage_name'] == stage]
            row = vds_row(sub['ground_truth'], sub[f'{model}_pred'], fpr_threshold)
            rows.append({'model': model, 'stage': stage, **row})
    return pd.DataFrame(rows)


if __name__ == '__main__':
    llm_master = pd.read_csv('llm_master_v2.csv')
    static_master = pd.read_csv('static_master.csv')

    table6 = build_table6(llm_master)
    print("Table 6: LLM classification performance")
    print(table6.to_string(index=False))
    table6.to_csv('table6_llm_classification_corrected.csv', index=False)

    print()
    table7 = build_table7(static_master)
    print("Table 7: static tool classification performance")
    print(table7.to_string(index=False))
    table7.to_csv('table7_static_classification_corrected.csv', index=False)

    print()
    table8 = build_table8(llm_master)
    print("Table 8: VD-S metric")
    print(table8.to_string(index=False))
    table8.to_csv('table8_vds_corrected.csv', index=False)
