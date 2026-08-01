# TempoVul

**A Temporal Benchmark Study of LLM-Assisted Vulnerability Detection Across the Secure SDLC**

Samson Quaye, Ahmed Ben Ayed, Maurice Dawson, Marwan Omar
Center for Cybersecurity and Forensic Education, Illinois Institute of Technology. School of Engineering & Technology, National University

![python](https://img.shields.io/badge/python-3.10-blue)
![license](https://img.shields.io/badge/License-MIT-yellow)
![dataset](https://img.shields.io/badge/dataset-included-brightgreen)
![models](https://img.shields.io/badge/LLMs-5%20open--source-blueviolet)
![tools](https://img.shields.io/badge/static%20tools-5-orange)
![status](https://img.shields.io/badge/status-preprint%20submitted-informational)

## Overview

Existing vulnerability detection benchmarks evaluate LLMs and static analysis tools almost exclusively at the implementation stage. TempoVul is the first benchmark to evaluate both across all four stages of the secure SDLC: Requirements, Design, Implementation, and Testing. The benchmark covers 400 samples spanning 15 CWE categories drawn from the Juliet Test Suite, Devign, and Big-Vul.

Detection is framed as a time-to-event problem. We apply Kaplan-Meier survival analysis, log-rank tests, and McNemar's test to evaluate five open-source LLMs: CodeLlama-7B, StarCoder2-7B, DeepSeek-Coder-7B, Mistral-7B-Instruct, and WizardCoder-15B. We evaluate the same five static analysis tools: Semgrep, Flawfinder, cppcheck, Infer, and CodeQL.

## Key Findings

Four of five LLMs reach median detection at the requirements stage. Static analysis tools remain structurally blind before implementation. This is a significant temporal advantage, confirmed by log-rank testing at p < 0.001, and the advantage holds even when both method families are restricted to the stages where static tools can operate.

Classification accuracy shows no consistent LLM advantage over static analysis. The top model by F1 does not significantly outperform the strongest static baseline after multiple comparison correction. DeepSeek-Coder is the exception, significantly outperforming every static baseline.

Detection capability varies significantly by CWE category. This variation is driven primarily, though not exclusively, by real world versus synthetic sample origin.

Instruction following reliability is a measurable confound, independent of code understanding capability. Parseable output rates ranged from 99.8% for Mistral-Instruct down to 16.9% for StarCoder2, a base rather than instruction tuned model.

## Repository Structure

```
TempoVul/
├── data/
│   ├── README.md                                       data schema documentation
│   ├── tempovul_v2.csv                                 400 samples, 4 stage-specific artifacts
│   ├── llm_predictions/
│   │   └── llm_master_v2.csv                           all 5 models, all 4 stages, 1,600 rows
│   └── static_tool_outputs/
│       └── static_master.csv                           all 5 tools, Stage 3
├── results/                                             reproduces every table in the paper
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
├── figures/                                             figures used in the paper
│   ├── FIG2-HEATMAP.png                                 F1 score heatmap, LLMs by SDLC stage
│   ├── FIG3-BARCHAT.png                                 F1 score comparison, grouped by stage
│   ├── FIG4-STATIC.png                                  static tool detection rate
│   ├── FIG5-KMCURVE.png                                 Kaplan-Meier survival curves
│   ├── FIG6-MEDIANDHEATMAP.png                          median detection stage by CWE category
│   └── EDR-Values-ForLLMS.png                           early detection rate by LLM
├── notebooks/
│   ├── 01_dataset_construction.ipynb                    sampling from Juliet, Devign, and Big-Vul
│   ├── 02_artifact_and_evaluation_pipeline.ipynb        stage artifact generation and LLM evaluation
│   └── 03_stage4_analysis.ipynb                         Stage 4 artifact build and full results analysis
└── src/
    └── utils/                                           evaluation and analysis scripts
```

## Quickstart

```python
import pandas as pd

df = pd.read_csv("data/tempovul_v2.csv")
# columns: id, label, category, cwe, source_dataset,
#          stage1_requirements, stage2_design, stage3_implementation, stage4_testing

llm_results = pd.read_csv("data/llm_predictions/llm_master_v2.csv")
# 1,600 rows: 400 samples across 4 stages, one prediction column per model

static_results = pd.read_csv("data/static_tool_outputs/static_master.csv")
# 400 samples at Stage 3, one prediction column per tool
```

## Related Work

This benchmark complements [IRAS-SDLC](https://doi.org/10.3390/systems14050546), a lifecycle risk aggregation framework for secure AI augmented software assurance under RMF and Zero Trust, from the same research group.

## Citation

```bibtex
@article{quaye2026tempovul,
  title   = {A Temporal Benchmark Study of LLM-Assisted Vulnerability Detection Across the Secure SDLC},
  author  = {Quaye, Samson and Ben Ayed, Ahmed and Dawson, Maurice and Omar, Marwan},
  journal = {Preprint submitted to Elsevier},
  year    = {2026}
}
```

The machine readable citation file is available at [CITATION.cff](CITATION.cff).

## License

Code is released under the [MIT License](LICENSE). `tempovul_v2.csv` draws source code from three corpora. The Juliet Test Suite is a NIST public domain resource. Devign draws from FFmpeg, QEMU, OpenSSL, and the Linux kernel. Big-Vul draws from 348 GitHub projects under mixed licenses. Underlying code retains its original project license. TempoVul's own additions, including stage artifacts, labels, and prompts, are released under MIT alongside the code.

## Contact

Samson Quaye
squaye@hawk.illinoistech.edu
