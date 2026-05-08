# Extending FF3 to FF4 in China A-Shares (1992-2025)

## 1. Research Motivation

The standard Fama-French three-factor model (`MKT_RF`, `SMB`, `HML`) has strong explanatory value in many settings, but it may omit medium-term momentum effects. In the China A-share market, this omission is especially important because return dynamics are shaped by regime shifts, changing market participation, and periods of strong trend behavior. This essay treats momentum as a formal extension to FF3 and evaluates whether adding `UMD` (Up Minus Down) materially improves model performance.

The core question is:

> Does a Carhart-style FF4 specification provide economically and statistically meaningful improvement over FF3 for China A-shares?

## 2. Assumptions and Empirical Setup

The extension uses the same baseline design as the project’s FF3 pipeline and changes only what is necessary to introduce momentum. The sample runs from July 1992 to December 2025 and focuses on the A-share universe. Returns are monthly and treated as decimals. Statistical inference uses Newey-West adjustments with 12 lags.

Momentum is built with a one-month skip to reduce short-term reversal contamination. Candidate momentum strategies vary by formation horizon (`J`) and holding horizon (`K`). Stocks are sorted into winner and loser deciles each formation month.

Portfolio weighting follows value-weight logic with a strict implementation rule: market-equity weights are fixed at formation month and then carried within each cohort. For `K > 1`, monthly returns are computed using overlapping active cohorts. This preserves Carhart-style timing discipline and avoids look-ahead bias.

Drawdown is measured on a compounded wealth path and bounded between -100% and 0%, ensuring mathematically valid risk reporting.

## 3. Methodological Approach

The analysis proceeds in four stages. First, a momentum strategy grid is tested across multiple `(J, K)` combinations. For each candidate strategy, winner and loser decile portfolios are formed monthly, and `UMD` is computed as winner minus loser. Each strategy is then summarized by mean return, volatility, Sharpe ratio, Newey-West t-statistic, hit rate (positive months), and maximum drawdown.

Second, an operational strategy is selected using the optimization evidence and ranking logic. Third, the selected `UMD` series is merged with the existing FF3 factors to build a monthly FF4 factor panel. Fourth, FF3 and FF4 are compared head-to-head on the same 25 size-BM test portfolios via time-series regressions, with emphasis on alpha behavior and goodness-of-fit.

This design allows a direct extension test: same test assets, same inference framework, one added factor.

## 4. Results

The momentum optimization results show that medium-term momentum exists economically in the China sample, though statistical strength is moderate rather than overwhelming. In the selected strategy (`9/6`), mean `UMD` is **0.559% per month** with a Newey-West t-stat of **1.759** and Sharpe of **0.077**. The winner and loser legs average **1.440%** and **0.881%** per month, respectively, yielding a stable positive spread. Other top candidates are close: `12/1` (mean `0.760%`, t=`1.713`) and `6/6` (mean `0.458%`, t=`1.591`).

Factor-level evidence suggests `UMD` is not a simple duplicate of existing FF3 factors. In the FF4 summary table, `UMD` has mean **0.559%**, standard deviation **7.230%**, t-stat **1.759**, and positive-month frequency **53.98%**. Correlations indicate low overlap with market and value factors (`corr(UMD, MKT_RF)=0.020`, `corr(UMD, HML)=0.004`), while interaction with size is moderate and negative (`corr(UMD, SMB)=-0.258`). This pattern supports incremental information rather than near-collinearity.

At the portfolio-pricing level, FF4 improves fit at the margin. Relative to FF3, mean `R^2` rises from **0.8973** to **0.9007** (`+0.0033`), and alpha RMSE falls from **0.2901%** to **0.2827%** (`-0.0074%`). However, improvements are not universal across every diagnostic: mean absolute alpha increases slightly from **0.2115%** to **0.2132%**, and significant-alpha counts at 5% remain unchanged (**4** portfolios under both FF3 and FF4). At the 1% level, significant alphas increase from **2** to **3**, indicating that FF4 does not uniformly reduce all mispricing signals.

## 5. Interpretation and Main Findings

Three findings follow from the evidence. First, adding momentum is empirically justified: `UMD` is economically positive (**0.559%/month**) and statistically non-zero in direction (t=`1.759`), with low correlation to `MKT_RF` and `HML`. Second, the gain is incremental, not transformational: FF4 improves model fit in aggregate (`R^2` and RMSE), but does not dominate FF3 on every metric (MAE and significant-alpha counts are mixed). Third, the broader project pattern remains unchanged: the strongest and most robust factor remains `SMB` (mean **0.860%**, t=`3.121`), while `HML` remains weaker (mean **0.417%**, t=`1.644`).

Therefore, the best interpretation is not that FF3 fails and FF4 solves everything, but that FF4 is a meaningful improvement within a still-incomplete factor description of China A-share returns.

## 6. Table-by-Table Guide for Writing

If this essay is used in a report or thesis, each table should play a specific role in the argument:

### 6.1 Momentum Construction and Selection

**`table_momentum_optimization.csv`** (also Table 1 in `academic_tables_momentum.md`) should be used to justify strategy choice. It shows which `(J, K)` designs deliver stronger economic spread and better risk-adjusted performance.

**`momentum_selection_rationale.md`** should be cited to document why one strategy was selected and how implementation details (skip month, overlapping, weighting) were fixed.

### 6.2 Factor Properties After Extension

**`table_1_factor_summary_with_momentum.csv`** (Table 2 Panel A) shows whether `UMD` is economically meaningful relative to FF3 factors.

**`table_2_factor_correlation_with_momentum.csv`** (Table 2 Panel B) shows whether `UMD` adds distinct information or is largely redundant.

### 6.3 Core FF3 vs FF4 Pricing Test

**`table_4_25port_ff4_regressions.csv`** (or equivalent `table_25port_ff4_regressions.csv`, displayed as Table 3) is the main model-test table. It compares FF3 and FF4 alpha behavior portfolio by portfolio and reports `UMD` loadings plus `R^2` changes.

**`table_5_alpha_diagnostics_comparison.csv`** (or `table_alpha_comparison.csv`, displayed as Table 4) provides the clean summary verdict through MAE/RMSE alpha and significance counts.

### 6.4 Supporting Robustness Context

**`momentum_subperiod_analysis.csv`** provides regime context (for example pre/post structural changes) and helps interpret whether the momentum signal is stable over time.

### 6.5 Consolidated Presentation

**`academic_tables_momentum.md`** is the publication-style integrated table file and should be the primary appendix/table reference in writing. The CSV files are the auditable numeric backbone.

## 7. Limitations

The evidence should be interpreted with several limitations in mind. Momentum strength is sample-dependent and can vary by regime. FF4 is still a reduced-form linear model and may omit other relevant dimensions (profitability, investment, turnover, policy exposure, or sentiment). Finally, while implementation corrections now produce economically plausible magnitudes, any factor strategy remains sensitive to portfolio construction choices.

## 8. Conclusion

As an extension of FF3, the FF4 model is empirically defensible and directionally useful in China A-shares over 1992-2025. Momentum contributes incremental explanatory content and modestly improves fit, but it does not eliminate all residual pricing errors. The most balanced conclusion is that FF4 is an improvement over FF3, yet still part of an evolving modeling framework rather than a final complete solution.
