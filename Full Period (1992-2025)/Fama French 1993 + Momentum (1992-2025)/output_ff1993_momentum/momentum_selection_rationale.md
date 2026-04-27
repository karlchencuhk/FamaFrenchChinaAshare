## Optimal Momentum Strategy Selection

### Candidate strategies considered:
- 9/6, 12/1, 6/6, 9/9, 12/3, 12/6, 9/3, 12/12, 3/6, 6/3, 6/1, 3/3, 3/1

### Top 3 performing strategies:
1. 9/6 - t=1.759, Sharpe=0.077
2. 12/1 - t=1.713, Sharpe=0.085
3. 6/6 - t=1.591, Sharpe=0.077

### Selected strategy: 9/6

### Rationale:
- Selected by best composite ranking using Sharpe, t-stat, mean return, and drawdown.
- Uses monthly overlapping portfolio implementation to reduce horizon mismatch.
- China A-share momentum appears strongest under this formation/holding pair in-sample.

### Implementation details for selected strategy:
- Formation period: 9 months
- Holding period: 6 months
- Skip month: 1 (t-1)
- Rebalancing: Monthly with 6 overlapping cohorts