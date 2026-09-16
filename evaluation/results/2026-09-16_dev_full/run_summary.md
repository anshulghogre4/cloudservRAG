# Run summary

- Input: `Docs/Capstone_Project/05_Datasets/development_tickets.json`; tickets: 500; started: 2026-09-16T06:00:30.339483+00:00; duration: 173.7s
- System version: 2576f80; thresholds: confidence 0.8, retrieval 0.4; run count on this input: 3

## Volume
processed 500, auto-responded 387, escalated 107, blocked 6

## Business
- First contact resolution: 77.4% (95% CI 73.5% to 80.8%)
- Escalation rate: 22.6% (95% CI 19.2% to 26.5%)
- Response time: mean 330 ms, median 347 ms

## Technical
- Intent macro precision 99.2%, macro recall 98.9%, accuracy 99.2% over 500 labelled tickets
- Retrieval hit rate 93.3% (n=357); routing accuracy 77.2%
- Citations resolve to retrieved passages 100.0%; cite the expected article 72.6%
- Latency median 347 ms, p95 529 ms

## Governance
- Decisions logged 2006, failed tickets 0, guardrail blocks {'grounding': 6}
- Private data detections 0, must-not-auto-respond violations 0
- Calibration ECE 0.004738636363642844, all bins with n >= 20 within 5 points: True
- Decision log reconciliation: complete; 2006 rows for 500 tickets; routing rows 500/500, validation rows 500/500

## Segment variation in routing accuracy (percentage points)
- tier: 7.4
- region: 7.5
- fluency: 2.6
- ticket_length: 11.7
- channel: 6.5
