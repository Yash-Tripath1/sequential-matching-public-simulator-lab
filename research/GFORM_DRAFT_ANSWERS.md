# Google Form — Round 1 answers (aligned to the submitted Round 1 PDF)

Drafts aligned to the thesis of `research/RESEARCH_NOTE_ROUND1.pdf`. Edit to fit field
limits and confirm all declarations before submitting. Everything below is public
synthetic-simulator work; no private seeds, private evaluation, Docker assessment, or
real-user evidence of any kind.

## Brief summary of approach

We separate normalisation, modelling and allocation, and study where the attainable score
in this simulator actually comes from. A structural diagnosis of the generated worlds
shows the reciprocal hard-constraint graph is thin (mean degree 2.53 in development, 33.9%
of members with no feasible partner, 31.9% permanently decline-blocked), which yields
per-family coverage ceilings (0.399 development, 0.341 cold start, 0.178 sparse). An
oracle ladder (analysis-only) shows that even free, perfect clarification plus
maximum-cardinality allocation moves coverage by ~0.001 and MSMI not at all. Our matched
17-configuration factorial on 10 public seeds × 6 families (1,020 episodes) then shows:
(1) asking vs not-asking is the robust lever — every one of 16 asking-vs-no-ask contrasts
has a 95% seed-block CI excluding zero, from +0.183 for the unmodified starter baseline to
+0.425 for our best cell; (2) targeted clarification is not supported (H1) — unlock-value
ranking gives differences of −0.083 to +0.008 vs simpler ask rules, all CIs straddling
zero, and reverses in cold start; (3) within competent asking policies, weight coding plus
global blossom matching is worth ~+0.133 combined vs starter greedy (neither half
individually significant at 10 seeds); (4) a calibrated fitted prior used as edge weight
is consistently worse than hand-coded weights, consistent with a weight-scale mechanism;
(5) residual-budget soft asks and online adaptation on dense directional responses both
produce no measurable gain. The score is supply-determined, not ranking-determined; the
productive levers for Round 2 are waiting/batching and pair selectivity, not further
targeting.

## Key papers / references considered

- Akbarpour, M., Li, S., & Oveis Gharan, S. (2020). "Thickness and Information in Dynamic
  Matching Markets." Journal of Political Economy, 128(3), 783–815. DOI 10.1086/704761.
  Waiting pays when departures are identifiable; motivates the planned batching ablation.
- Edmonds, J. (1965). "Paths, Trees, and Flowers." Canadian Journal of Mathematics, 17(3),
  449–467. DOI 10.4153/CJM-1965-045-4. The blossom algorithm for general-graph matching —
  the feasible graph is not bipartite, so Hungarian assignment does not apply.
- Dudík, M., Langford, J., & Li, L. (2011). "Doubly Robust Policy Evaluation and
  Learning." ICML '11, 1097–1104. Planned off-policy evaluation on our own randomised logs.
- Russo, D., Van Roy, B., Kazerouni, A., Osband, I., & Wen, Z. (2018). "A Tutorial on
  Thompson Sampling." Foundations and Trends in Machine Learning, 11(1). Background for the
  label-starvation argument (≈0.87 MSMI events per episode).
- Hitsch, G. J., Hortaçsu, A., & Ariely, D. (2010). "Matching and Sorting in Online
  Dating." American Economic Review, 100(1), 130–163. DOI 10.1257/aer.100.1.130.
- Vouchsafe / Romeo & Juliet (2026). The One Introduction Problem — final participant
  specification 1.0.0, with docs/DATA_CONTRACT.md, POLICY_INTERFACE.md, SUBMISSION.md.
  Authoritative for every rule quoted in the note.
- Organizer starter kit release 1.0.0 (bundled unchanged under `starter/` with its MIT
  licence and source-commit metadata).

## Proposed methods / algorithms

Three separated components, each independently ablatable. (1) Clarification: unlock-value
rule scoring members by expected matching-unlock value — a product of empirical
hard-constraint pass-probability marginals (estimated only from the six supplied training
pools) and a reduced-profit term using yesterday's matching weights; declined fields are
never re-asked or imputed; a residual-budget variant converts spare daily units into
1-unit soft-field answers. (2) Pair weighting: three variants — 7-soft agreement count,
signed core-4 coding (+1/−1/0 with the fitted intercept absorbing "unknown"), and a small
ridge-logistic prior fit on 7,613 labelled introductions from our own randomised logging
rollouts (108 episodes, 18 declared training seeds disjoint from the 10 evaluation seeds),
targeting P(mutual acceptance | both responded within 7 days), held-out AUC 0.598, with
calibration table in the note. (3) Allocation: general-graph maximum-weight matching
(networkx blossom), never bipartite/Hungarian; hard feasibility gates every method; no
policy reads hidden simulator state. An audit ledger records per-pair evidence, unresolved
fields and rejection reasons.

## Evaluation plan: baselines, metrics, comparisons

Same-world matched comparisons over 10 public seeds × 6 scenario families. Required
baselines: supplied greedy with default asks, no-clarification greedy, and
random-feasible — verified action-for-action against the organisers' reference policy.py
on seeds 101–606 across all six families. Statistics: primary score = unweighted mean of
six family means of MSMI/100; 95% CIs by percentile bootstrap over the ten seed blocks
(10,000 draws); exact two-sided sign-flip tests on seed-block differences; W/T/L over all
60 paired episodes; no multiplicity correction (stated). Headline numbers from the Round 1
note: pre-specified incumbent vs official greedy +0.175 MSMI/100 (95% CI [+0.092, +0.258],
p = 0.016, W/T/L 23/29/8); asking vs no-asking +0.183 (CI [+0.042, +0.325]) with all 16
asking-vs-no-ask contrasts excluding zero; targeted-ask H1 not supported; best screened
cell 0.592 flagged as winner's-cursed and needing fresh seeds. Failure analysis covers
sparse supply (structural, not policy failure), declined answers (31.9–41% permanently
excluded), cold start (where targeting reverses, with a named shrinkage fix), delayed
feedback/right-censoring, and candidate competition. Caveats in every table: public seeds
only, in-process timing, unadjusted p-values, fully synthetic outcomes.

## Optional GitHub / supporting-material link

Repository: https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab
(contains the Round 1 PDF at `research/RESEARCH_NOTE_ROUND1.pdf`, the artifact-status map
at `research/ROUND1_NOTE.md`, and all prior-phase artifacts).

## Optional additional information

The Round 1 note reports several negative results on purpose: H1 (targeted clarification)
not supported; H3 (online adaptation on dense directional responses) falsified — decisions
bit-identical to its static version in all 60 episodes; H5 (residual soft asks) null with
~390 extra ask units for +0.017 (CI straddling 0). An internal audit found and corrected a
30-day date-deadline defect in an earlier label helper (no reported score was affected;
documented in note §7.5). The new-harness scripts and Round 1 result artifacts listed in
`research/ROUND1_NOTE.md` are being mirrored into the repository; the ⏳ rows there are the
authoritative pending list. Nothing here estimates relationship compatibility for real
people, and no result is evidence of product effectiveness.

## Declaration — verify before signing

Suggested disclosure wording, to be edited to match the actual team and the form's exact
requirements:

> We used the organisers' public synthetic simulator and bundled starter kit (release
> 1.0.0; provenance and licence details in the repository), along with the cited papers
> and listed Python dependencies. AI assistance from Arena.ai Agent Mode was used for
> experiment/code development, analysis, and drafting/review support; one model-assisted
> implementation contained the label-cutoff defect disclosed in the note, found by
> human-directed audit. The team reviewed the methods, results, code and final
> submission. No private evaluation data or real-user data were used.

Before submitting: list any additional AI tools, external code, datasets, libraries or
contributors actually used; remove anything inaccurate; the team must verify and sign its
own declaration.

## Final submission steps (not part of the form text)

1. Push the repository update (Round 1 PDF, ROUND1_NOTE.md, reconciled docs; then the
   pending scripts/assets/results from the working machine) and record the resulting
   40-character commit SHA.
2. In the form's link field, use the repository URL above; if pinning a commit, use
   `https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab/commit/`
   followed by that SHA. A revision received before the deadline replaces an earlier one,
   so pinning can be done as a form revision immediately after the push.
3. Confirm the PDF carries the team name/author line and declaration, upload it, and keep
   the form receipt timestamp.
