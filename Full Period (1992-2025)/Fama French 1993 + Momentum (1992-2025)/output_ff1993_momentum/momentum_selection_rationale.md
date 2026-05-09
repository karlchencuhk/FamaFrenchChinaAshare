## Momentum Strategy Protocol (Jegadeesh-Titman style)

### Candidate strategies considered:
- 3/1, 3/3, 3/6, 6/1, 6/3, 6/6, 9/3, 9/6, 9/9, 12/1, 12/3, 12/6, 12/12

### Grid evidence (reported, not optimized):
1. 9/6 - t=1.759, Sharpe=0.077
2. 12/1 - t=1.713, Sharpe=0.085
3. 6/6 - t=1.591, Sharpe=0.077

### Robustness principle:
- Following Jegadeesh-Titman style practice, momentum is evaluated on a standard J/K grid and interpreted by the pattern across strategies.
- We do not claim a uniquely optimal in-sample strategy from this table.

### Benchmark strategy used for FF4: 12/3

### Rationale:
- We report the full J/K grid and emphasize robustness across specifications.
- A pre-specified benchmark is used only as an operational input to build a single FF4 factor series.
- The FF4 UMD leg is constructed in Carhart style: UMD = 0.5*(Small High + Big High) - 0.5*(Small Low + Big Low).
- For FF4 construction, we use a pre-specified benchmark momentum strategy.
- This separates model evaluation from in-sample strategy tuning.

### Implementation details for benchmark strategy:
- Formation period: 12 months
- Holding period: 3 months
- Skip month: 1 (t-1)
- Rebalancing: Monthly with 3 overlapping cohorts