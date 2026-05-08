# Extending the Fama-French Three-Factor Model with Momentum in China A-Shares (1992-2025)

## Introduction

This study extends the existing Fama-French three-factor (FF3) framework for China A-shares by adding a momentum factor, following the Carhart-style four-factor (FF4) logic. The motivation is straightforward: if medium-term momentum is a priced source of risk or mispricing in China, then adding `UMD` (Up Minus Down) should improve the model's ability to explain returns on the standard 25 size-book-to-market test portfolios.

The extension is implemented as an empirical add-on to the existing FF3 pipeline, not as a replacement. In other words, the central question is whether momentum meaningfully improves explanatory power beyond `MKT_RF`, `SMB`, and `HML`.

## Assumptions and Design Choices

The analysis keeps the same baseline market structure and sample frame used in the project's FF3 implementation. The return sample runs from July 1992 through December 2025 and remains focused on the A-share universe. Monthly returns are treated as decimal returns, and inference is based on Newey-West adjusted statistics with 12 lags.

Momentum formation uses a one-month skip convention to reduce short-term reversal contamination. Candidate strategies span multiple formation and holding horizons (`J` and `K`) and are evaluated in a grid. Stocks are ranked by formation-month momentum score and split into winner and loser deciles.

The weighting choice is value-weighting, but with an important implementation detail: weights are fixed at formation-month market equity for each cohort. This is critical for Carhart-style interpretation. For holding horizons longer than one month, overlapping cohorts are used, and each month's momentum return is the average of active cohort returns.

Drawdown is reported using a compounded wealth-path definition and bounded between -100% and 0%, preventing invalid values below -100%.

## Methodology

The procedure begins by testing a family of momentum strategies across different `(J, K)` combinations. For each strategy, monthly winner and loser portfolio returns are constructed, and `UMD` is computed as winner minus loser. Strategy performance is summarized by mean return, volatility, Sharpe ratio, Newey-West t-statistic, positive-month frequency, and drawdown. A composite ranking is then used to select an operational strategy for the final factor construction.

After strategy selection, the chosen monthly `UMD` series is merged with the existing FF3 factors. This produces a monthly FF4 factor panel containing `MKT_RF`, `SMB`, `HML`, and `UMD`. The model comparison step then estimates time-series regressions on the same 25 size-BM test portfolios under both FF3 and FF4 specifications. The comparison focuses on alpha diagnostics, loading significance, and fit metrics such as `R^2`.

## Results

The momentum optimization output indicates that medium-term momentum is present in China A-shares but not overwhelmingly strong in a strict statistical sense. In the current corrected run, top strategies produce economically meaningful positive monthly `UMD` premia, but t-statistics are generally moderate rather than decisive.

In the final selected specification, the momentum factor contributes additional structure without fully dominating existing factors. Correlation patterns suggest that `UMD` is not redundant with `MKT_RF` and `HML`, though some interaction with `SMB` remains. This supports treating momentum as an incremental, not duplicate, factor dimension.

When moving from FF3 to FF4 on the 25 test portfolios, the evidence is mixed but directionally favorable. Fit quality improves modestly in aggregate (for example, small improvements in average `R^2` and lower RMSE of alpha). However, improvements are not universal across all diagnostics, and the number of statistically significant alphas does not collapse to zero. The extension therefore improves pricing performance at the margin rather than producing a full model-resolution event.

## Findings and Interpretation

The main finding is that adding momentum to FF3 is useful in the China A-share context, but the gain is incremental. Momentum appears to be economically relevant, yet its statistical strength is not consistently strong enough to claim that FF4 fully solves the residual pricing errors left by FF3.

This leads to a balanced interpretation. First, FF4 is a justified extension and should be preferred when the objective is to modestly improve empirical fit. Second, the remaining alpha structure implies that additional dimensions beyond FF4 may still matter in modern China data. Third, the broader project pattern remains intact: size-related effects are still the most robust and persistent among the classic factors, while value remains comparatively fragile.

## Conclusion

Treating FF4 as an extension of FF3 is empirically defensible in this dataset. The momentum factor adds explanatory content and improves some model diagnostics, but the improvement is moderate rather than transformative. The evidence supports momentum as a meaningful supplementary factor in China A-shares, while also indicating that a complete return-pricing description likely requires further factor development beyond the classic four-factor set.
