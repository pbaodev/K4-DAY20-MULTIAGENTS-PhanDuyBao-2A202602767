---
name: structured-log-exports
description: Use when parsing logs into structured JSON summaries or error records.
---
1. Inspect the required output schema and preserve all required top-level fields and metadata.
2. Normalize service names to lowercase and replace hyphens with underscores when required.
3. Normalize timestamps to the specified timezone and representation before comparing or sorting them.
4. Sort error records by service, then by normalized timestamp, in ascending order when required.
5. Validate schema fields, normalization, ordering, and parsed record counts in the written output.
