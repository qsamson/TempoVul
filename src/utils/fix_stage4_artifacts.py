#!/usr/bin/env python3
"""
Builds the Stage 4 (Testing) artifact by combining each sample's Stage 3
source code with a per-tool static analysis findings summary.

Findings are placed before the code so they survive downstream model
context truncation regardless of code length. See paper Section 3.4 for
the artifact design.

Reads:
  - tempovul_with_artifacts_final.csv
  - static_analysis_results/{tool}_complete.csv  (Stage 3 findings, 5 tools)

Writes:
  - tempovul_with_artifacts_v2.csv  (stage4_testing rebuilt, all other
                                      columns preserved as-is)

Usage:
  python fix_stage4_artifacts.py
"""

import pandas as pd

TOOLS = ['flawfinder', 'cppcheck', 'semgrep', 'infer', 'codeql']


def build_findings_summary(idx, tool_dfs):
    """Format one sample's per-tool static analysis findings as text."""
    lines = []
    any_findings = False
    for tool in TOOLS:
        t = tool_dfs[tool]
        if idx not in t.index:
            lines.append(f"- {tool}: [no result available]")
            continue
        row = t.loc[idx]
        pred = row[f'{tool}_pred']
        cwe = row[f'{tool}_cwe']
        n = row[f'{tool}_findings']
        if pred == 1:
            any_findings = True
            cwe_display = cwe if pd.notna(cwe) else 'unspecified CWE'
            lines.append(f"- {tool}: {int(n)} finding(s), suspected {cwe_display}")
        else:
            lines.append(f"- {tool}: no findings")
    header = ("STATIC ANALYSIS FINDINGS:" if any_findings
              else "STATIC ANALYSIS FINDINGS (no tool flagged this sample):")
    return header + "\n" + "\n".join(lines)


def main():
    df = pd.read_csv('tempovul_with_artifacts_final.csv')
    assert len(df) == 400, f"Expected 400 rows, got {len(df)}"

    tool_dfs = {}
    for tool in TOOLS:
        t = pd.read_csv(f'static_analysis_results/{tool}_complete.csv')
        tool_dfs[tool] = t.set_index('sample_id')

    new_stage4 = []
    for idx, row in df.iterrows():
        findings = build_findings_summary(idx, tool_dfs)
        code = row['stage3_implementation']
        combined = f"{findings}\n\n--- SOURCE CODE ---\n{code}"
        new_stage4.append(combined)

    df['stage4_testing'] = new_stage4

    leftover = df['stage4_testing'].str.contains(
        r'\[Static analysis placeholder\]', regex=True
    ).sum()
    assert leftover == 0, f"Placeholder text still present in {leftover} rows"

    out_path = 'tempovul_with_artifacts_v2.csv'
    df.to_csv(out_path, index=False)

    print(f"Saved corrected artifacts to {out_path}")
    print(f"Placeholder text remaining: {leftover} (expected 0)")

    n_over_2000 = (df['stage4_testing'].str.len() > 2000).sum()
    print(
        f"Rows where full stage4_testing exceeds 2000 chars "
        f"(code truncated downstream, findings preserved): {n_over_2000}/400"
    )


if __name__ == '__main__':
    main()
