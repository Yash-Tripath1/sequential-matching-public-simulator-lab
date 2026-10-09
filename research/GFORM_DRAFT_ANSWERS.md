# Google Form — draft answer material

Drafts for review, not a signed submission. Edit to fit field limits and confirm all declarations. The research note and repository are explicitly about public synthetic-simulator work.

## Brief summary of approach

We study how a limited clarification budget affects sequential matching under reciprocal hard constraints. At each decision day, a heuristic prioritizes available people whose unknown hard constraints may be blocking promising edges. After clarification, known hard constraints remain absolute gates; among feasible pairs, we compare the starter greedy matcher with a general-graph maximum-weight matcher using observed soft-field similarities. The primary experiment crosses default versus potential-ask clarification with greedy versus max-weight matching, alongside no-ask and random-feasible controls, over six public synthetic scenario families and ten matched seeds per family. Results suggest a positive average effect for targeted hard-constraint asks but an uncertain matcher effect; the ask effect reverses in cold start. A separate soft-question holdout shows no reliable gain. Results are exploratory and are not private-evaluation or real-world evidence.

## Key papers / references considered

- Karp, R. M., Vazirani, U. V., & Vazirani, V. V. (1990). “An Optimal Algorithm for On-line Bipartite Matching.” *STOC ’90*, 352–358. DOI: 10.1145/100216.100262. Foundational online-matching context; its bipartite model is not the simulator’s general-graph setting. https://dl.acm.org/doi/10.1145/100216.100262
- Gamlath, B., Kapralov, M., Maggiori, A., Svensson, O., & Wajc, D. (2019). “Online Matching with General Arrivals.” *FOCS 2019*, 26–37. DOI: 10.1109/FOCS.2019.00011. More relevant background on online matching under general arrival models. https://www.computer.org/csdl/proceedings-article/focs/2019/495200a026/1grNEXYNGZW
- Saar-Tsechansky, M., Melville, P., & Provost, F. (2009). “Active Feature-Value Acquisition.” *Management Science*, 55(4), 664–684. DOI: 10.1287/mnsc.1080.0952. Motivates cost-aware information acquisition as an analogy; it is not a direct matching algorithm. https://dl.acm.org/doi/10.1287/mnsc.1080.0952
- Organizer starter kit, release 1.0.0, bundled at upstream commit `a8e26b35118cfa8e886a02f93984923e43ab64f6`; see `starter/SOURCE.md`, `starter/LICENSE`, and `starter/DATA_LICENSE.md`.

## Proposed methods / algorithms

The policy runs a clarification phase followed by a matching phase. The potential-ask heuristic ranks currently available members by the number of plausible candidate edges whose hard feasibility may be blocked by unknown constraints, then uses the simulator’s daily ask budget. It is a heuristic, not an exact expected-value-of-information calculation. Known reciprocal hard constraints remain non-negotiable gates. For the matching ablation, the system compares the starter greedy matcher with maximum-weight matching on the currently feasible general graph, using observed agreement across seven soft fields as edge weights. No policy reads hidden simulator truth. Soft-field questions are reported as a secondary exploratory ablation, not as the core claim.

## Evaluation plan: baselines, metrics, comparisons

Use the supplied greedy-with-default-asks, no-clarification greedy, and random-feasible policies as controls. The primary ablation crosses default versus potential-ask clarification with greedy versus general-graph max-weight matching. The core public screen includes ten matched seeds in each of six scenario families: 60 public worlds and 360 policy–world rows. The primary metric is MSMI per 100 arrived members, averaging the six scenario-family means equally. Compare methods on matched worlds; report seed-block bootstrap 95% intervals, exact seed-block sign-flip tests, and every scenario family. Tests are exploratory and unadjusted for multiple comparisons. Coverage, assignments, mutual acceptances, dates, ask cost, and missing feedback are secondary descriptive measures. A separate three-seed soft-question screen and seven-seed public holdout are secondary; the holdout estimate is +0.024 MSMI/100 (95% CI [−0.071, +0.131], exact sign-flip p = 0.844), which does not establish a reliable gain. No private evaluation, Docker evaluation, or real-user test has been performed.

## Optional GitHub / supporting-material link

Repository: https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab

After the update is pushed, add the immutable commit URL or commit SHA here: **[replace with the new commit SHA after push]**. Do not claim the attached ZIP itself has been pushed.

## Optional additional information

All experiments and results in this package use the public synthetic simulator. They should not be interpreted as predictions about real people or proof of product effectiveness. The primary ten-seed factorial shows scenario heterogeneity, including a cold-start reversal; the soft-question pilot uplift did not replicate convincingly in its seven-seed public holdout. In-process runtimes are not official per-invocation or Docker runtimes. The row-level JSON for the user-VM soft-question screen/holdout was not available in the bundle; aggregate figures are documented and explicitly identified as such.

## Declaration — verify before signing

Suggested disclosure wording, to be edited to match the actual team and the form’s exact requirements:

> We used the organizers’ public synthetic simulator and bundled starter kit (release 1.0.0; provenance and license details are in the repository), along with the cited papers and listed Python dependencies. AI assistance from Arena.ai Agent Mode was used for experiment/code debugging, analysis, and drafting/review support. The team reviewed the methods, results, code, and final submission. No private evaluation data or real-user data were used.

Before submitting, list any additional AI tools, external code, datasets, libraries, or contributors actually used, and remove anything that is not accurate. The team must verify and sign its own declaration.
