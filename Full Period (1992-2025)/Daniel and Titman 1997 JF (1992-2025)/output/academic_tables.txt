# Daniel and Titman (1997) Style Tests — China 1992-2025

## Table 1A. Mean Excess Monthly Return of 45 Portfolios (Size $\times$ BM $\times$ HML Loading)
| Characteristic portfolio (SZ,BM) | HML loading portfolio 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| SZ1BM1 | 1.653 | 1.515 | 1.427 | 2.006 | 1.410 |
| SZ1BM2 | 1.681 | 2.273 | 1.917 | 1.915 | 1.703 |
| SZ1BM3 | 2.243 | 1.850 | 1.883 | 1.723 | 2.070 |
| SZ2BM1 | 0.843 | 1.038 | 0.897 | 0.850 | 0.772 |
| SZ2BM2 | 1.218 | 1.555 | 1.612 | 1.089 | 1.119 |
| SZ2BM3 | 1.802 | 1.361 | 1.288 | 1.260 | 1.352 |
| SZ3BM1 | 0.415 | 0.367 | 0.767 | 0.770 | 0.461 |
| SZ3BM2 | 0.536 | 0.925 | 0.752 | 1.107 | 0.584 |
| SZ3BM3 | 1.125 | 0.807 | 1.206 | 1.113 | 0.769 |

Notes:
- Characteristic portfolios are formed on Size tercile and BM tercile: `SZ1BM1` ... `SZ3BM3`.
- Within each characteristic portfolio and formation year, stocks are sorted into 5 portfolios by pre-formation $\beta^{HML}$ (1=low, 5=high).
- Cell entries are value-weighted mean excess monthly returns in percent.

## Table 1. Daniel-Titman Characteristic-vs-Loading Tests (1992-2025)
| Test family | Contrast | Group | Mean spread (%/mo) | NW12 t | Sig | N months |
| --- | --- | --- | --- | --- | --- | --- |
| Size characteristic held fixed | High beta_SMB - Low beta_SMB | Size tercile 1 | 0.102 | 0.269 |  | 378 |
| Size characteristic held fixed | High beta_SMB - Low beta_SMB | Size tercile 2 | -0.075 | -0.251 |  | 378 |
| Size characteristic held fixed | High beta_SMB - Low beta_SMB | Size tercile 3 | -0.698 | -2.232 | ** | 366 |
| Size characteristic held fixed | High beta_SMB - Low beta_SMB | Pooled across size terciles | -0.135 | -0.412 |  | 378 |
| beta_SMB loading held fixed | Small size - Big size | beta_SMB bin 1 | 0.955 | 2.401 | ** | 378 |
| beta_SMB loading held fixed | Small size - Big size | beta_SMB bin 2 | 0.957 | 3.355 | *** | 378 |
| beta_SMB loading held fixed | Small size - Big size | beta_SMB bin 3 | 1.342 | 4.767 | *** | 366 |
| beta_SMB loading held fixed | Small size - Big size | Pooled across beta_SMB bins | 1.102 | 3.802 | *** | 378 |
| BM characteristic held fixed | High beta_HML - Low beta_HML | BM tercile 1 | 0.105 | 0.356 |  | 378 |
| BM characteristic held fixed | High beta_HML - Low beta_HML | BM tercile 2 | -0.010 | -0.043 |  | 378 |
| BM characteristic held fixed | High beta_HML - Low beta_HML | BM tercile 3 | -0.254 | -0.850 |  | 378 |
| BM characteristic held fixed | High beta_HML - Low beta_HML | Pooled across BM terciles | -0.053 | -0.282 |  | 378 |
| beta_HML loading held fixed | High BM - Low BM | beta_HML bin 1 | 0.626 | 2.143 | ** | 378 |
| beta_HML loading held fixed | High BM - Low BM | beta_HML bin 2 | 0.306 | 1.411 |  | 378 |
| beta_HML loading held fixed | High BM - Low BM | beta_HML bin 3 | 0.267 | 0.869 |  | 378 |
| beta_HML loading held fixed | High BM - Low BM | Pooled across beta_HML bins | 0.399 | 1.855 | * | 378 |

Interpretation guide:
- Characteristics view (Daniel-Titman): significant characteristic spreads when loadings are held fixed, and weak loading spreads when characteristics are held fixed.
- Risk-loading view (Fama-French): significant loading spreads when characteristics are held fixed.

## Table 2. Fama-MacBeth Regressions: Characteristics and Loadings Together
| Model | Coefficient | Avg slope | NW12 t | Sig | N months | Avg N stocks |
| --- | --- | --- | --- | --- | --- | --- |
| DT_FM_chars_and_loadings | intercept | 0.068 | 2.705 | *** | 378 | 1479.442 |
| DT_FM_chars_and_loadings | ln_size | -0.005 | -3.695 | *** | 378 | 1479.442 |
| DT_FM_chars_and_loadings | ln_be_me | 0.004 | 2.243 | ** | 378 | 1479.442 |
| DT_FM_chars_and_loadings | beta_smb | -0.000 | -0.196 |  | 378 | 1479.442 |
| DT_FM_chars_and_loadings | beta_hml | 0.000 | 0.448 |  | 378 | 1479.442 |

Cross-sectional regression each month:
- $R_{i,t}^{e}=\gamma_{0,t}+\gamma_{1,t}\ln(Size_{i,t-1})+\gamma_{2,t}\ln(BE/ME_{i,t-1})+\gamma_{3,t}eta^{SMB}_{i,t-1}+\gamma_{4,t}eta^{HML}_{i,t-1}+arepsilon_{i,t}$
- Reported slopes are time-series means of $\gamma_{k,t}$ with Newey-West (12) $t$-statistics.
