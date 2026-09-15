# Run summary

- Input: `Docs/Capstone_Project/05_Datasets/development_tickets.json`; tickets: 500; started: 2026-09-15T19:12:47.114972+00:00; duration: 0.9s
- System version: 39bf9c5; thresholds: confidence 0.8, retrieval 0.4; run count on this input: 1

## Volume
processed 500, auto-responded 310, escalated 190, blocked 0

## Business
- First contact resolution: 62.0% (95% CI 57.7% to 66.1%)
- Escalation rate: 38.0% (95% CI 33.9% to 42.3%)
- Response time: mean 12 ms, median 12 ms

## Technical
- Intent macro precision 99.7%, macro recall 99.7%, accuracy 99.8% over 500 labelled tickets
- Retrieval hit rate 99.7% (n=357); routing accuracy 99.8%
- Citations resolve to retrieved passages 100.0%; cite the expected article 100.0%
- Latency median 12 ms, p95 12 ms

## Governance
- Decisions logged 500, failed tickets 1, guardrail blocks {}
- Private data detections 0, must-not-auto-respond violations 0
- Calibration ECE 0.3265999999999993, all bins within 5 points: False

## Segment variation in routing accuracy (percentage points)
- tier: 0.6
- region: 0.7
- fluency: 0.3
- ticket_length: 0.2
- channel: 1.3
