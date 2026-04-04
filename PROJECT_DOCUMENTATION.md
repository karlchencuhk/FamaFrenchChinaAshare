# China Asset Pricing Replication Project Documentation

## 1. Project Overview

This workspace documents a multi-part empirical asset pricing project on Chinese A-shares. The work completed in this project covers three related strands:

1. **Fama and French (1992) style cross-sectional tests** for the pricing of beta, size, and book-to-market.
2. **Fama and French (1993) style three-factor model construction and testing** using China A-share data.
3. **Daniel and Titman (1997) style characteristic-versus-loading tests** to distinguish whether returns are better explained by firm characteristics or by factor loadings.

The project is designed as a pure Python, script-based replication environment using raw monthly stock return data, annual balance sheet data, market return data, and a monthly risk-free rate series. The code does not depend on `pandas`, `numpy`, or `scipy`; all data processing and estimation are implemented with Python standard-library tools and custom helper functions.

The central research question throughout the project is:

> Do the classic size, value, and beta effects from the U.S. asset-pricing literature replicate in China, and if so, are they stable across time and consistent with characteristic-based or risk-loading-based explanations?

A second major theme of the project is **regime heterogeneity**, especially the difference between the early Chinese market structure and the more modern post-2010 environment.

---

## 2. Workspace Structure and Completed Analysis Folders

The main completed research folders present in the workspace are:

### Fama-French 1992 style replications
- `Fama French 1992 (1992-1999)`
- `Fama French 1992 (1992-2010M03)`
- `Fama French 1992 (1992-2025)`
- `Fama French 1992 (2000-2025)`
- `Fama French 1992 (2010M04-2025)`

### Fama-French 1993 style replications
- `Fama French 1993 (1992-1999)`
- `Fama French 1993 (1992-2010M03)`
- `Fama French 1993 (1992-2025)`
- `Fama French 1993 (2000-2025)`
- `Fama French 1993 (2010M04-2025)`

### Daniel-Titman style replications
- `Daniel and Titman 1997 JF (1992-2025)`
- `Daniel and Titman 1997 JF (2000-2025)`

The additional `1992-1999` and `Daniel and Titman 1997 JF (1992-2025)` folders are also useful as auxiliary checks and are documented below.

---

## 3. Recent Updates and Key Analyses

This section highlights the most recent work completed in the project.

### 3.1 Fama-French 1993 Alignment Project (Full Period 1992-2025)

A major recent update was a full-scale alignment of the Fama-French 1993 replication with the tables and narrative of the original 1993 paper. This was motivated by the need to have outputs that directly map to the classic academic study.

This work is contained in new subfolders within the `Full Period (1992-2025)/Fama French 1993 (1992-2025)/` directory:
- **`scripts_ff1993_aligned/`**: Contains new Python scripts dedicated to generating and formatting the aligned tables.
- **`output_ff1993_aligned/`**: Contains the final output tables in `.md`, `.tex`, and `.txt` formats, along with the intermediate CSV files.

The key output file is **`ff1993_aligned_tables.md`**, which presents a complete narrative that:
1.  **Describes the risk factors** (MKT_RF, SMB, HML) with summary statistics (an analogue to FF1993 Table 1).
2.  **Presents the "puzzle"** by showing the average excess returns for 25 portfolios sorted on size and book-to-market (an analogue to FF1993 Table 5).
3.  **Solves the puzzle** by running time-series regressions and showing that the 3-factor model largely eliminates the pricing errors (alphas) that the standard CAPM cannot explain (an analogue to FF1993 Table 9). This includes a head-to-head comparison of CAPM and 3-factor model alphas and their t-statistics.
4.  **Provides detailed diagnostics**, including factor loadings and R-squared values from the 3-factor model regressions (an analogue to FF1993 Table 6).

This aligned analysis confirms that the Fama-French 3-factor model is a significant improvement over the CAPM for explaining stock returns in the Chinese A-share market for the full 1992-2025 period.

### 3.2 Updates to Fama-French 1992 Replication (Full Period 1992-2025)

Minor but important updates were made to the Fama-MacBeth (cross-sectional) analysis for the full period.
- The main output table for the Fama-MacBeth regressions (Table IV analogue) was updated to include the average cross-sectional `ln(ME)` and `ln(BE/ME)` characteristics of the 100 test portfolios.
- The table was also updated to include the average `post-ranking beta` for each portfolio, providing a clearer picture of the relationship between beta and returns after accounting for size.

---

## 4. Raw Data Used

The analysis uses the following raw datasets.

### 4.1 Monthly stock returns and market equity
**File used:** `Monthly Stock Price  Returns121529524/TRD_Mnth_SSE_A_SZSE_A.txt`

This file provides the stock-level monthly panel used in every pipeline. Key fields used by the scripts include:
- `Stkcd`: stock code
- `Trdmnt`: trading month
- `Mretwd`: monthly return including dividends
- `Msmvttl`: total market equity / total market capitalization field
- `Markettype`: security-market classification

**How it is used:**
- Monthly stock return series for portfolio returns and cross-sectional regressions
- Monthly market equity as the size measure
- Formation-month market equity for portfolio sorting
- Previous-month market equity as portfolio weights in value-weighted returns

**Universe restriction used in the code:**
- Only `Markettype in ('1', '4')` are kept in the stock-level panel. This corresponds to the main A-share universe used in the project scripts.

### 4.2 Annual balance sheet data
**File used:** `Balance Sheet110248807/FS_Combas.csv`

This file is used to construct annual book equity.

**Fields used:**
- `Stkcd`
- `Accper`
- `Typrep`
- `A003100000` or fallback `A003000000`

**How it is used:**
- Only `Typrep == 'A'` is used, i.e. A-statement observations
- The scripts prefer annual statement dates that correspond to year-end accounting values
- In the FF1992 and D&T pipelines, year-end `-12-31` statements are explicitly targeted for book equity assignment

### 4.3 Aggregate market returns
**File used:** `Aggregated Monthly Market Returns141530201/TRD_Cnmont.csv`

**Fields used:**
- `Trdmnt`
- `Cmretwdtl`
- `Markettype`

**How it is used:**
- Only `Markettype == '5'` is used to proxy the aggregate market return relevant to the China A-share setting
- The monthly market return is combined with the monthly risk-free rate to construct `MKT_RF`

### 4.4 Monthly risk-free rate
**File used by scripts:** `Risk-Free Rate135436249/TRD_Nrrate.csv`

**Fields used:**
- `Clsdt`
- `Nrrmtdt`

**How it is used:**
- The scripts take the **latest available quote in each month**
- The monthly risk-free rate is converted from percent to decimal by dividing by 100
- Used to form stock excess returns and market excess returns

### 4.5 Additional risk-free-rate folder present in the workspace
An additional folder exists:
- `Risk_Free_Rate/IR3TIB01CNM156N.csv`

This file is present in the workspace but is **not the file referenced by the active replication scripts** examined here.

---

## 5. Common Sample Design and Core Assumptions

Across the pipelines, the following conventions are used repeatedly.

### 5.1 Return window conventions
The code uses sample-window controls through `RETURN_START` and `RETURN_END` in each folder-specific `00_config.py`.

The main windows documented in this project are:
- `1992-07` to `2025-12`
- `2000-01` to `2025-12`
- `1992-07` to `2010-03`
- `2010-04` to `2025-12`
- `1992-07` to `1999-12` in the archived early-sample folders

### 5.2 July-to-June holding convention
The project follows the standard Fama-French timing convention:
- Firm characteristics are measured at the June formation date
- Portfolio membership is then applied from **July of year `t` through June of year `t+1`**

This convention appears in both the FF1992 and FF1993 implementations and in the Daniel-Titman membership logic.

### 5.3 Book-to-market timing convention
The code uses lagged accounting information to avoid look-ahead bias.

#### In FF1992 scripts
- Book equity is assigned using a lagged year mapping based on the return month
- For formation-year characteristics, book equity from the prior accounting year is merged to June market equity

#### In FF1993 scripts
- For factor construction, the code uses book equity from year `t-1` and market equity from the previous December for BM sorts, consistent with a standard FF-style implementation

### 5.4 Size measure
Size is measured using `Msmvttl` from the stock monthly file.

**Important assumption:** this is a **total market equity** measure, not an explicitly free-float or tradable-share measure.

Implications:
- This is consistent with standard practice in many empirical replications
- It may be more problematic in early China, especially before and during the split-share reform era, because non-tradable shares distort the mapping between price and true tradable market value
- This issue is especially relevant for interpreting the value effect in the pre-reform period, but it does not overturn the project’s main conclusion that value is not a robust premium in China

### 5.5 Beta estimation windows
Two different beta windows are used depending on the project:
- **FF1992:** `BETA_WINDOW = 60`, `BETA_MIN_OBS = 24`
- **Daniel-Titman:** `BETA_WINDOW = 36`, `BETA_MIN_OBS = 24`

The shorter window in the Daniel-Titman pipeline reflects the specific need to estimate pre-formation factor loadings for the characteristic-versus-loading tests.

### 5.6 Newey-West inference
All major significance reporting uses:
- `NW_LAG = 12`

This applies to:
- Fama-MacBeth average slope t-statistics
- Mean factor premium t-statistics
- Time-series alpha inference
- Daniel-Titman portfolio spread inference

### 5.7 Weighting conventions
Where portfolios are value-weighted, the scripts generally:
- use previous-month market equity where available
- fall back to contemporaneous market equity if necessary

### 5.8 Data quality and missingness handling
The scripts are conservative and skip observations when key fields are missing.

Examples:
- No stock observation if market equity is missing or non-positive
- No BM value if book equity is missing or non-positive
- No factor or spread observation if required component portfolios are unavailable
- No beta if rolling-window minimum observations are not met

### 5.9 No heavy external dependencies
The project intentionally uses only pure Python scripts and custom matrix/statistical routines.

This means:
- all OLS, Newey-West, and sorting logic are transparent in code
- the project is portable and reproducible without a heavier scientific-Python stack
- speed and convenience are traded off for control and auditability

---

## 6. Methodology by Pipeline

## 6.1 Fama-French 1992 style replication

### Objective
Replicate the FF1992 cross-sectional logic for Chinese A-shares:
- test whether beta explains average returns
- test whether size explains average returns
- test whether book-to-market explains average returns
- test whether beta retains significance after controlling for size and BM

### Main scripts
From `Fama French 1992 (1992-2025)/scripts/`:
- `01_build_master_panel.py`
- `02_build_june_chars_and_membership.py`
- `03_make_table_ii.py`
- `04_make_table_i_size_beta_10x10.py`
- `05_make_table_v_size_beme_10x10.py`
- `05b_make_table_iv_beme_only.py`
- `06_make_table_iii_fama_macbeth.py`
- `07_run_all.py`
- `08_format_academic_tables.py`
- `09_format_latex_tables.py`

### Step-by-step method

#### Step 1: Build master panel
The script constructs a master monthly panel containing:
- stock return
- market equity
- risk-free rate
- market return
- stock excess return
- market excess return
- book equity
- `BE/ME`
- `ln(size)`
- `ln(BE/ME)`

This panel is saved as `master_panel_200001_202512.csv` in the output folder. The filename remains constant even across alternative sample windows, but the actual rows included depend on the folder-specific config and downstream sample filtering.

#### Step 2: Compute June characteristics and portfolio membership
For each formation year, the script:
- looks at June market equity
- estimates pre-ranking beta using rolling market-model beta
- merges lagged book equity
- computes `ln_size` and `ln_be_me`
- assigns deciles for size, beta, and BM
- assigns conditional deciles within size groups
- writes a July-to-June membership file for monthly use

#### Step 3: Build descriptive portfolio tables
The scripts generate:
- 10x10 size-by-beta portfolios
- univariate size and beta portfolios
- BE/ME-only portfolios
- 10x10 size-by-BE/ME portfolios

These tables provide the classic FF1992 descriptive evidence.

#### Step 4: Run Fama-MacBeth regressions
Monthly cross-sectional regressions are estimated for seven model variants:
- `M1_beta`
- `M2_ln_size`
- `M3_ln_be_me`
- `M4_beta_ln_size`
- `M5_beta_ln_be_me`
- `M6_ln_size_ln_be_me`
- `M7_all3`

The script stores monthly slopes and then computes average lambdas with NW(12) t-statistics.

### Outputs generated
Key outputs include:
- `master_panel_200001_202512.csv`
- `sample_coverage.csv`
- `june_characteristics.csv`
- `membership_jul_to_jun.csv`
- `table_i_size_beta_10x10.csv`
- `table_ii_size_only.csv`
- `table_ii_beta_only.csv`
- `table_iv_beme_only.csv`
- `table_v_size_beme_10x10.csv`
- `fm_monthly_slopes.csv`
- `table_iii_fama_macbeth.csv`
- `academic_tables.md`
- `academic_tables.tex`
- `academic_tables.txt`

---

## 6.2 Fama-French 1993 style replication

### Objective
Construct and evaluate China-specific FF3 factors:
- `MKT_RF`
- `SMB`
- `HML`

Then test whether these factors explain the returns of 25 size-BM test portfolios.

### Main scripts
From `Fama French 1993 (1992-2025)/scripts/`:
- `01_build_ff3_and_tables.py`
- `02_format_academic_tables.py`
- `03_format_latex_tables.py`
- `04_run_all.py`

### Step-by-step method

#### Step 1: Load stock, BE, market, and RF data
The script constructs the stock-level monthly panel from the same underlying sources used by the FF1992 pipeline.

#### Step 2: Form FF 2x3 portfolios
For each formation year:
- June size is used for the small/big split
- prior-December market equity and lagged book equity are used to form BM
- size is split into 2 groups
- BM is split into 3 groups using 30/70 breakpoints
- six base portfolios are formed: `SL`, `SM`, `SH`, `BL`, `BM`, `BH`

#### Step 3: Build monthly FF3 factors
The script computes monthly value-weighted returns for the six base portfolios and constructs:
- `SMB = (SH + SM + SL)/3 - (BH + BM + BL)/3`
- `HML = (SH + BH)/2 - (SL + BL)/2`
- `MKT_RF = RM - RF`

#### Step 4: Build 25 size-BM test portfolios
The script also constructs 5x5 size-BM portfolios used as test assets for model evaluation.

#### Step 5: Run time-series regressions of 25 portfolios on FF3 factors
For each 5x5 test portfolio, the script estimates:
- alpha
- market beta
- SMB loading
- HML loading
- `R^2`

with NW(12) t-statistics.

#### Step 6: Summarize model fit
The outputs include:
- factor summary statistics
- factor correlation matrix
- six portfolio summary statistics
- average excess returns of 25 portfolios
- 25 FF3 regressions
- alpha diagnostics
- pricing errors
- factor-premium significance table

### Outputs generated
Key outputs include:
- `ff3_factors_monthly.csv`
- `ff3_leg_returns.csv`
- `ff3_june_characteristics.csv`
- `ff3_port25_monthly.csv`
- `table_1_factor_summary.csv`
- `table_2_factor_correlation.csv`
- `table_3_six_portfolio_summary.csv`
- `table_4_25port_avg_excess_returns.csv`
- `table_5_25port_ff3_regressions.csv`
- `table_6_alpha_diagnostics.csv`
- `table_7_pricing_errors.csv`
- `table_8_factor_premia_significance.csv`
- `academic_tables.md`
- `academic_tables.tex`
- `academic_tables.txt`

---

## 6.3 Daniel-Titman 1997 style replication

### Objective
Test whether cross-sectional returns are better explained by:
- firm characteristics themselves, or
- factor loadings estimated from factor models

This is the characteristic-versus-covariance (or characteristic-versus-loading) distinction emphasized by Daniel and Titman (1997).

### Main scripts
From `Daniel and Titman 1997 JF (2000-2025)/scripts/`:
- `01_build_master_panel.py`
- `02_build_characteristics_and_factors.py`
- `03_estimate_preformation_betas.py`
- `04_make_dt_portfolios.py`
- `05_make_dt_tests.py`
- `06_format_academic_tables.py`
- `07_format_latex_tables.py`
- `08_run_all.py`
- `dt_utils.py`

### Step-by-step method

#### Step 1: Build master panel
As in FF1992, the D&T pipeline starts by creating a master monthly stock panel with returns, excess returns, market values, and accounting variables.

#### Step 2: Build June characteristics and FF3 factors
The script:
- forms June characteristics
- constructs both FF 2x3 legs and characteristic 3x3 groups
- writes a July-to-June membership file
- produces monthly FF3 factor series for the relevant sample window

#### Step 3: Estimate pre-formation factor loadings
Using a rolling 36-month window with a 24-observation minimum, the script estimates pre-formation betas relevant for the D&T sorts.

#### Step 4: Form 3x3 Daniel-Titman test portfolios
The script forms two kinds of grids:
- size tercile × `beta_SMB` tercile
- BM tercile × `beta_HML` tercile

This allows the code to compare:
- returns across different loadings while holding characteristics fixed, and
- returns across different characteristics while holding loadings fixed

#### Step 5: Compute characteristic-versus-loading spreads
The main output table reports mean monthly spreads and NW(12) t-statistics for:
- size characteristic held fixed, varying `beta_SMB`
- `beta_SMB` loading held fixed, varying size characteristic
- BM characteristic held fixed, varying `beta_HML`
- `beta_HML` loading held fixed, varying BM characteristic

### Outputs generated
Key outputs include:
- `master_panel_200001_202512.csv`
- `june_characteristics.csv`
- `membership_jul_to_jun.csv`
- `ff3_factors_monthly.csv`
- `preformation_betas.csv`
- `dt_size_3x3_monthly.csv`
- `dt_bm_3x3_monthly.csv`
- `table_dt_main_tests.csv`
- `academic_tables.md`
- `academic_tables.tex`
- `academic_tables.txt`

---

## 7. Sample Windows Completed and Why They Matter

## 7.1 Full long sample: 1992-07 to 2025-12
This is the broadest China A-share sample in the project and captures:
- the early market opening period
- the pre-split-share-reform era
- the 2005-2006 reform period
- the 2007 boom/bust
- the post-2010 modernization period
- the later institutionalization period

This sample is useful for maximum power and for broad historical comparison, but it also mixes very different market regimes.

## 7.2 Main modern sample: 2000-01 to 2025-12
This sample starts after the earliest years of the Chinese market and is useful for:
- improving data comparability
- reducing the extreme thin-market effects of the 1990s
- focusing on the period more often used in modern empirical China papers

This sample turned out to be especially informative for the apparent value effect, because it showed stronger BE/ME significance than the full 1992-2025 sample.

## 7.3 Pre/post-2010 split
A key extension in this project is the split at:
- **pre period:** `1992-07` to `2010-03`
- **post period:** `2010-04` to `2025-12`

### Why this split was used
The split is motivated by an institutional-regime interpretation centered on:
- China’s margin trading and short-selling pilot launched in March 2010
- broader post-2010 development of arbitrage, hedging, and more sophisticated institutional trading

This split is not a perfect structural-break design, but it is economically meaningful and aligns with the idea that the Chinese market after 2010 is a more modern and arbitrage-capable environment.

## 7.4 Archived early-sample check: 1992-07 to 1999-12
The `1992-1999` folders isolate the earliest stage of the Chinese market. These are useful as descriptive checks because they show how extreme and unstable the earliest period was.

---

## 8. Headline Empirical Results

## 8.1 Fama-French 1992 results

### 8.1.1 FF1992, full sample 1992-2025
From `Fama French 1992 (1992-2025)/output/academic_tables.md`:

#### Key Fama-MacBeth results
Model `M7_all3`:
- `beta = -0.0040`, `t = -1.443` → **not significant**
- `ln_size = -0.0060`, `t = -2.928` → **highly significant**
- `ln_be_me = 0.0020`, `t = 1.249` → **not significant**

#### Interpretation
- Beta does not price the cross-section.
- Size is a robust negative relation: smaller firms earn higher average returns.
- Book-to-market is not a reliable independent predictor in the full long sample once size and beta are controlled for.

### 8.1.2 FF1992, modern sample 2000-2025
From `Fama French 1992 (2000-2025)/output/academic_tables.md`:

Model `M7_all3`:
- `beta = -0.0004`, `t = -0.364` → **not significant**
- `ln_size = -0.0045`, `t = -3.137` → **strongly significant**
- `ln_be_me = 0.0025`, `t = 3.005` → **strongly significant**

#### Interpretation
- Size remains very strong.
- Value appears significant in this sub-sample.
- This raised the question of whether the value result is structural or concentrated in a particular historical regime.

### 8.1.3 FF1992, pre-2010 split
From `Fama French 1992 (1992-2010M03)/output/table_iii_fama_macbeth.csv`:

Model `M7_all3`:
- `beta = -0.00594`, `t = -1.1466` → **not significant**
- `ln_size = -0.00797`, `t = -2.1861` → **significant**
- `ln_be_me = 0.00212`, `t = 0.7315` → **not significant**

#### Interpretation
- Size remains significant.
- Value disappears once the long pre-2010 period is isolated.
- This suggests the 2000-2025 value result is not a stable cross-sectional law.

### 8.1.4 FF1992, post-2010 split
From `Fama French 1992 (2010M04-2025)/output/table_iii_fama_macbeth.csv`:

Model `M7_all3`:
- `beta = -0.00186`, `t = -1.6058` → **not significant**
- `ln_size = -0.00388`, `t = -2.5414` → **significant**
- `ln_be_me = 0.00177`, `t = 1.8507` → **marginal only**

#### Interpretation
- Size remains robust in the post-2010 era.
- Value is at most weakly marginal and far from a strong, stable premium.

### 8.1.5 FF1992, early sample 1992-1999
From `Fama French 1992 (1992-1999)/output/academic_tables.md`:

Model `M7_all3`:
- `beta = -0.0157`, `t = -1.308` → **not significant**
- `ln_size = -0.0158`, `t = -2.108` → **significant**
- `ln_be_me = -0.0002`, `t = -0.027` → **not significant**

#### Interpretation
Even in the earliest and most extreme market environment, the strongest systematic cross-sectional signal is still size, not beta or value.

### FF1992 overall conclusion
Across all FF1992 windows examined:
- **beta is not priced**
- **size is consistently priced**
- **value is episodic, unstable, and generally not robust**

---

## 8.2 Fama-French 1993 results

### 8.2.1 FF1993, full sample 1992-2025
From `Fama French 1993 (1992-2025)/output/academic_tables.md`:

#### Factor-premia significance
- `MKT_RF = 0.674%`, `t = 1.337` → **not significant**
- `SMB = 0.860%`, `t = 3.121` → **strongly significant**
- `HML = 0.417%`, `t = 1.644` → **not conventionally significant**

#### Alpha diagnostics
- `n_sig_5pct = 4/25`
- `n_sig_1pct = 2/25`
- `RMSE = 0.306%`
- `MAE = 0.223%`

#### Interpretation
- The China SMB factor is real and statistically robust.
- HML is weak and not reliably priced.
- The FF3 model fits the 25 size-BM portfolios reasonably, but not perfectly.

### 8.2.2 FF1993, modern sample 2000-2025
From `Fama French 1993 (2000-2025)/output/academic_tables.md`:

#### Factor-premia significance
- `MKT_RF = 0.492%`, `t = 0.949` → **not significant**
- `SMB = 0.840%`, `t = 2.696` → **strongly significant**
- `HML = 0.161%`, `t = 0.796` → **not significant**

#### Alpha diagnostics
- `n_sig_5pct = 9/25`
- `n_sig_1pct = 5/25`
- `RMSE = 0.232%`
- `MAE = 0.185%`

#### Interpretation
- SMB remains strong.
- HML becomes even weaker in the 2000-2025 sample.
- The model leaves more statistically significant alphas than in the 1992-2025 sample, suggesting imperfect pricing even when restricted to the more modern sample.

### 8.2.3 FF1993, pre-2010 split
From `Fama French 1993 (1992-2010M03)/output/table_8_factor_premia_significance.csv` and `table_6_alpha_diagnostics.csv`:

#### Factor-premia significance
- `MKT_RF = 0.966%`, `t = 1.109` → **not significant**
- `SMB = 1.099%`, `t = 2.705` → **strongly significant**
- `HML = 0.649%`, `t = 1.580` → **not significant**

#### Alpha diagnostics
- `n_sig_5pct = 1/25`
- `n_sig_1pct = 0/25`

#### Interpretation
- Pre-2010 China shows a strong size factor.
- HML remains statistically weak.
- FF3 fit is actually fairly tight in this split when judged by significant alpha counts.

### 8.2.4 FF1993, post-2010 split
From `Fama French 1993 (2010M04-2025)/output/table_8_factor_premia_significance.csv` and `table_6_alpha_diagnostics.csv`:

#### Factor-premia significance
- `MKT_RF = 0.346%`, `t = 0.819` → **not significant**
- `SMB = 0.591%`, `t = 1.678` → **marginally significant**
- `HML = 0.156%`, `t = 0.598` → **not significant**

#### Alpha diagnostics
- `n_sig_5pct = 7/25`
- `n_sig_1pct = 6/25`

#### Interpretation
- SMB weakens after 2010, though it does not disappear entirely.
- HML is clearly not a priced factor in the post-2010 sample.
- FF3 leaves substantially more unexplained alphas post-2010 than pre-2010.

### 8.2.5 FF1993, early sample 1992-1999
From `Fama French 1993 (1992-1999)/output/academic_tables.md`:

#### Factor-premia significance
- `MKT_RF = 0.932%`, `t = 0.785` → **not significant**
- `SMB = 1.649%`, `t = 2.796` → **strongly significant**
- `HML = 0.873%`, `t = 0.953` → **not significant**

#### Interpretation
Even in the earliest sample, SMB is the only clearly reliable factor premium. HML does not become a robust factor despite a high mean return because volatility and instability keep its t-statistic weak.

### FF1993 overall conclusion
Across all FF1993 windows examined:
- **SMB is the only consistently significant non-market factor**
- **HML is not a reliable China factor**
- **the three-factor model fits some subsamples better than others, but its weak point is clearly the value dimension**

---

## 8.3 Daniel-Titman results

### 8.3.1 D&T, modern sample 2000-2025
From `Daniel and Titman 1997 JF (2000-2025)/output/academic_tables.md`:

#### Size-side tests
When **size characteristic is held fixed** and `beta_SMB` is varied:
- pooled spread = `-0.214%/month`, `t = -1.602` → **not significant**

When **beta_SMB loading is held fixed** and size is varied:
- pooled spread = `0.934%/month`, `t = 2.870` → **strongly significant**

#### BM-side tests
When **BM characteristic is held fixed** and `beta_HML` is varied:
- pooled spread = `-0.105%/month`, `t = -0.695` → **not significant**

When **beta_HML loading is held fixed** and BM is varied:
- pooled spread = `0.283%/month`, `t = 1.211` → **not significant**

#### Interpretation
- The size effect behaves like a **characteristic effect**, not a risk-loading effect.
- The value side is weak in both characteristic and loading form.
- This is strongly consistent with the broader FF1992/FF1993 evidence.

### 8.3.2 D&T, full sample 1992-2025
From `Daniel and Titman 1997 JF (1992-2025)/output/academic_tables.md`:

#### Size-side tests
- Loading-held-fixed size spread pooled = `1.102%/month`, `t = 3.802` → **strongly significant**
- Characteristic-held-fixed loading spread pooled = `-0.135%/month`, `t = -0.412` → **not significant**

#### BM-side tests
- Loading-held-fixed BM spread pooled = `0.399%/month`, `t = 1.855` → **marginal only**
- Characteristic-held-fixed `beta_HML` spread pooled = `-0.053%/month`, `t = -0.282` → **not significant**

#### Interpretation
- The full-sample D&T evidence also supports a characteristic-based size premium.
- BM remains weak, inconsistent, and at most marginal.

### D&T overall conclusion
Across the D&T analyses examined:
- **size works mainly as a characteristic effect**
- **loadings on SMB do not explain away the size premium**
- **value/HML is weak and not robustly supported**

---

## 9. Interpretation of the Time-Split Results

The time-split exercise was one of the most important extensions completed in this project.

## 9.1 Why split at 2010-04
The chosen break is economically motivated by the March 2010 launch of China’s margin-trading and short-selling pilot. Using April 2010 as the first post-break month provides a clean monthly separation.

The split is intended to capture changes in:
- market sophistication
- arbitrage capacity
- shorting and leverage mechanisms
- institutional participation
- pricing efficiency

## 9.2 What the split shows

### On size
- Size remains significant in FF1992 before and after 2010.
- SMB is strongest before 2010, but still present or marginal after 2010.
- D&T indicates the size effect is characteristic-based rather than loading-based.

**Interpretation:** size is the most robust and persistent China cross-sectional effect in this project.

### On value
- Full-sample and 2000-2025 pooled windows can make value look stronger than it really is.
- Once the sample is broken into regimes, the value signal weakens sharply.
- FF1993 HML is insignificant in both the pre-2010 and post-2010 split.
- D&T does not rescue value by showing a strong characteristic effect either.

**Interpretation:** value is not a stable or reliable priced dimension in China.

### On model fit
- Pre-2010 FF3 leaves relatively few significant alphas.
- Post-2010 FF3 leaves many more significant alphas.

This is an interesting result because one might expect a more modern market to be easier for the model to price. Instead, the post-2010 environment appears to contain other dimensions of returns not captured by the simple FF3 structure.

---

## 10. What to Conclude About Value in China

The most defensible conclusion from the project is:

> **Value is not a robust or persistent pricing effect in Chinese A-shares.**

A more complete version is:

> The apparent value effect in pooled windows such as 2000-2025 is best interpreted as episodic and regime-specific rather than as a stable cross-sectional premium. Once the sample is examined by sub-period and with characteristic-versus-loading tests, the evidence strongly favors size as the durable effect and rejects beta as a priced dimension, while value remains weak, unstable, and statistically fragile.

### Why this conclusion is stronger than saying “value exists”
Because the evidence shows:
- FF1992 full sample: value not significant in the all-controls model
- FF1992 pre-2010: value not significant
- FF1992 post-2010: only marginal
- FF1993 pre-2010: HML not significant
- FF1993 post-2010: HML not significant
- D&T: no robust support for value as either characteristic or loading effect

The strongest project-wide summary is therefore:
- **beta: not priced**
- **size: robustly priced**
- **value: not robustly priced**

---

## 11. Why 2000-2025 Can Still Show a Stronger Value Signal

One important interpretive issue addressed in the project is why the `2000-2025` FF1992 window can produce a significant `ln_be_me` coefficient while the split-sample evidence is weak.

The most plausible explanation is that the signal is concentrated in the **2000s**, particularly around structural repricing episodes, rather than being persistent through the whole modern era.

### Working interpretation
The stronger apparent value signal in `2000-2025` likely reflects a combination of:
- the exclusion of the noisy earliest 1990s period
- the concentration of repricing in the 2000s
- historical market distortions related to the split-share reform era
- a pooled-regression power effect that averages across heterogeneous subperiods

However, the time-split exercise shows that this should **not** be interpreted as stable evidence for a general China value premium.

---

## 12. Methodological Caveats and Limitations

### 12.1 Total market equity vs tradable/free-float market equity
The scripts use `Msmvttl` from the monthly stock file, which is a total market equity measure.

This matters because:
- pre-reform China had large non-tradable share blocks
- prices were discovered on tradable float, not on the full capital base
- this can distort measured size and BM, especially pre-2006

That said, the project’s substantive conclusion does not rely on free-float correction:
- if anything, this issue makes value harder to interpret cleanly
- but the overwhelming empirical pattern across windows still says value is not robust

### 12.2 Structural breaks in China are large
China’s equity market changed dramatically across:
- the early market-opening period
- state-owned share overhang
- the 2005-2006 split-share reform
- the 2007 boom-bust cycle
- the post-2010 development of margin trading and arbitrage

As a result, pooled full-sample estimates should always be interpreted cautiously.

### 12.3 Three factors may be too few for post-2010 China
The increase in significant alphas after 2010 suggests that FF3 is missing important dimensions of returns in the later period.

Potential missing dimensions include:
- profitability
- investment
- turnover / sentiment
- mispricing or speculative intensity
- China-specific state-ownership or policy exposure

### 12.4 Pure-Python implementation trade-offs
The code is transparent and reproducible, but because all estimation is hand-coded:
- numerical routines are intentionally simple
- there is less convenience than in a scientific-Python or R environment
- future extensions may eventually benefit from a more modular statistical backend

---

## 13. Practical Summary of What Was Done

In plain terms, the project accomplished the following:

1. Built and maintained raw-data-driven replication pipelines for FF1992, FF1993, and Daniel-Titman tests in China.
2. Standardized all pipelines around consistent data sources and timing conventions.
3. Ran the main full-sample replications.
4. Ran modern-sample replications beginning in 2000.
5. Built pre/post-2010 split-sample folders and executed those analyses.
6. Verified the key outputs across the split folders.
7. Compared results across methods and time periods.
8. Resolved the interpretation of the value effect by showing it is not stable across regimes.
9. Reached a consistent cross-method conclusion favoring size over value or beta.

---

## 14. Recommended Paper Positioning

If this project is written up as a paper or thesis chapter, the most coherent positioning is:

### Main empirical message
> In China A-shares, the only robust classic Fama-French style cross-sectional pattern is size. Beta is not priced, and value is episodic rather than persistent. Daniel-Titman tests further show that the size effect behaves as a characteristic effect rather than a risk-loading effect.

### Stronger interpretation
> The apparent value premium in pooled samples is largely a historical artifact of specific reform-era and early-market conditions, not a stable pricing relation in the modern Chinese market.

### Relationship to the literature
This project’s findings are best framed as being consistent with the literature arguing that:
- size matters in China
- standard HML is weak in China
- classic U.S. factor structures do not transport cleanly into the Chinese institutional environment

---

## 15. Key File-Level Outputs to Cite

### FF1992 key outputs
- `Fama French 1992 (1992-2025)/output/table_iii_fama_macbeth.csv`
- `Fama French 1992 (2000-2025)/output/table_iii_fama_macbeth.csv`
- `Fama French 1992 (1992-2010M03)/output/table_iii_fama_macbeth.csv`
- `Fama French 1992 (2010M04-2025)/output/table_iii_fama_macbeth.csv`
- `Fama French 1992 (1992-2025)/output/academic_tables.md`

### FF1993 key outputs
- `Fama French 1993 (1992-2025)/output/table_8_factor_premia_significance.csv`
- `Fama French 1993 (2000-2025)/output/table_8_factor_premia_significance.csv`
- `Fama French 1993 (1992-2010M03)/output/table_8_factor_premia_significance.csv`
- `Fama French 1993 (2010M04-2025)/output/table_8_factor_premia_significance.csv`
- `Fama French 1993 (1992-2025)/output/table_6_alpha_diagnostics.csv`
- `Fama French 1993 (2000-2025)/output/table_6_alpha_diagnostics.csv`

### Daniel-Titman key outputs
- `Daniel and Titman 1997 JF (2000-2025)/output/table_dt_main_tests.csv`
- `Daniel and Titman 1997 JF (1992-2025)/output/table_dt_main_tests.csv`
- `Daniel and Titman 1997 JF (2000-2025)/output/academic_tables.md`

---

## 16. Final Bottom-Line Conclusions

### Conclusion 1: Beta is not priced
Across the FF1992 regressions, beta never emerges as a robust positive explanatory variable for average returns.

### Conclusion 2: Size is the dominant classic cross-sectional effect in China
This is the strongest and most stable result across:
- full sample
- 2000-2025 sample
- pre-2010 sample
- post-2010 sample
- FF1992 cross-sectional regressions
- FF1993 factor premia
- Daniel-Titman tests

### Conclusion 3: Value is not a reliable China premium
Value can look stronger in pooled windows such as `2000-2025`, but the combined evidence shows that:
- it is not stable across regimes
- it is not a reliable FF3 factor premium
- it does not receive strong support in Daniel-Titman tests

### Conclusion 4: The post-2010 market is different
The post-2010 sample weakens SMB and leaves more unexplained alpha in FF3 regressions, suggesting that the standard FF3 framework is incomplete for modern China.

### Conclusion 5: The cleanest project-wide message
The simplest and strongest summary of everything done in this workspace is:

> **China A-share returns show a robust size effect, no reliable beta effect, and no stable value effect.**

---

## 17. Suggested Next Extensions

Natural next steps, if the project continues, would be:
- extend Daniel-Titman tests to the pre/post-2010 split directly
- add profitability and investment factors to test whether FF5-style structures outperform FF3 in China
- test free-float market equity as a robustness check in the pre-reform period
- add industry-neutral versions of the sorts and regressions
- compare equal-weighted and value-weighted versions more systematically
- write a paper-style master table combining FF1992, FF1993, and D&T results in one place

---

## 18. Status of This Document

This document is based on the scripts and output files currently present in the workspace and is intended to serve as a detailed project memo / research record. It is written to be used as:
- a project summary
- a methods appendix draft
- a writing aid for a paper or thesis
- a handoff document for future extension work
