# CLAUDE.md — QIGOA Paper (Paper 3)

> **Tóm tắt cho tác giả (tiếng Việt):** File này là "luật chơi" mà Claude Code tự đọc mỗi phiên.
> Nó ghi bối cảnh paper, các quy tắc **liêm chính học thuật** (KHÔNG bịa số liệu / trích dẫn),
> chuẩn viết IEEE, cách chạy thí nghiệm, và khi nào dùng skill nào. Sửa file này bất cứ lúc nào.

Communicate with the user **in Vietnamese**. Be decisive and push work toward submission
(the author prefers Claude to make well-reasoned decisions rather than ask many questions).
Reference files as clickable `path:line`.

---

## 1. Project

- **Paper 3 — QIGOA:** *Multilevel Image Thresholding for Brain Tumor Segmentation using a
  Quantum-Inspired Grasshopper Optimization Algorithm.*
- **Core idea:** QIGOA = standard GOA (Saremi 2017) + a **3-layer contribution stack** for multilevel
  thresholding with **Kapur's entropy** as the objective:
  1. **Quantum representation** — Q-bit pairs `(α, β)` updated by a quantum rotation gate.
  2. **Adaptive rotation angle** — `θ_i = θ_min + (θ_max − θ_min) × fitness_gap × time_decay`.
  3. **OBL + Lévy** — Opposition-Based Learning at init; Lévy-flight kick when stagnated for
     `stagnation_window` iterations.
- **Novelty framing:** lead with the **3-layer stack**, NOT "we added quantum to GOA" (too thin for
  a Q1 journal). The stack gives reviewers something to credit beyond the swap.
- **Domain:** medical image segmentation — brain tumor MRI, **BraTS** dataset.
- **Author:** Nguyễn Võ Hoàng Long (Long Nguyen Vo Hoang).
- **Target venue (decided 2026-05-19):** ***Biomedical Signal Processing and Control*** (Elsevier,
  Q1, IF ~5.1). NOT IEEE JBHI — the advisor first suggested JBHI, but it was redirected because JBHI
  demands deep-learning SOTA comparison on full BraTS, which thresholding cannot deliver.
- **Current draft:** `Huong-tiep-can-paper-Long.pdf` — an **old 2-page skeleton** with the stale
  IEEE JBHI header and a thinner method. **Its results are PLACEHOLDER / illustrative** ("Your Name",
  the PSNR & CPU table). Treat every number in it as unverified; the plan above supersedes it.
- **Code status:** the `qigoa/` implementation (`src/algorithms/` 7 optimizers, `notebooks/qigoa_kaggle.ipynb`)
  was **removed from this repo** (git: "Remove QIGOA project files"). If restored, that is the driver.

### Conference → Journal strategy
The author's broader plan is **conference papers that extend into journal papers**. When working here:
- Keep a clear line between what is *conference-level* and what is *journal-level* new content.
- A journal extension must add **substantial** new material over any conference version
  (more baselines, more datasets, deeper analysis, statistical validation, ablations) — not a reprint.
- Sibling projects for context (do not edit from here): `../1-Conference-SNDF` (Quishing/QR, ICTA 2025),
  `../2-Conference-Explainable Federated Learning...` (IEEE FJCAI 2026), `../6-Boundary-Uncertainty Aware U-Net`.

---

## 2. Research integrity — NON-NEGOTIABLE (đọc kỹ)

These override any instinct to "make the paper look finished."

1. **Never fabricate.** Do not invent experimental numbers, table values, p-values, dataset sizes,
   or citations. If a value is not from a real run or a real source, it does not go in the paper.
2. **Every quantitative claim traces to evidence.** A PSNR/SSIM/CPU number must come from a script
   output the author can re-run. Keep the producing code/notebook path next to the result.
3. **Mark unverified content explicitly.** Use `[PLACEHOLDER]`, `[TODO: run experiment]`,
   `[UNVERIFIED]`, or `[GAP]` tags. Never silently promote a placeholder into a stated result.
4. **No hallucinated references.** Every citation must be a real, verifiable work (title + venue +
   year, ideally DOI). If you cannot verify it, flag it — do not add it. Use the `academic-paper`
   citation-check mode and cross-check against Google Scholar / Semantic Scholar / DOI.
5. **Don't overclaim.** "Outperforms state-of-the-art" requires real comparative data **and** a
   statistical test. Otherwise write "preliminary results suggest".
6. **Separate proposed vs measured.** Clearly distinguish the *proposed method* (design) from
   *measured outcomes* (experiments). The draft currently blurs this — fix it.

If asked to write results before experiments exist, produce a **results template with placeholders**
and a list of experiments to run — not fabricated numbers.

---

## 3. Method & experiment rigor (QIGOA specifics)

- **Objective:** Kapur's entropy for multilevel thresholding; state it precisely and consistently.
- **Quantum layer:** Q-bit individual `[α;β]`, rotation gate; justify how the adaptive `θ_i` is
  derived from the fitness gap, and how measurement maps Q-states → discrete thresholds. Watch
  boundary handling. Keep the OBL-init and Lévy-flight-kick logic explicit in the algorithm listing.
- **Dataset:** BraTS 2020/2023 **FLAIR axial slices**; evaluate the binary tumor mask.
- **Threshold levels:** `k ∈ {2, 3, 4, 5}`.
- **Search settings:** population = 30, max iterations = 100, **30 independent runs** per algorithm.
- **Baselines (planned set):** GA, PSO, GOA, **WOA, GWO, MPA**. Cite each properly.
- **Metrics:** PSNR, SSIM, FSIM, **Dice, IoU, sensitivity, specificity**, fitness (Kapur value), CPU time.
- **Statistical validation (required for Q1):** report **mean ± std** over the 30 runs, plus
  **Wilcoxon pairwise + Friedman omnibus + Holm post-hoc**. Single-run tables are not acceptable.
- **Reproducibility:** fix random seeds, log all hyperparameters (pop, max_iter, `c` schedule,
  `θ_min/θ_max`, `stagnation_window`), record the BraTS year/split, and keep the exact notebook.

### Experiment workflow
- Experiments run on **Kaggle** (author's environment); the driver was `notebooks/qigoa_kaggle.ipynb`,
  writing CSVs to `/kaggle/working/results/`. Produce self-contained, Kaggle-runnable code.
- **Immediate next step after a Kaggle run:** fill Methods + Results sections from the generated CSVs.
- Store real outputs in the repo (e.g. `results/`) alongside the code that produced them.

---

## 4. Writing conventions

- **Format:** IEEE. Draft is LaTeX (author uses Overleaf for sibling papers — prefer LaTeX/`.tex`).
- **Language:** formal academic English in the manuscript; Vietnamese when chatting with the author.
- **Structure:** Abstract → Index Terms → Introduction → Related Work → Problem Formulation →
  Proposed Method → Experiments → Results & Discussion → Conclusion → References.
- **Related Work / GAP:** motivate the contribution from a real, cited research gap (use Elicit /
  `deep-research` lit-review). State the gap explicitly and tie each contribution to it.
- Keep terminology and notation consistent (e.g. always "Kapur's entropy", one symbol per concept).

---

## 5. Installed skills — when to use which

Four skills are installed under `.claude/skills/` (from `academic-research-skills`, CC-BY-NC-4.0).
Invoke by describing the task; Claude picks the mode.

| Need | Skill / mode |
|------|--------------|
| Find/verify research GAP, systematic lit review (PRISMA), fact-check | **deep-research** |
| Write/plan/outline paper, revise from reviewer comments, citation-check, draft rebuttal | **academic-paper** |
| Self-review before submission (simulated EIC + peer reviewers, 0–100 rubric) | **academic-paper-reviewer** |
| End-to-end research→write→review→revise with integrity gates | **academic-pipeline** |

`.claude/skills/shared/` holds protocols/schemas the skills load at runtime — **do not delete**.
To reinstall/update, re-clone `github.com/imbad0202/academic-research-skills` and copy the four skill
dirs + `shared/` back into `.claude/skills/`.

**External tools the author has collected** (see memory `reference-research-ai-tools`):
Elicit (research gaps), Consensus (literature search), a Google-Scholar credibility tool.

---

## 6. Working agreement

- Before submission, run the paper through **academic-paper-reviewer** and fix what a real reviewer
  would flag (especially: missing baselines, no statistical test, unverifiable claims).
- Prefer concrete next actions (draft this section, write this experiment) over abstract advice.
- Do not commit or push unless asked. `.claude/skills/` is git-ignored (vendored third-party code).
- When a claim in the draft can't be supported yet, say so plainly and propose how to support it.
