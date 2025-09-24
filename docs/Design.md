
# Design & Requirements (POC)

## Goal
Enable a human user to provide a single introduction (family + child + target schools) and coordinate multiple AI roles in a realistic,
non‑rigid conversation. After several rounds, the Writer aggregates all evidence into a professional strategy document for top private
school application preparation.

## Roles
- Admissions Officer — asks 1–2 high‑leverage questions, offers micro‑assessment.
- Parent — answers in a parent's voice with concrete evidence.
- Student — answers as the child, with specific examples and reflection.
- Advisor — converts signals into an actionable plan (owner/due/evidence).
- Writer — silent; produces structured Markdown at the end.

## Routing
- Prioritize: Admissions asks → Parent/Student answer → Advisor plans → Writer (final only).
- If nobody can answer confidently → ask user for missing info (asks_to_user).
- Stop when: rounds reached OR info gaps are resolved.

## Output
- Logs under `logs/`
- Final report: `logs/final_report.md`

## Extensibility
- Replace stubs with provider calls (OpenAI/Azure/Anthropic).
- Add Slack/Discord adapters for multi‑bot live demo later.
