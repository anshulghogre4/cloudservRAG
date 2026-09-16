# Run summary

- Input: `Docs/Capstone_Project/05_Datasets/development_tickets.json`; tickets: 500; started: 2026-09-16T05:04:22.830328+00:00; duration: 2589.0s
- System version: 2576f80; thresholds: confidence 0.8, retrieval 0.4; run count on this input: 1

## Volume
processed 500, auto-responded 356, escalated 101, blocked 43

## Business
- First contact resolution: 71.2% (95% CI 67.1% to 75.0%)
- Escalation rate: 28.8% (95% CI 25.0% to 32.9%)
- Response time: mean 5160 ms, median 2374 ms

## Technical
- Intent macro precision 100.0%, macro recall 100.0%, accuracy 100.0% over 500 labelled tickets
- Retrieval hit rate 93.3% (n=357); routing accuracy 73.8%
- Citations resolve to retrieved passages 100.0%; cite the expected article 72.2%
- Latency median 2374 ms, p95 16769 ms

## Governance
- Decisions logged 500, failed tickets 0, guardrail blocks {'grounding': 43}
- Private data detections 0, must-not-auto-respond violations 0
- Calibration ECE 0.005369986631022759, all bins within 5 points: False

## Segment variation in routing accuracy (percentage points)
- tier: 6.7
- region: 7.0
- fluency: 1.7
- ticket_length: 8.7
- channel: 11.3
