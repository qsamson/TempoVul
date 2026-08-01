# Data Directory

## `tempovul_v2.csv`

400 samples, one row per sample, spanning all four SDLC stage artifacts.

| Column | Type | Description |
|---|---|---|
| `id` | str | Sample identifier, format `TV-0001` through `TV-0400` |
| `label` | int | 0 for safe, 1 for vulnerable |
| `category` | str | One of 7 categories: Memory Safety Juliet, Injection, Numeric Errors, Resource Misuse, Memory Safety BigVul, Access Control, General |
| `cwe` | str | CWE identifier, for example `CWE-78`. Empty for General (Devign), which has no CWE label |
| `source_dataset` | str | `juliet`, `bigvul`, or `devign` |
| `code` | str | The full source code of the sample |
| `stage1_requirements` | str | Natural language requirements specification |
| `stage2_design` | str | Data flow, trust boundary, and I/O design description |
| `stage3_implementation` | str | Full source code, identical to `code` |
| `stage4_testing` | str | Static analysis findings summary followed by the source code. Findings are placed first so they are preserved under model context truncation regardless of code length |
| `cve_id` | str | CVE identifier, populated only for Big-Vul samples |
| `project` | str | Source project name, populated only for Big-Vul samples |
| `commit_id` | str | Source commit hash, populated only for Big-Vul samples |

Source counts: Juliet 220, Big-Vul 139, Devign 41.

## `llm_predictions/llm_master_v2.csv`

1,600 rows, 400 samples across 4 stages.

| Column | Description |
|---|---|
| `sample_id`, `stage`, `stage_name`, `ground_truth`, `category`, `cwe` | Join keys and metadata |
| `codellama_pred`, `starcoder2_pred`, `deepseek_pred`, `mistral_pred`, `wizardcoder_pred` | Binary prediction per model, 0 or 1 |

## `static_tool_outputs/static_master.csv`

400 rows, Stage 3 only. Static analysis tools operate exclusively on source code, so their predictions are stage invariant. This was confirmed directly: Flawfinder, Semgrep, Infer, and CodeQL produce identical predictions at Stage 3 and Stage 4. cppcheck's Stage 3 predictions are reported here as its canonical value, since its separate Stage 4 run encountered a parsing artifact unrelated to genuine detection capability.

| Column | Description |
|---|---|
| `sample_id`, `stage`, `ground_truth`, `category`, `cwe` | Join keys and metadata |
| `flawfinder_pred`, `cppcheck_pred`, `semgrep_pred`, `infer_pred`, `codeql_pred` | Binary prediction per tool, 0 or 1 |

## Reproducing the paper's tables

| Table or figure | Source file |
|---|---|
| Table 6, LLM classification | `../results/table6_llm_classification_corrected.csv` |
| Table 7, static tool classification | `../results/table7_static_classification_corrected.csv` |
| Table 8, VD-S | `../results/table8_vds_corrected.csv` |
| Table 10, median TTD and EDR | `../results/table10_median_ttd_edr_corrected.csv` |
| Table 11, log rank, best LLM versus best static | `../results/table11_logrank_best_llm_vs_static_corrected.csv` |
| Table 12, best F1 per category | `../results/table12_best_f1_per_category_corrected.csv` |
| Table 13, category significance summary | `../results/table13_category_significance_summary_corrected.csv` |
| Appendix A, pairwise log rank, all LLMs | `../results/appendixA_logrank_pairwise_llms_corrected.csv` |
| Appendix B, pairwise McNemar, Stage 3 | `../results/appendixB_mcnemar_stage3_all_methods_verified.csv` |
| Appendix C, category versus rest log rank | `../results/appendixC_category_vs_rest_logrank_corrected.csv` |
