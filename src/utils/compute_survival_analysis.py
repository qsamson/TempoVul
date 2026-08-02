#!/usr/bin/env python3
"""
Survival analysis functions used throughout the paper's temporal
detection results: time-to-detection, median TTD, early detection rate,
Kaplan-Meier survival curves, and log-rank significance testing.

Reproduces Tables 10, 11, 12, and 13, and Appendices A and C.

Requires: lifelines, statsmodels

Usage as a script:
  python compute_survival_analysis.py

Or import the functions directly:
  from compute_survival_analysis import compute_ttd, pairwise_logrank
"""

import numpy as np
import pandas as pd
from itertools import combinations
from lifelines.statistics import logrank_test
from statsmodels.stats.multitest import multipletests

LLM_MODELS = ['codellama', 'starcoder2', 'deepseek', 'mistral', 'wizardcoder']
STAGES = ['stage1', 'stage2', 'stage3', 'stage4']


def compute_ttd(df, model):
    """
    Time-to-detection for one model. For each vulnerable sample, returns
    the first stage where the model correctly predicted 'vulnerable'.
    Samples never detected are censored at Stage 4 (event = 0).
    """
    vuln = df[df['ground_truth'] == 1].copy()
    times, events = [], []
    for sample_id in vuln['sample_id'].unique():
        sample_rows = df[df['sample_id'] == sample_id].sort_values('stage')
        detected_stage = None
        for _, row in sample_rows.iterrows():
            if row[f'{model}_pred'] == 1:
                detected_stage = row['stage']
                break
        if detected_stage is not None:
            times.append(detected_stage)
            events.append(1)
        else:
            times.append(4)
            events.append(0)
    return np.array(times), np.array(events)


def median_ttd_and_edr(times, events):
    """Median time-to-detection among detected samples, and early detection rate (Stage 1-2)."""
    median_stage = np.median(times[events == 1]) if events.sum() > 0 else None
    n_censored = int((events == 0).sum())
    edr = ((times <= 2) & (events == 1)).sum() / len(times)
    return median_stage, n_censored, edr


def pairwise_logrank(ttd_results, alpha=0.05):
    """Pairwise log-rank tests between all models in ttd_results, Holm and Bonferroni corrected."""
    rows = []
    for m1, m2 in combinations(ttd_results.keys(), 2):
        t1, e1 = ttd_results[m1]
        t2, e2 = ttd_results[m2]
        result = logrank_test(t1, t2, event_observed_A=e1, event_observed_B=e2)
        rows.append({'model_a': m1, 'model_b': m2,
                      'chi2': round(result.test_statistic, 3), 'p': result.p_value})

    df = pd.DataFrame(rows)
    reject_holm, p_holm, _, _ = multipletests(df['p'], alpha=alpha, method='holm')
    reject_bonf, p_bonf, _, _ = multipletests(df['p'], alpha=alpha, method='bonferroni')
    df['p_holm'], df['sig_holm'] = p_holm, reject_holm
    df['p_bonf'], df['sig_bonf'] = p_bonf, reject_bonf
    return df


def category_vs_rest_logrank(df, model, categories, alpha=0.05):
    """
    Per-category log-rank test: each category's detection time
    distribution against the pooled distribution of all other
    categories, Holm corrected within the model's family of tests.
    """
    vuln = df[df['ground_truth'] == 1]

    def ttd_for_samples(sample_ids):
        times, events = [], []
        for sid in sample_ids:
            rows = df[df['sample_id'] == sid].sort_values('stage')
            detected_stage = None
            for _, row in rows.iterrows():
                if row[f'{model}_pred'] == 1:
                    detected_stage = row['stage']
                    break
            times.append(detected_stage if detected_stage else 4)
            events.append(1 if detected_stage else 0)
        return np.array(times), np.array(events)

    p_values, meta = [], []
    for cat in categories:
        cat_ids = vuln[vuln['category'] == cat]['sample_id'].unique()
        rest_ids = vuln[vuln['category'] != cat]['sample_id'].unique()
        t_cat, e_cat = ttd_for_samples(cat_ids)
        t_rest, e_rest = ttd_for_samples(rest_ids)
        result = logrank_test(t_cat, t_rest, event_observed_A=e_cat, event_observed_B=e_rest)
        p_values.append(result.p_value)
        meta.append((cat, len(cat_ids), result.test_statistic))

    reject, p_holm, _, _ = multipletests(p_values, alpha=alpha, method='holm')
    rows = [
        {'model': model, 'category': m[0], 'n': m[1], 'chi2': round(m[2], 3),
         'p_holm': round(ph, 4), 'sig': 'Yes' if sig else 'No'}
        for m, ph, sig in zip(meta, p_holm, reject)
    ]
    return pd.DataFrame(rows)


if __name__ == '__main__':
    llm_master = pd.read_csv('llm_master_v2.csv')

    ttd_results = {m: compute_ttd(llm_master, m) for m in LLM_MODELS}

    print("Median time-to-detection and early detection rate (Table 10)")
    rows = []
    for model in LLM_MODELS:
        times, events = ttd_results[model]
        median_stage, n_censored, edr = median_ttd_and_edr(times, events)
        pct_censored = n_censored / len(events) * 100
        print(f"{model:12s} median_TTD={median_stage}  "
              f"n_censored={n_censored} ({pct_censored:.1f}%)  EDR={edr:.3f}")
        rows.append({'model': model, 'median_ttd': median_stage,
                      'n_censored': n_censored, 'pct_censored': f"{pct_censored:.1f}%",
                      'edr': round(edr, 3)})
    pd.DataFrame(rows).to_csv('table10_median_ttd_edr_corrected.csv', index=False)

    print()
    print("Pairwise log-rank, all 5 LLMs (Appendix A)")
    logrank_df = pairwise_logrank(ttd_results)
    print(logrank_df.to_string(index=False))
    logrank_df.to_csv('appendixA_logrank_pairwise_llms_corrected.csv', index=False)

    print()
    print("Category vs rest log-rank, per model (Appendix C)")
    categories = sorted(llm_master[llm_master['ground_truth'] == 1]['category'].unique())
    all_cat_rows = []
    for model in LLM_MODELS:
        cat_df = category_vs_rest_logrank(llm_master, model, categories)
        all_cat_rows.append(cat_df)
    appendix_c = pd.concat(all_cat_rows, ignore_index=True)
    print(appendix_c.to_string(index=False))
    appendix_c.to_csv('appendixC_category_vs_rest_logrank_corrected.csv', index=False)
