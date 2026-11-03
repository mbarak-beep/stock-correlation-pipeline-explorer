# Coding Agent Instructions

- Keep ingestion, numerical computation, storage, and UI separated.
- Prefer simple, typed, testable Python.
- Avoid nested Python loops for dense numerical calculations.
- Use NumPy vectorization where appropriate.
- Be explicit about the 20-trading-day rolling correlation definition.
- Validate input assumptions.
- Test numerical correctness and storage round trips.
- Do not use blanket exception handling.
- Optimize only after measuring.
