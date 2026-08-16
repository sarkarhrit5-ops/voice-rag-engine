# Threshold benchmark report

- Sample size: 200 validation queries
- Answerable queries: 101
- No-answer queries: 99
- Best tradeoff threshold: 0.65

| threshold | correct answer | incorrect refusal | correct refusal | incorrect answer | false answer rate | false refusal rate | grounded answer rate | refusal accuracy | precision | recall | f1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.65 | 41 | 60 | 99 | 0 | 0.0000 | 0.5941 | 0.4059 | 1.0000 | 1.0000 | 0.4059 | 0.5775 |
| 0.67 | 41 | 60 | 99 | 0 | 0.0000 | 0.5941 | 0.4059 | 1.0000 | 1.0000 | 0.4059 | 0.5775 |
| 0.69 | 41 | 60 | 99 | 0 | 0.0000 | 0.5941 | 0.4059 | 1.0000 | 1.0000 | 0.4059 | 0.5775 |
| 0.71 | 41 | 60 | 99 | 0 | 0.0000 | 0.5941 | 0.4059 | 1.0000 | 1.0000 | 0.4059 | 0.5775 |
| 0.73 | 41 | 60 | 99 | 0 | 0.0000 | 0.5941 | 0.4059 | 1.0000 | 1.0000 | 0.4059 | 0.5775 |
| 0.75 | 41 | 60 | 99 | 0 | 0.0000 | 0.5941 | 0.4059 | 1.0000 | 1.0000 | 0.4059 | 0.5775 |
| 0.77 | 41 | 60 | 99 | 0 | 0.0000 | 0.5941 | 0.4059 | 1.0000 | 1.0000 | 0.4059 | 0.5775 |
| 0.79 | 41 | 60 | 99 | 0 | 0.0000 | 0.5941 | 0.4059 | 1.0000 | 1.0000 | 0.4059 | 0.5775 |
| 0.81 | 37 | 64 | 99 | 0 | 0.0000 | 0.6337 | 0.3663 | 1.0000 | 1.0000 | 0.3663 | 0.5362 |
| 0.83 | 26 | 75 | 99 | 0 | 0.0000 | 0.7426 | 0.2574 | 1.0000 | 1.0000 | 0.2574 | 0.4094 |
| 0.85 | 15 | 86 | 99 | 0 | 0.0000 | 0.8515 | 0.1485 | 1.0000 | 1.0000 | 0.1485 | 0.2586 |

## Best threshold

The threshold with the strongest F1 tradeoff while minimizing false refusals is 0.65. It achieved grounded-answer rate 0.4059, false-refusal rate 0.5941, and F1 0.5775.

This threshold should be treated as the candidate production guardrail until a live-provider benchmark confirms it under real generation latency and a larger validation sample.
