# Comparison with Original Papers

This document systematically compares our China replication to the original academic papers, highlighting methodological deviations and institutional differences.

---

## 1. Fama-French 1992

### Study Context

| **Original Paper** | **Our Replication** |
|---|---|
| **Title** | "The Cross-Section of Expected Stock Returns" (Journal of Finance, 1992) |
| **Title** | "Cross-Sectional Asset Pricing: China A-Shares (1992–2025)" |
| **Sample Period** | U.S. market, 1926–1989 (64 years) | China A-shares, 1992–2025 (34 years) |
| **Primary Goal** | Test if CAPM's single beta explains returns; isolate size and book-to-market effects | Replicate FF1992 methodology on Chinese market; test if size and value effects exist |

### Data & Universe

| **Original Paper** | **Our Replication** |
|---|---|
| **Stock Universe** | NYSE-listed stocks, all large U.S. firms | SSE/SZSE A-shares (Markettype ∈ {1, 4}); includes small caps |
| **Sample Size** | ~1,500–2,000 firms per year | ~1,000–3,500 firms per year (growing over time) |
| **Market Liquidity** | Mature, deep markets with institutional trading | Thin trading 1992–1999; massive growth post-2000 |
| **Information Environment** | Efficient financial press, analyst coverage, SEC disclosure | Limited transparency 1992–2005; improved post-2005 |
| **Market Structure** | Stable regulatory environment throughout | Non-tradable shares (1992–2005) → split-share reform (2005–2007) → modern market (2010+) |

### Methodology

| **Original Paper** | **Our Replication** |
|---|---|
| **Beta Window** | 60-month rolling window on historical data | 60-month rolling window (but noisier in thin-trading 1990s) |
| **Beta Minimum Obs.** | 24 months | 24 months |
| **Sorting Methodology** | Annual sorts (June rebalancing) into deciles | Annual sorts (June rebalancing) into deciles |
| **Sort Dimensions** | Independent 10×10 sorts: size vs. beta, size vs. BM | Same: 10×10 size-beta, 10×10 size-BM |
| **Cross-Sectional Test** | Fama-MacBeth regressions on monthly returns | Fama-MacBeth regressions on monthly excess returns |
| **Factors Tested** | β (CAPM beta), ln(ME) (size), ln(BE/ME) (book-to-market) | Same three factors |
| **Significance Test** | t-statistics (assumes independence) | Newey-West (lag=12) corrected t-statistics |
| **Key Output** | Average slope (lambda) and t-stat across 7 model specifications | Same: 7 model specifications, NW-adjusted inference |

### Results Interpretation

| **Original Paper** | **Our Replication** |
|---|---|
| **Beta significance** | Weak/insignificant after controlling for size and BM | Weak/insignificant after controlling for size and BM (similar to original) |
| **Size effect** | Significant negative premium (~0.3% per decile) | Present but weaker than original; t-stats lower |
| **Value (BM) effect** | Significant positive premium (~0.5% per decile) | Present but inconsistent across sub-periods; weak overall |
| **Market price of risk** | Estimated risk premia are stable across time | Risk premia are time-varying; especially unstable 1992–1999 |

### Key Deviations

| **Original Paper** | **Our Replication** |
|---|---|
| **Institutional context** | U.S. established market with mature regulations | Chinese market with state ownership, regulatory intervention, SOE bias |
| **Thin trading impact** | Mature market, daily trading common | Sparse trading 1992–1999; potential price staleness and measurement error |
| **Omitted factors** | Assumes 3 factors sufficient | China-specific factors (state ownership, policy access, regulatory constraints) not captured |
| **Structural breaks** | Stable market structure across 1926–1989 | Multiple structural breaks: split-share reform (2005–2007), margin trading (March 2010) |

---

## 2. Fama-French 1993

### Study Context

| **Original Paper** | **Our Replication** |
|---|---|
| **Title** | "Common Risk Factors in the Returns of Stocks and Bonds" (Journal of Financial Economics, 1993) | "Three-Factor Model on China A-Shares (1992–2025)" |
| **Sample Period** | U.S. market, 1963–1991 (29 years) | China A-shares, 1992–2025 (34 years) |
| **Primary Goal** | Construct SMB (small-minus-big) and HML (high-minus-low BM) zero-investment portfolios; test if 3-factor model explains returns better than CAPM | Replicate FF1993 factor construction and time-series regression framework on Chinese market |

### Factor Construction

| **Original Paper** | **Our Replication** |
|---|---|
| **Sort Frequency** | Annual, each June | Annual, each June |
| **Size Breakpoint** | NYSE median market equity | Full-universe (SSE/SZSE) median market equity for 2×3 sort; SSE-only median for 5×5 test portfolios |
| **Value Breakpoint** | 30th and 70th percentile NYSE BE/ME | 30th and 70th percentile full-universe BE/ME (2×3); percentile-based for 5×5 |
| **Sort Independence** | Independent 2×3 size-value sort (6 leg portfolios) | Same: independent 2×3 (6 legs), SSE breakpoints for 5×5 test portfolios |
| **Portfolio Weighting** | Value-weighted | Value-weighted (lagged market equity) |
| **Factor Definition** | SMB = avg(3 small legs) − avg(3 big legs); HML = avg(2 high-BM legs) − avg(2 low-BM legs) | Same formula |
| **Monthly Returns** | Value-weighted returns on each portfolio | Value-weighted returns on each portfolio |

### Testing Methodology

| **Original Paper** | **Our Replication** |
|---|---|
| **Test Portfolios** | 25 portfolios (5×5 size-BM sorts) on NYSE | 25 portfolios (5×5 size-BM sorts) on SSE/SZSE |
| **Time-Series Regression** | Monthly regressions: r_i = α + β_mkt·MKT_RF + β_smb·SMB + β_hml·HML + ε_i | Same specification |
| **Beta Estimation** | Full-sample OLS on entire 1963–1991 period | Full-sample OLS on entire 1992–2025 period |
| **Inference** | t-statistics and R-squared | Newey-West (lag=12) t-statistics and R-squared |
| **Key Output Tables** | Table 1: factor summary stats; Table 5: 25-portfolio returns; Table 6: factor loadings (β_mkt, β_smb, β_hml); Table 9: CAPM vs. 3-factor alphas | Same table structure and interpretation |

### Results Interpretation

| **Original Paper** | **Our Replication** |
|---|---|
| **Size effect (SMB)** | Significant premium (~0.2–0.3% per month) | Present but varies by period; weak and unstable 1992–1999; stronger post-2000 |
| **Value effect (HML)** | Significant premium (~0.4–0.5% per month) | Weak overall; not statistically robust; suggests value mispricing is limited in China |
| **3-factor model fit** | Substantially reduces CAPM alphas; R² typically 0.75–0.95 | Similar mechanical fit (R² ~0.84–0.96) but less economic significance due to weak HML |
| **CAPM fails** | Size and value effects unexplained by CAPM | Same pattern in China; 3-factor model a partial improvement |

### Key Deviations

| **Original Paper** | **Our Replication** |
|---|---|
| **Institutional context** | U.S. established market; investors respond to risk factors uniformly | Chinese market with state ownership, policy intervention, heterogeneous investor sophistication |
| **Breakpoint choice** | NYSE-specific (survivorship bias, large-cap bias in exchange) | Adapted to SSE/SZSE universe; SSE-only for test portfolios to match market structure |
| **Full-sample OLS** | 29 years of data; reasonable stationarity assumption | 34 years with multiple structural breaks (split-share reform, margin trading launch); assumes constant factor loadings despite regime changes |
| **Value premium weakness** | Original documents strong HML; we find weak HML | Suggests either: (a) value mispricing is genuinely limited in China, or (b) institutional constraints prevent value arbitrage |
| **Time-varying betas** | Full-sample OLS assumes constant; original acknowledged this limitation | Same limitation; Chinese market dynamics especially unstable 1992–2010, making full-sample assumption problematic |

---

## 3. Daniel-Titman 1997

### Study Context

| **Original Paper** | **Our Replication** |
|---|---|
| **Title** | "Evidence on the Characteristics vs. Loadings Debate" (Journal of Finance, 1997) | "Characteristic vs. Risk-Loading Tests on China A-Shares (1992–2025)" |
| **Sample Period** | U.S. market, 1963–1994 (32 years) | China A-shares, 1992–2025 (34 years) |
| **Primary Goal** | Test whether average returns are driven by firm characteristics (e.g., size, BM) or by factor loadings (FF3 betas); resolve "characteristics debate" | Replicate DT1997 framework on Chinese market; test if returns driven by characteristics or loadings |

### Data & Matching

| **Original Paper** | **Our Replication** |
|---|---|
| **Stock Universe** | NYSE/AMEX, 1,000s of firms | SSE/SZSE A-shares, 1,000–3,500 firms per year |
| **Sample Density** | Dense; multiple firms in each characteristic-loading bin | Sparse 1992–1999; denser post-2000; matching often fails in thin periods |
| **Matching Procedure** | Match firms on characteristics (size, BM, beta) at June formation; re-rank each July by characteristics or loadings | Same procedure; but fewer matches available in early periods |
| **Matching Failure Rate** | ~10–15% | ~20–40% in 1990s; ~5–10% post-2010 (data quality varies) |

### Methodology

| **Original Paper** | **Our Replication** |
|---|---|
| **Formation Period Beta** | 36-month rolling window ending May of formation year | 36-month rolling window ending May (same as original) |
| **Beta Minimum Obs.** | 24 months | 24 months |
| **Sort 1: By Characteristics** | Quintile sort on: size, BE/ME, post-ranking beta | Same three characteristics |
| **Sort 2: By Factor Loadings** | Match each firm in Characteristic quintile to a firm with similar FF3 loadings (β_mkt, β_smb, β_hml) | Same matching logic |
| **Return Measurement** | Hold July-to-June; measure equal-weighted and value-weighted returns | Same holding period; value-weighted focus |
| **Spread Inference** | Return spread (high characteristic − low characteristic) vs. (high loading − low loading) tested for significance | Newey-West (lag=12) t-statistics; original used simple t-stats |
| **Hypothesis** | If characteristics drive returns, characteristic-sort spread should be positive; if loadings drive returns, loading-sort spread should be positive | Same hypothesis testing |

### Results Interpretation

| **Original Paper** | **Our Replication** |
|---|---|
| **Main finding** | Characteristics > Loadings; evidence that firm characteristics, not factor loadings, drive average returns | Evidence mixed; some characteristics significant, others weak; fewer matches reduce power |
| **Size effect** | Characteristic-sort spread positive and significant | Positive but weaker than original; especially unreliable 1992–1999 |
| **Value effect (BE/ME)** | Characteristic-sort spread positive and significant | Weak overall; not robust across sub-periods |
| **Beta characteristic** | Loading-sort spread near zero (contradicts CAPM) | Similar: post-ranking beta does not predict returns |

### Key Deviations

| **Original Paper** | **Our Replication** |
|---|---|
| **Sample density** | Dense U.S. market allows precise matching | Sparse Chinese market, especially 1990s; many quintiles have <5 firms; matching is noisier |
| **Beta estimation window** | 36-month window adequate for U.S. data | 36-month window noisier in Chinese thin-trading environment; potential attenuation bias |
| **Matching algorithm** | Original used discrete quintile matching | Same approach; but fewer matches available; many "mismatches" in thin periods |
| **Information environment** | U.S. market: betas and characteristics relatively stable across investors | China: high heterogeneity in information and interpretation; some investors may not track betas |
| **Institutional constraints** | U.S.: arbitrage is relatively free | China: arbitrage constrained by margin trading limits (pre-2010), regulatory intervention, capital controls |
| **Significance testing** | Original t-stats (assumes independence) | Newey-West (lag=12) t-stats; more conservative due to autocorrelation in returns |

---

## 4. Summary: Key Deviations and Interpretation

### All Three Papers

| **Dimension** | **Original Papers (U.S.)** | **Our Replication (China)** | **Interpretation** |
|---|---|---|---|
| **Market Maturity** | Established markets with 50+ years history | Young market (1992–); structural breaks 2005, 2010 | Risk premiums likely unstable; early-period results unreliable |
| **Institutional Context** | Profit-maximizing firms, efficient capital markets | SOEs, state intervention, policy-driven events | Factor pricing may differ fundamentally |
| **Thin Trading** | Modern era: daily liquidity | 1990s: sparse trading; post-2000: improved | Price staleness and measurement error inflate betas, alphas |
| **Information Efficiency** | Mature financial press and disclosure | Limited transparency 1992–2005 | Returns may reflect information diffusion, not risk premiums |
| **Regulatory Environment** | Stable SEC rules across 60+ years | Multiple regime changes (non-tradable shares, split-share reform, margin trading) | Time-varying risk models more appropriate than full-sample OLS |
| **Omitted Factors** | 3 factors assumed sufficient | China-specific factors (state ownership, policy access) not captured | Size and value premiums in China may be partly mispricing, partly risk |

### Specific to Each Paper

| **FF1992** | Risk premiums are time-varying in China; size and value weak | Early period unreliable; use post-2000 for inference |
| **FF1993** | HML weak suggests either limited value anomaly or institutional constraints in China | Compare pre- vs. post-2010 to isolate margin-trading effect |
| **DT1997** | Sparse matching in 1990s; weak power to distinguish characteristics vs. loadings | Focus on post-2000 results; acknowledge 1990s uncertainty |

---

## 5. Recommendations for Users

- **For forward-looking inference**: Use post-2010 results (most reliable; modern market structure stable)
- **For descriptive historical analysis**: Use full 1992–2025, but acknowledge 1992–1999 is exploratory only
- **For comparison to originals**: Acknowledge institutional differences; do **not** directly generalize U.S. risk premiums to China
- **For factor construction**: 5×5 test portfolios use SSE-breakpoints (preferred); 2×3 factor sort uses full-universe breakpoints (standard FF1993)
