# Daniel and Titman (1997) Style Tests — China 1992-2025

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
