# Fairness audit (NFR-06, Governance Framework section 3)

## Fairness audit: 2026-09-16_validation (80 tickets)

Resolution rate = auto-responded and not blocked; quality score = routing accuracy against the labels; 95% Wilson intervals; variation = best segment in the group minus this segment. The Explanation column is for the author.

### tier (NOT within 5 points (14.2 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| Business customers | 30 | 90.0% (74.4% to 96.5%) | 73.3% (55.5% to 85.8%) | 14.2 pts | yes |  |
| Enterprise customers | 8 | 87.5% (52.9% to 97.8%) | 87.5% (52.9% to 97.8%) | best | yes |  |
| Standard customers | 42 | 61.9% (46.8% to 75.0%) | 73.8% (58.9% to 84.7%) | 13.7 pts | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- Business customers: 30.0% / 3.3% / 149.8 chars / 0.996 / 100.0% (n=22)
- Enterprise customers: 25.0% / 0.0% / 159.4 chars / 0.997 / 100.0% (n=6)
- Standard customers: 50.0% / 21.4% / 155.4 chars / 0.988 / 92.0% (n=25)

### fluency (NOT within 5 points (22.4 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| Tickets in fluent English | 61 | 75.4% (63.3% to 84.5%) | 80.3% (68.7% to 88.4%) | best | yes |  |
| Tickets in non-fluent English | 19 | 73.7% (51.2% to 88.2%) | 57.9% (36.3% to 76.9%) | 22.4 pts | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- Tickets in fluent English: 34.4% / 14.8% / 152.0 chars / 0.991 / 95.5% (n=44)
- Tickets in non-fluent English: 57.9% / 5.3% / 159.2 chars / 0.995 / 100.0% (n=9)

### ticket_length (NOT within 5 points (28.6 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| Long or complex tickets | 70 | 80.0% (69.2% to 87.7%) | 71.4% (60.0% to 80.7%) | 28.6 pts | yes |  |
| Short tickets (< 120 chars) | 10 | 40.0% (16.8% to 68.7%) | 100.0% (72.2% to 100.0%) | best | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- Long or complex tickets: 37.1% / 5.7% / 164.2 chars / 0.992 / 95.9% (n=49)
- Short tickets (< 120 chars): 60.0% / 60.0% / 79.9 chars / 0.995 / 100.0% (n=4)

### region (NOT within 5 points (26.5 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| region: asia_pacific | 21 | 85.7% (65.4% to 95.0%) | 85.7% (65.4% to 95.0%) | best | yes |  |
| region: europe | 25 | 76.0% (56.6% to 88.5%) | 80.0% (60.9% to 91.1%) | 5.7 pts | yes |  |
| region: latin_america | 7 | 57.1% (25.1% to 84.2%) | 85.7% (48.7% to 97.4%) | best | yes |  |
| region: north_america | 27 | 70.4% (51.5% to 84.2%) | 59.3% (40.7% to 75.5%) | 26.5 pts | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- region: asia_pacific: 28.6% / 9.5% / 160.4 chars / 0.981 / 100.0% (n=17)
- region: europe: 36.0% / 4.0% / 163.5 chars / 0.996 / 94.7% (n=19)
- region: latin_america: 57.1% / 28.6% / 135 chars / 0.995 / 100.0% (n=3)
- region: north_america: 48.1% / 18.5% / 144.1 chars / 0.996 / 92.9% (n=14)

### channel (NOT within 5 points (8.7 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| channel: chat | 22 | 63.6% (43.0% to 80.3%) | 77.3% (56.6% to 89.9%) | 0.1 pts | yes |  |
| channel: docs_comment | 16 | 68.8% (44.4% to 85.8%) | 68.8% (44.4% to 85.8%) | 8.7 pts | yes |  |
| channel: email | 31 | 83.9% (67.4% to 92.9%) | 77.4% (60.2% to 88.6%) | best | yes |  |
| channel: forum | 11 | 81.8% (52.3% to 94.9%) | 72.7% (43.4% to 90.2%) | 4.7 pts | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- channel: chat: 40.9% / 22.7% / 127.3 chars / 0.981 / 84.6% (n=13)
- channel: docs_comment: 50.0% / 12.5% / 155.1 chars / 0.995 / 100.0% (n=10)
- channel: email: 32.3% / 6.5% / 166.0 chars / 0.996 / 100.0% (n=22)
- channel: forum: 45.5% / 9.1% / 169.4 chars / 0.997 / 100.0% (n=8)

## Fairness audit: 2026-09-16_dev_full (500 tickets)

Resolution rate = auto-responded and not blocked; quality score = routing accuracy against the labels; 95% Wilson intervals; variation = best segment in the group minus this segment. The Explanation column is for the author.

### tier (NOT within 5 points (7.4 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| Business customers | 164 | 76.8% (69.8% to 82.6%) | 81.7% (75.1% to 86.9%) | best | yes |  |
| Enterprise customers | 83 | 81.9% (72.3% to 88.7%) | 77.1% (67.0% to 84.8%) | 4.6 pts | yes |  |
| Standard customers | 253 | 76.3% (70.7% to 81.1%) | 74.3% (68.6% to 79.3%) | 7.4 pts | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- Business customers: 35.4% / 7.3% / 157.8 chars / 0.988 / 91.1% (n=123)
- Enterprise customers: 38.6% / 6.0% / 161.8 chars / 0.992 / 94.9% (n=59)
- Standard customers: 39.1% / 4.7% / 159.2 chars / 0.985 / 94.3% (n=175)

### fluency (within 5 points)

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| Tickets in fluent English | 380 | 77.9% (73.5% to 81.8%) | 76.6% (72.1% to 80.6%) | 2.6 pts | yes |  |
| Tickets in non-fluent English | 120 | 75.8% (67.5% to 82.6%) | 79.2% (71.0% to 85.5%) | best | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- Tickets in fluent English: 39.2% / 4.7% / 163.4 chars / 0.986 / 94.8% (n=270)
- Tickets in non-fluent English: 33.3% / 9.2% / 145.9 chars / 0.991 / 88.5% (n=87)

### ticket_length (NOT within 5 points (11.7 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| Long or complex tickets | 451 | 79.6% (75.6% to 83.1%) | 76.1% (71.9% to 79.8%) | 11.7 pts | yes |  |
| Short tickets (< 120 chars) | 49 | 57.1% (43.3% to 70.0%) | 87.8% (75.8% to 94.3%) | best | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- Long or complex tickets: 36.8% / 2.4% / 166.7 chars / 0.989 / 94.2% (n=328)
- Short tickets (< 120 chars): 46.9% / 36.7% / 90.0 chars / 0.97 / 82.8% (n=29)

### region (NOT within 5 points (7.5 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| region: asia_pacific | 119 | 73.1% (64.5% to 80.3%) | 73.9% (65.4% to 81.0%) | 7.5 pts | yes |  |
| region: europe | 151 | 78.8% (71.6% to 84.6%) | 81.5% (74.5% to 86.9%) | best | yes |  |
| region: latin_america | 60 | 86.7% (75.8% to 93.1%) | 78.3% (66.4% to 86.9%) | 3.1 pts | yes |  |
| region: north_america | 170 | 75.9% (68.9% to 81.7%) | 75.3% (68.3% to 81.2%) | 6.2 pts | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- region: asia_pacific: 46.2% / 10.9% / 154.3 chars / 0.983 / 92.1% (n=76)
- region: europe: 31.8% / 4.6% / 162.9 chars / 0.99 / 93.0% (n=115)
- region: latin_america: 35.0% / 1.7% / 156.1 chars / 0.991 / 95.3% (n=43)
- region: north_america: 38.2% / 4.7% / 160.4 chars / 0.987 / 93.5% (n=123)

### channel (NOT within 5 points (6.5 pts))

| Segment | Tickets in segment | Resolution rate | Quality score | Variation from best | CI overlaps best | Explanation |
|---|---|---|---|---|---|---|
| channel: chat | 155 | 76.8% (69.5% to 82.7%) | 78.1% (70.9% to 83.9%) | 1.2 pts | yes |  |
| channel: docs_comment | 78 | 76.9% (66.4% to 84.9%) | 73.1% (62.3% to 81.7%) | 6.2 pts | yes |  |
| channel: email | 212 | 77.8% (71.8% to 82.9%) | 79.2% (73.3% to 84.2%) | best | yes |  |
| channel: forum | 55 | 78.2% (65.6% to 87.1%) | 72.7% (59.8% to 82.7%) | 6.5 pts | yes |  |

Facts for the explanation: share labelled escalate / share with no passage above threshold / mean length / mean confidence / retrieval hit rate

- channel: chat: 32.3% / 7.7% / 143.1 chars / 0.974 / 90.8% (n=119)
- channel: docs_comment: 47.4% / 5.1% / 161.8 chars / 0.992 / 93.8% (n=48)
- channel: email: 37.3% / 4.7% / 166.5 chars / 0.995 / 94.1% (n=153)
- channel: forum: 41.8% / 5.5% / 172.3 chars / 0.99 / 97.3% (n=37)
