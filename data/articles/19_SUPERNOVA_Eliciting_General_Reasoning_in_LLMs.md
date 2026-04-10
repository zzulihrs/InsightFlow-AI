# SUPERNOVA: Eliciting General Reasoning in LLMs with Reinforcement Learning on Natural Instructions

## Metadata

- **Source:** arXiv
- **Date:** 2026-04-09
- **arXiv ID:** 2604.08477
- **URL:** https://arxiv.org/abs/2604.08477
- **DOI:** https://doi.org/10.48550/arXiv.2604.08477
- **Subjects:** Artificial Intelligence (cs.AI); Machine Learning (cs.LG)
- **Comments:** 23 Pages, 4 figures
- **Code/Data:** https://github.com/asuvarna31/supernova
- **License:** arXiv.org perpetual, non-exclusive license (arXiv:2604.08477)

## Authors

- Ashima Suvarna
- Kendrick Phan
- Mehrab Beikzadeh
- Hritik Bansal
- Saadia Gabriel

## Abstract

Reinforcement Learning with Verifiable Rewards (RLVR) has significantly improved large language model (LLM) reasoning in formal domains such as mathematics and code. Despite these advancements, LLMs still struggle with general reasoning tasks requiring capabilities such as causal inference and temporal understanding. Extending RLVR to general reasoning is fundamentally constrained by the lack of high-quality, verifiable training data that spans diverse reasoning skills. To address this challenge, we propose SUPERNOVA, a data curation framework for RLVR aimed at enhancing general reasoning. Our key insight is that instruction-tuning datasets containing expert-annotated ground-truth encode rich reasoning patterns that can be systematically adapted for RLVR. To study this, we conduct 100+ controlled RL experiments to analyze how data design choices impact downstream reasoning performance. In particular, we investigate three key factors: (i) source task selection, (ii) task mixing strategies, and (iii) synthetic interventions for improving data quality. Our analysis reveals that source task selection is non-trivial and has a significant impact on downstream reasoning performance. Moreover, selecting tasks based on their performance for individual target tasks outperforms strategies based on overall average performance. Finally, models trained on SUPERNOVA outperform strong baselines (e.g., Qwen3.5) on challenging reasoning benchmarks including BBEH, Zebralogic, and MMLU-Pro.

## Key Contributions

- **SUPERNOVA Framework:** A data curation framework that systematically adapts instruction-tuning datasets for Reinforcement Learning with Verifiable Rewards (RLVR), enabling extension of RL-based training to general reasoning tasks beyond mathematics and code.

- **Comprehensive Empirical Study:** Over 100 controlled RL experiments analyzing how data design choices -- including source task selection, task mixing strategies, and synthetic interventions -- impact downstream reasoning performance.

- **Source Task Selection Insights:** Demonstrates that source task selection is non-trivial and has significant impact on reasoning performance. Task-specific selection outperforms strategies based on overall average performance.

- **Strong Benchmark Results:** Models trained with SUPERNOVA achieve improvements up to 52.8% on the BBEH benchmark relative to baselines such as Qwen3.5, with additional gains on Zebralogic and MMLU-Pro benchmarks.
