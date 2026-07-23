# Simulated Peer Review — Round 1

> Skill: `academic-paper-reviewer` (full, 5 reviewers). Manuscript: `paper/main.tex` + `paper/sections/*.tex`.
> Target venue: Biomedical Signal Processing and Control (BSPC, Elsevier). Date: 2026-07-22.
> Evidence base: manuscript prose + `results/` CSVs + `docs/RESULTS.md`. Reviewer numbers verified against data where cited.

## Phase 0 — Field analysis & reviewer configuration

- **Primary field:** medical image analysis / unsupervised segmentation. **Secondary:** optimization / evaluation methodology.
- **Paradigm:** empirical benchmark + measurement study with a constructive tool. **Maturity:** complete data pipeline, full draft.
- **Panel:** EIC (BSPC associate editor, image-based biomedical signal processing); R1 methodology (segmentation evaluation & statistics); R2 domain (multilevel thresholding / metaheuristics); R3 perspective (clinical ML translation); R4 Devil's Advocate (core-argument challenger).

---

## R0 — Editor-in-Chief

**Fit & significance.** The paper sits squarely in BSPC's scope (thresholding on medical images) but arrives as a *reality-check + tool* rather than a new method. The neutral, benchmark-shaped title and contribution-first abstract are the right choices; an accusatory frame would have drawn a hostile associate editor from the very community that supplies reviewers. Significance is real: the single thesis is clean, and the ceiling decomposition answers a "why" that the cited ceiling paper (François & Tinarrage) only asserts.

**Concern.** BSPC readers expect an actionable method. The constructive legs (O(L log L) diagnostic, protocol checklist, single-parameter baseline) must be foregrounded so the paper does not read as pure critique. The deferred coded survey (Table I) leaves the "audit" leg partly promissory.

**Recommendation:** Major Revision. The science is sound; the presentation of the central result and two rigor gaps need work.

---

## R1 — Methodology reviewer

**Strengths.** Exemplary on the axes this community usually neglects: an *exact* global optimum as reference (not mutual ranking), an asserted equal NFE budget with a hard gate, patient-level splits with leakage control, TOST + Bayesian ROPE for equivalence, bootstrap CIs, a preregistered analysis protocol, and one-to-one provenance from every table to a script and commit. Failed predictions (P2c, P3-secondary) are reported rather than buried.

**MAJOR-1 — the central equivalence is shown at one operating point only.** Section V-B reports median Dice difference of zero at the primary point (`brightest`, k=4). But at that point the *absolute* Dice is modest, and a skeptical reader will ask whether methods are equivalent because the gap does not project, or merely because that decoding discards the signal so every method is equally poor. **This is answerable from the existing data and the answer favors the authors:** at `morph` decoding (WT/FLAIR, k=4), where DP-exact median Dice is 0.82, the median metaheuristic−DP difference is still ≤ 0.003 across all nine methods (< the 0.01 SESOI). The equivalence therefore holds where the mask is *good*, not only where it is poor. This must be added — it converts the strongest objection into a robustness result. *(Verified: `results/main/raw.csv`, per-operating-point.)*

**MAJOR-2 — Table 3's headline Dice (0.16) is a pooled-over-targets artifact.** The main-grid table reports DP-exact Dice ≈ 0.165 at k=4/`brightest`, a value pooled across WT/FLAIR and the much harder ET/T1ce, which drags the median down. Per target the numbers are far more informative and less alarming: WT/FLAIR `brightest` = 0.73, `morph` = 0.82. Report per target; a reader who sees 0.16 will assume the whole pipeline failed. *(Verified from data.)*

**MAJOR-3 — the ceiling decomposition rests on a single U-Net seed.** The headline +0.050 Dice gain over the intensity oracle has no across-seed variance, while the metaheuristic grid runs five seeds. Either add ≥2 more U-Net seeds (the config already supports it; ~2 GPU sessions) or state prominently that the learned rung is single-seed and bound the risk (the per-fold consistency, 0.9185–0.9289, is reassuring but is not seed variance).

**MINOR.** (a) The P2c positive correlation (ρ 0.30–0.77) sits in mild tension with "the gap does not project"; the reconciliation (equivalence survives even where fitness is informative) is correct but should be stated at the point of tension, not only in §V-A. (b) Report `zero_method='pratt'` tie handling and n_zero/n_total in the equivalence table caption, as the protocol promises.

---

## R2 — Domain reviewer

**Strengths.** Near-rival positioning is unusually careful and honest: Menotti (exact solver, credited, not claimed), Hammouche (metaheuristics-vs-optimum, credited for priority), François & Tinarrage (ceiling, explicitly not restated as ours), Lipton/RankSEG (level-set theorem, application only), Hegazy & Gabr (same seam, cited for priority). This is the strongest part of the paper for a domain reader.

**MAJOR-4 — the audit leg is currently qualitative.** The claim that the literature leaves the decoding map unstated is presented as an unquantified observation, with the coded two-coder survey (Table I) deferred. That is honest, but it leaves the paper's "audit" identity half-supported: a domain reviewer wants at least a small coded sample with Cohen's κ, or the audit framing should be softened to "measurement + tool" with the survey named as future work. Decide which paper this is.

**MINOR.** The Al-Najdawi citation now supports the setup weakly — its dataset is TCIA COVID-19-AR (chest), not brain, and its full text was not accessible for verification. Keep it for "the field ranks optimizers on medical images by surrogate/cost," but do not lean on it; a brain-MRI thresholding example would be stronger if one can be verified.

---

## R3 — Perspective reviewer

**Strengths.** The O(L log L) diagnostic is genuinely portable and has impact beyond this paper: any author can bound their method family before writing an optimizer. The Goodhart-on-k framing connects to a broad ML-evaluation concern and gives the paper reach. The "so what" is answered: practitioners should stop optimizing thresholds where the ceiling is far from the requirement (ET, 0.635) and should report the ceiling first.

**Challenge.** State once, explicitly, whether the decomposition generalizes beyond Kapur/BraTS or is a case study; the current bounding is good but a reader wants the scope sentence in the abstract-adjacent text, not only in Threats.

**MINOR.** §VII (quantum-inspired) now reports only the grid-level placement of QIGOA and defers the component ablation. This is honest given it was not run, but a reader drawn by "quantum-inspired" in the title/keywords may feel under-served. Consider removing quantum-inspired from the keywords if the component is not dissected, to set expectations.

---

## R4 — Devil's Advocate

**Strongest counter-argument.** "The paper's whole thesis — the optimization gap does not project onto the clinical mask — could be an artifact of the chosen primary decoding. If `brightest` at k=4 collapses the mask so that every threshold vector scores about the same, then 'equivalence to the exact optimum' is trivially true and says nothing about optimization; it says the decoder is lossy. The paper must exclude this before the thesis stands."

**Resolution (in the authors' favor, but only once shown).** The counter-argument is defused by the data the authors already hold: equivalence to the exact optimum persists at `morph` decoding where median Dice is 0.82, i.e. where the mask is clinically usable. Until §V-B reports this, the objection is live and a competent reviewer will raise it. **This is the single most important revision.** (Not CRITICAL, because the data resolve it; MAJOR, because the manuscript does not yet show it.)

**Other challenges.**
- *Cherry-picking check:* passes — failed predictions are reported (P2c, P3 secondary, empty-mask non-effect).
- *Confirmation bias:* strongly mitigated by preregistration and the immortal-on-both-branches thesis structure.
- *Overgeneralization:* the title verb ("optimizing the wrong variable") is stronger than the bounded claim; the neutral submission title and the Threats scoping fix this, but ensure no sentence in the body generalizes beyond additive criteria / intensity-only decoders.
- *Class B vs Class C:* the U-Net (out-of-fold) vs oracle (test-time GT) comparison is framed as information decomposition, not a fair benchmark. Correct — but add one sentence noting that `morph` decoding (no learning, no test-time GT) *also* exceeds the intensity oracle (0.894 > 0.853), so the "information is in the pixels" conclusion does not depend on the learned model alone.

**No CRITICAL issues.**

---

## Phase 2 — Editorial decision

**Decision: MAJOR REVISION.**

Consensus across the panel: the methodology is rigorous and honest, the contributions are real, and the near-rival positioning is exemplary. No reviewer found a fatal flaw or an integrity problem. The decision is Major (not Minor) because the central result's presentation has a gap that a competent reviewer will attack (MAJOR-1 / DA), and two rigor items (per-target reporting, single-seed U-Net) need attention.

### Revision roadmap (priority order)

1. **[MAJOR-1 / DA — do first]** Report the metaheuristic-vs-exact equivalence across decoding rules, foregrounding `morph` (median Dice 0.82) so the thesis is shown to hold where the mask is good, not only at `brightest`. Data already exist; add a row/panel and one paragraph. *This is the load-bearing revision.*
2. **[MAJOR-2]** Replace the pooled Table 3 Dice with per-target values (WT/FLAIR and ET/T1ce separately); annotate that the pooled 0.16 was target-mixed.
3. **[MAJOR-3]** Add ≥2 U-Net seeds for a variance band on the +0.050 decomposition, or state the single-seed limitation prominently with the per-fold spread as partial evidence.
4. **[MAJOR-4]** Decide the paper's identity: run a small coded survey with κ to support the audit leg, or soften "audit" to "measurement + tool + protocol" and name the survey as future work.
5. **[MINOR]** (a) Move the P2c reconciliation to the point of tension. (b) Report Pratt ties + n_zero in the equivalence caption. (c) Add the "morph also beats the intensity oracle" sentence to §VIII. (d) De-emphasize Al-Najdawi; consider dropping "quantum-inspired" from keywords. (e) Clear the 2 remaining `[VERIFY]` bib comments (demsar/benavoli volume/pages).

### What is explicitly fine (do not change)
- The reframe holds. Honest negative + working tool is a publishable BSPC contribution.
- Red lines are respected: no quantum-advantage claim, no "we establish the ceiling," theorems credited to Menotti and Lipton, ceiling credited to François & Tinarrage.
- Provenance discipline and preregistration are strengths — keep them visible.
