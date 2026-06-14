# P3 Triage Agent Report — Personal Finance Advisor
**Generated:** 2026-06-14  
**Agent:** P3-Triage-Agent (`agents/triage_agent.py`)  
**Scope:** All customer profiles · All expense categories  
**Severity Scale:** P1-Critical → P2-High → P3-Medium → P4-Low → P5-Healthy

---

## Executive Summary

| Customer | Income (₹) | Total Expense (₹) | Savings (₹) | Savings Rate | Overall Severity |
|----------|-----------|------------------|------------|-------------|------------------|
| Alice    | 75,000    | 62,000           | 13,000     | 17.3%       | **P4-Low**       |
| Bob      | 55,000    | 50,000           | 5,000      | 9.1%        | **P2-High**      |
| Carol    | 95,000    | 77,000           | 18,000     | 18.9%       | **P3-Medium**    |
| David    | 40,000    | 38,000           | 2,000      | 5.0%        | **P3-Medium**    |

> **Fleet-level risk:** 1 customer at P2 (Bob), 2 at P3, 1 at P4. No P1-Critical profiles.

---

## Customer Reports

---

### Alice — P4-Low

**Profile:** Mid-career software engineer, single, rents apartment.  
**Health:** Fair | Savings ₹13,000 / month (17.3%)

| Category      | Spent (₹) | Benchmark (₹) | Overspend (₹) | % of Income | Severity   |
|---------------|-----------|--------------|--------------|-------------|------------|
| Food          | 12,000    | 11,250       | 750          | 16.0%       | P4-Low     |
| Shopping      | 8,500     | 7,500        | 1,000        | 11.3%       | P4-Low     |
| Entertainment | 4,000     | 3,750        | 250          | 5.3%        | P4-Low     |
| Rent          | 18,000    | 22,500       | —            | 24.0%       | P5-Healthy |
| EMI           | 10,000    | 15,000       | —            | 13.3%       | P5-Healthy |
| Travel        | 6,000     | 6,000        | —            | 8.0%        | P5-Healthy |
| Utilities     | 3,500     | 3,750        | —            | 4.7%        | P5-Healthy |

**Issues (3):**
- **[P4-Low] Shopping** — ₹1,000 over benchmark  
  > Action: Introduce a spending cap; apply the 24-hour rule.
- **[P4-Low] Food** — ₹750 over benchmark  
  > Action: Reduce dining out; meal prep twice a week.
- **[P4-Low] Entertainment** — ₹250 over benchmark  
  > Action: Share streaming plans; limit impulse bookings.

**Verdict:** Minor overspends only. Alice can reach the 20% savings target by trimming ₹2,000 from Shopping and Food.

---

### Bob — P2-High ⚠️

**Profile:** Marketing executive, high discretionary spending.  
**Health:** Low | Savings ₹5,000 / month (9.1%)

| Category      | Spent (₹) | Benchmark (₹) | Overspend (₹) | % of Income | Severity   |
|---------------|-----------|--------------|--------------|-------------|------------|
| Shopping      | 12,000    | 5,500        | 6,500        | 21.8%       | P2-High    |
| Entertainment | 6,500     | 2,750        | 3,750        | 11.8%       | P2-High    |
| Food          | 9,500     | 8,250        | 1,250        | 17.3%       | P4-Low     |
| EMI           | 12,000    | 11,000       | 1,000        | 21.8%       | P4-Low     |
| Utilities     | 3,000     | 2,750        | 250          | 5.5%        | P4-Low     |
| Rent          | 15,000    | 16,500       | —            | 27.3%       | P5-Healthy |
| Travel        | 2,000     | 4,400        | —            | 3.6%        | P5-Healthy |

**Issues (5):**
- **[P2-High] Shopping** — ₹6,500 over benchmark (118% above ideal)  
  > Action: Introduce a spending cap; apply the 24-hour rule.
- **[P2-High] Entertainment** — ₹3,750 over benchmark (136% above ideal)  
  > Action: Share streaming plans; limit impulse bookings.
- **[P4-Low] Food** — ₹1,250 over benchmark  
  > Action: Reduce dining out; meal prep twice a week.
- **[P4-Low] EMI** — ₹1,000 over benchmark  
  > Action: Avoid adding new loans while existing ones are active.
- **[P4-Low] Utilities** — ₹250 over benchmark  
  > Action: Audit subscriptions; use energy-efficient appliances.

**Verdict:** Bob is the highest-risk profile. Shopping (21.8% of income) and Entertainment (11.8%) are the primary drivers. Reducing these two categories to benchmark would free ₹10,250/month and push savings rate to 27.8%.

---

### Carol — P3-Medium

**Profile:** Senior manager, frequent traveler, home loan EMI.  
**Health:** Fair | Savings ₹18,000 / month (18.9%)

| Category      | Spent (₹) | Benchmark (₹) | Overspend (₹) | % of Income | Severity   |
|---------------|-----------|--------------|--------------|-------------|------------|
| Travel        | 11,000    | 7,600        | 3,400        | 11.6%       | P3-Medium  |
| Food          | 14,000    | 14,250       | —            | 14.7%       | P5-Healthy |
| Rent          | 22,000    | 28,500       | —            | 23.2%       | P5-Healthy |
| EMI           | 15,000    | 19,000       | —            | 15.8%       | P5-Healthy |
| Shopping      | 7,000     | 9,500        | —            | 7.4%        | P5-Healthy |
| Utilities     | 4,500     | 4,750        | —            | 4.7%        | P5-Healthy |
| Entertainment | 3,500     | 4,750        | —            | 3.7%        | P5-Healthy |

**Issues (1):**
- **[P3-Medium] Travel** — ₹3,400 over benchmark (44.7% above ideal)  
  > Action: Book ahead; switch to train for short distances.

**Verdict:** Carol is otherwise well-managed. Travel is the sole concern. Booking trips in advance or consolidating business travel would close the gap and push savings above 22%.

---

### David — P3-Medium

**Profile:** Junior analyst, careful spender, moderate savings.  
**Health:** Low | Savings ₹2,000 / month (5.0%)

| Category      | Spent (₹) | Benchmark (₹) | Overspend (₹) | % of Income | Severity   |
|---------------|-----------|--------------|--------------|-------------|------------|
| Food          | 8,000     | 6,000        | 2,000        | 20.0%       | P3-Medium  |
| Shopping      | 5,000     | 4,000        | 1,000        | 12.5%       | P3-Medium  |
| Entertainment | 3,000     | 2,000        | 1,000        | 7.5%        | P3-Medium  |
| Utilities     | 2,500     | 2,000        | 500          | 6.2%        | P3-Medium  |
| Rent          | 12,000    | 12,000       | —            | 30.0%       | P5-Healthy |
| EMI           | 6,000     | 8,000        | —            | 15.0%       | P5-Healthy |
| Travel        | 1,500     | 3,200        | —            | 3.8%        | P5-Healthy |

**Issues (4):**
- **[P3-Medium] Food** — ₹2,000 over benchmark (33.3% above ideal)  
  > Action: Reduce dining out; meal prep twice a week.
- **[P3-Medium] Shopping** — ₹1,000 over benchmark  
  > Action: Introduce a spending cap; apply the 24-hour rule.
- **[P3-Medium] Entertainment** — ₹1,000 over benchmark  
  > Action: Share streaming plans; limit impulse bookings.
- **[P3-Medium] Utilities** — ₹500 over benchmark  
  > Action: Audit subscriptions; use energy-efficient appliances.

**Verdict:** David's 5% savings rate is critically low despite a modest income. All four overspends are P3-Medium — no single large leak, but compounding across categories leaves almost no buffer. Targeting Food first (₹2,000 savings) would double the monthly savings immediately.

---

## Fleet-Level Findings

### Category Risk Heatmap

| Category      | Alice    | Bob       | Carol    | David    | Risk Level  |
|---------------|----------|-----------|----------|----------|-------------|
| Shopping      | P4-Low   | P2-High   | —        | P3-Med   | **High**    |
| Entertainment | P4-Low   | P2-High   | —        | P3-Med   | **High**    |
| Food          | P4-Low   | P4-Low    | —        | P3-Med   | Medium      |
| Travel        | —        | —         | P3-Med   | —        | Low         |
| Utilities     | —        | P4-Low    | —        | P3-Med   | Low         |
| EMI           | —        | P4-Low    | —        | —        | Low         |
| Rent          | —        | —         | —        | —        | None        |

### Top Systemic Issues

1. **Shopping** appears overspent in 3 of 4 profiles — the most common single risk across the portfolio.
2. **Entertainment** appears overspent in 3 of 4 profiles — driven by untracked subscriptions and impulse bookings.
3. **Savings rate** is below the 20% target for all four customers. Bob (9.1%) and David (5.0%) are critical.

### Recommended Actions (by priority)

| Priority | Action                                                              | Affected Customers |
|----------|---------------------------------------------------------------------|--------------------|
| 1        | Cap Shopping at 10% of income; use 24-hour rule                     | Alice, Bob, David  |
| 2        | Audit and cancel unused streaming + subscription services           | Bob, David         |
| 3        | Bob: reduce Entertainment by ₹3,750 (single largest recoverable item) | Bob              |
| 4        | David: meal prep 3x/week to cut Food by ₹1,500–2,000               | David              |
| 5        | Carol: pre-book travel 6–8 weeks ahead                              | Carol              |

---

## Severity Distribution

```
P1-Critical  ████░░░░░░░░░░░░░░░░  0 issues  (0%)
P2-High      ████████░░░░░░░░░░░░  2 issues  (15%)
P3-Medium    ████████████░░░░░░░░  6 issues  (46%)
P4-Low       ████████░░░░░░░░░░░░  5 issues  (38%)
P5-Healthy   ░░░░░░░░░░░░░░░░░░░░  0         —
```

**Total issues flagged:** 13 across 4 customers  
**Total recoverable savings per month:** ₹20,950 (if all benchmarks met)

---

*Report generated by P3-Triage-Agent — `agents/triage_agent.py` — Personal Finance Advisor v1.0*
