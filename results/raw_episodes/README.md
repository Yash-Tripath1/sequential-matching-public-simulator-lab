# Raw per-episode results

Every file is newline-delimited JSON, gzip-compressed, one record per episode.
Records carry `seed`, `variant`, `arm`, `seconds`, `metrics`, `waits`,
`askable_by_day`, `asks_by_day` and a per-member `members` array. Successful
episodes have no `valid` key; a failed episode carries `valid: false` plus an
`error`. Filter with `if r.get('valid') is False or not r.get('metrics'): continue`.

`members.jsonl` is deliberately not committed: the harness regenerates it from
`episodes.jsonl` at the end of every run, so it is derived data.

## Coverage

| arm | seeds | episodes | file(s) |
|---|---|---|---|
| `greedy` | 1101–1220 (120) | 720 | `greedy_potential_ask_1131-1220_chunk*` + `greedy_1101-1130` |
| `no_ask` (no clarification) | 1101–1220 (120) | 720 | `no_ask_random_feasible_*.chunk*` |
| `random_feasible` | 1101–1220 (120) | 720 | `no_ask_random_feasible_*.chunk*` |
| `potential_ask` | 1131–1220 (90) | 540 | `greedy_potential_ask_1131-1220_chunk*` |
| `potential_ask_greedy` | 1101–1220 (120) | 720 | `potential_ask_greedy_1101-1130` + `..._chunk*` |
| `disagreement_aware` | 1101–1220 (120) | 720 | `disagreement_aware_1101-1130` + `..._chunk*` |

All four arms the rules name, greedy, no-clarification, random-feasible and our
candidate, therefore have full raw coverage on the same 120 seeds.

## Not available

`oldest_first` raw rows were produced on a separate machine whose per-episode
log could not be recovered; only its aggregate in `../primary_120seeds.json`
survives. It is not one of the four arms the rules name.

**Transcription verified.** The aggregate tables for `greedy` were transcribed
from terminal output on that machine, whose per-episode log was unavailable.
Re-running `greedy` from scratch here reproduces them: **30 of 30** per-seed
primary scores in the 1101–1130 block are identical to the transcribed values
(to 1e-9), on top of the 120-seed aggregate match reported in §5.14. The
transcription is therefore confirmed at the per-seed level, not just in the mean.
