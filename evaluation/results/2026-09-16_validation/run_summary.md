# Run summary

- Input: `Docs/Capstone_Project/05_Datasets/validation_tickets.json`; tickets: 80; started: 2026-09-16T06:13:21.696900+00:00; duration: 460.0s
- System version: ab696a0; thresholds: confidence 0.8, retrieval 0.4; run count on this input: 1

## Volume
processed 80, auto-responded 60, escalated 16, blocked 4

## Business
- First contact resolution: 75.0% (95% CI 64.5% to 83.2%)
- Escalation rate: 25.0% (95% CI 16.8% to 35.5%)
- Response time: mean 5643 ms, median 5967 ms

## Technical
- Intent macro precision 99.1%, macro recall 99.2%, accuracy 98.8% over 80 labelled tickets
- Retrieval hit rate 96.2% (n=53); routing accuracy 75.0%
- Citations resolve to retrieved passages 100.0%; cite the expected article 73.3%
- Latency median 5967 ms, p95 13683 ms

## Governance
- Decisions logged 324, failed tickets 0, guardrail blocks {'grounding': 4}
- Private data detections 0, must-not-auto-respond violations 0
- Calibration ECE 0.012639956550801001, all bins with n >= 20 within 5 points: True
- Decision log reconciliation: complete; 324 rows for 80 tickets; routing rows 80/80, validation rows 80/80

## Segment variation in routing accuracy (percentage points)
- tier: 14.2
- region: 26.5
- fluency: 22.4
- ticket_length: 28.6
- channel: 8.7
