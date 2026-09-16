# Run summary

- Input: `Docs/Capstone_Project/05_Datasets/development_tickets.json`; tickets: 20; started: 2026-09-16T04:53:11.486266+00:00; duration: 207.1s
- System version: 2576f80; thresholds: confidence 0.8, retrieval 0.4; run count on this input: 1

## Volume
processed 20, auto-responded 12, escalated 5, blocked 3

## Business
- First contact resolution: 60.0% (95% CI 38.7% to 78.1%)
- Escalation rate: 40.0% (95% CI 21.9% to 61.3%)
- Response time: mean 9903 ms, median 9907 ms

## Technical
- Intent macro precision 100.0%, macro recall 100.0%, accuracy 100.0% over 20 labelled tickets
- Retrieval hit rate 93.3% (n=15); routing accuracy 75.0%
- Citations resolve to retrieved passages 100.0%; cite the expected article 75.0%
- Latency median 9907 ms, p95 20377 ms

## Governance
- Decisions logged 20, failed tickets 0, guardrail blocks {'grounding': 3}
- Private data detections 0, must-not-auto-respond violations 0
- Calibration ECE 0.0037433155080213165, all bins within 5 points: True

## Segment variation in routing accuracy (percentage points)
- tier: 44.4
- region: 80.0
- fluency: 11.9
- ticket_length: 27.8
- channel: 50.0
