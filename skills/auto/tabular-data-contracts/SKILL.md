---
name: tabular-data-contracts
description: Use when cleaning, deduplicating, analyzing, or exporting tabular data to specified output files.
---
1. Read the task instructions and input documentation; list every required output, field, unit, ordering, and normalization rule.
2. Count input rows before deduplication; apply the specified distinct-record rule and separately track records excluded for missing or invalid values.
3. Parse dates using documented formats and timezone rules; emit the required canonical timestamp representation.
4. Represent monetary amounts in the required unit and type; use integer cents when the contract requires cents.
5. Write every requested artifact, including cleaned data and summary metadata; derive metadata counts using the contract's exact definitions.
6. Validate output headers, field order, row counts, canonical values, and JSON structure against the contract before finishing.
