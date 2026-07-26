# TempoVul

**A Temporal Benchmark Study of LLM-Assisted Vulnerability Detection Across the Secure SDLC**

Samson Quaye, Ahmed Ben Ayed, Maurice Dawson, Marwan Omar
Center for Cybersecurity and Forensic Education (C2SAFE), Illinois Institute of Technology · School of Engineering & Technology, National University

## Overview

Existing vulnerability detection benchmarks evaluate LLMs and static analysis tools almost exclusively at the implementation stage. TempoVul is the first benchmark to evaluate both across **all four stages of the secure SDLC** — Requirements, Design, Implementation, and Testing — on 400 samples spanning 15 CWE categories drawn from the Juliet Test Suite, Devign, and Big-Vul.

Framing detection as a time-to-event problem, we apply Kaplan-Meier survival analysis, log-rank tests, and McNemar's test to five open-source LLMs (CodeLlama-7B, StarCoder2-7B, DeepSeek-Coder-7B, Mistral-7B-Instruct, WizardCoder-15B) and five static analysis tools (Semgrep, Flawfinder, cppcheck, Infer, CodeQL).

**Key findings:**
- Four of five LLMs reach median detection at the requirements stage, while static analysis tools remain structurally blind before implementation — a significant temporal advantage (log-rank *p* < 0.001) that holds even when both method families are restricted to the stages where static tools can operate.
- Classification accuracy shows no consistent LLM advantage over static analysis: the top model by F1 does not significantly outperform the strongest static baseline after multiple-comparison correction, though DeepSeek-Coder does.
- Detection capability varies significantly by CWE category, driven primarily, though not exclusively, by real-world versus synthetic sample origin.
- Instruction-following reliability is a measurable confound independent of code-understanding capability: parseable output rates ranged from 99.8% (Mistral-Instruct) to 16.9% (StarCoder2, a base rather than instruction-tuned model).

## Repository Structure

```
TempoVul/
├── data/
│   ├── tempovul_v2.csv                     # 400 samples x 4 stage-specific artifacts (corrected)
│   ├── llm_predictions/
│   │   └── llm_master_v2.csv               # all 5 models x all 4 stages, 1,600 rows
│   └── static_tool_outputs/
│       └── static_master.csv               # all 5 tools, Stage 3
├── results/                                # reproduces every table in the paper
│   ├── table6_llm_classification_corrected.csv
│   ├── table7_static_classification_corrected.csv
│   ├── table8_vds_corrected.csv
│   ├── table10_median_ttd_edr_corrected.csv
│   ├── table11_logrank_best_llm_vs_static_corrected.csv
│   ├── table12_best_f1_per_category_corrected.csv
│   ├── table13_category_significance_summary_corrected.csv
│   ├── appendixA_logrank_pairwise_llms_corrected.csv
│   ├── appendixB_mcnemar_stage3_all_methods_verified.csv
│   └── appendixC_category_vs_rest_logrank_corrected.csv
├── figures/                                # figures used in the paper
│   ├── FIG2-HEATMAP.png                    # F1 score heatmap, LLMs x SDLC stages
│   ├── FIG3-BARCHAT.png                    # F1 score comparison, grouped by stage
│   ├── FIG4-STATIC.png                     # static tool detection rate
│   ├── FIG5-KMCURVE.png                    # Kaplan-Meier survival curves
│   ├── FIG6-MEDIANDHEATMAP.png             # median detection stage by CWE category
│   └── EDR-Values-ForLLMS.png              # early detection rate by LLM
├── notebooks/                              # evaluation pipeline notebooks
└── src/utils/                              # dataset construction and evaluation scripts
```

## Quickstart

```python
import pandas as pd

df = pd.read_csv("data/tempovul_v2.csv")
# columns: id, label, category, cwe, source_dataset,
#          stage1_requirements, stage2_design, stage3_implementation, stage4_testing

llm_results = pd.read_csv("data/llm_predictions/llm_master_v2.csv")
# 1,600 rows: 400 samples x 4 stages, with one prediction column per model

static_results = pd.read_csv("data/static_tool_outputs/static_master.csv")
# 400 samples x Stage 3, with one prediction column per tool
```

## A note on data provenance

`tempovul_v2.csv` and `llm_master_v2.csv` are corrected versions of the dataset and LLM evaluation outputs used to produce this paper's final results. During validation, we identified and fixed an artifact-generation defect affecting the Stage 4 (Testing) evaluation: the intended static analysis findings were not correctly incorporated into a subset of stage artifacts prior to LLM evaluation. This was corrected and the affected evaluations were re-run in full prior to publication. See the paper's Discussion (Section 5.3) for details on the correction and its effect on reported results.

## Citation

```bibtex
@article{quaye2026tempovul,
  title   = {A Temporal Benchmark Study of LLM-Assisted Vulnerability Detection Across the Secure SDLC},
  author  = {Quaye, Samson and Ben Ayed, Ahmed and Dawson, Maurice and Omar, Marwan},
  journal = {Preprint submitted to Elsevier},
  year    = {2026}
}
```

See [CITATION.cff](CITATION.cff) for the machine-readable version.

## License

Code: see [LICENSE](LICENSE) (MIT). Dataset: `tempovul_v2.csv` draws source code from the Juliet Test Suite (NIST, public domain), Devign (FFmpeg, QEMU, OpenSSL, Linux kernel), and Big-Vul (348 GitHub projects, mixed licenses). Underlying code retains its original project license; TempoVul's own additions (stage artifacts, labels, prompts) are released under MIT alongside the code.

## Contact

Samson Quaye - squaye@hawk.illinoistech.edu
