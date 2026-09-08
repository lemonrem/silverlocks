# Active CSV repair

## Requested outcome
Repair CSV export so quoted commas, embedded newlines and escaped quotes remain within their fields. No deployment or commit requested.

## Verified progress
Prior investigation reproduced wrong columns/rows in the current parser. The causal boundary is known: splitlines and comma splitting do not respect CSV quoting. No implementation change has been made.

## Current state
The user has reported that the defect remains. Implementation and post-fix verification are pending. Existing source and tests are authoritative.
