# Optimizing the Wrong Variable: Structural Degeneracy in Multilevel Thresholding for Brain Tumor Segmentation

> **DRAFT v1 — full prose complete: Abstract (EN+VI), I–VII.** Pending: figures/tables (numbers ready
> in `results/`, rendering TODO), bibliography resolution (bibkeys map to `CLAUDE.md §1`), and a polish
> pass (em-dash density, sentence rhythm per skill writing-quality check).
> Every quantitative value traces to `results/` via `docs/RESULTS.md`; do not edit numbers by hand.
> Style: IEEE playbook `docs/lam-va-viet-paper-chuan-IEEE.md` — hard formulation, evaluation as
> refutation, honest positioning, no over-claim.
> Reading order (not file order): Abstract → I → II → III → IV → V → VI → VII.

---

## Abstract

A decade of work has proposed metaheuristic and quantum-inspired optimizers for multilevel
thresholding of brain tumor MRI, reporting gains in the optimizer's own currency — a higher Kapur
objective, a better PSNR, a favorable convergence curve. The benchmark images carry expert masks
that are rarely opened. Opening them inverts the picture. On the full BraTS 2020 cohort ($n=368$),
with the optimization and decoding stages held apart and a complete equivalence-testing protocol,
we show that the objective gap the field competes to close does not project onto the clinical mask.
No metaheuristic clears a 0.99 hit rate against the exact global optimum at any threshold count, and
the hit rate collapses to zero as the number of thresholds grows; yet the resulting per-patient Dice
is statistically equivalent to the exact optimum's (median difference zero; two one-sided tests pass
at a 0.05 margin in all 36 comparisons). The mask is instead set by a decoding stage the literature
treats as an afterthought. Decomposing the achievable ceiling with a 2-D U-Net on identical input, we
locate the residual gap in spatial structure rather than intensity: the learned model exceeds the
intensity-only level-set ceiling by a median 0.050 Dice on whole tumor ($p<10^{-31}$). We give an
$O(L\log L)$ diagnostic that computes this ceiling from the labeled histogram before any optimizer is
written. We claim no quantum advantage, no speed record, and no new ceiling — only the measurement,
the decomposition, and the diagnostic. The field is optimizing the wrong variable.

**Keywords** — multilevel thresholding, brain tumor segmentation, Kapur entropy, metaheuristic
optimization, evaluation methodology, Goodhart's law, Dice ceiling, structural degeneracy.

### Tóm tắt (tiếng Việt)

Suốt một thập kỷ, nhiều nghiên cứu đề xuất các thuật toán metaheuristic và lấy cảm hứng lượng tử để
tối ưu phân ngưỡng đa mức cho ảnh MRI u não, và báo cáo cải thiện bằng chính đơn vị của bộ tối ưu —
giá trị Kapur cao hơn, PSNR tốt hơn, đường hội tụ đẹp hơn. Nhưng các ảnh benchmark đều kèm mask
chuyên gia mà gần như không bài nào mở ra. Mở ra thì kết quả đảo chiều. Trên toàn bộ cohort BraTS
2020 ($n=368$), với hai tầng tối ưu và giải mã tách bạch cùng một giao thức kiểm định tương đương đầy
đủ, chúng tôi cho thấy khoảng cách tối ưu mà cả dòng văn liệu tranh nhau thu hẹp **không chiếu xuống
mask lâm sàng**. Không thuật toán nào đạt hit-rate 0,99 so với tối ưu toàn cục chính xác ở bất kỳ số
ngưỡng nào, và hit-rate sụp về 0 khi số ngưỡng tăng; thế nhưng Dice theo từng bệnh nhân lại tương
đương thống kê với nghiệm tối ưu chính xác (chênh lệch trung vị bằng 0; TOST đạt ở biên 0,05 trên cả
36 so sánh). Mask thực ra được quyết định ở tầng giải mã mà văn liệu xem là thứ yếu. Phân rã trần khả
đạt bằng một U-Net 2D trên cùng đầu vào, chúng tôi định vị phần gap còn lại nằm ở cấu trúc không gian
chứ không ở cường độ: mô hình học vượt trần chỉ-cường-độ trung vị 0,050 Dice trên u toàn phần
($p<10^{-31}$). Chúng tôi đưa ra một công cụ chẩn đoán $O(L\log L)$ tính trần này từ histogram có nhãn
trước khi viết bất kỳ bộ tối ưu nào. Bài không tuyên bố lợi thế lượng tử, không tuyên bố kỷ lục tốc
độ, và không tuyên bố xác lập trần — chỉ đóng góp phép đo, phép phân rã, và công cụ chẩn đoán.

**Từ khoá** — phân ngưỡng đa mức, phân đoạn u não, entropy Kapur, tối ưu metaheuristic, phương pháp
đánh giá, định luật Goodhart, trần Dice, suy biến cấu trúc.

---

## III. Problem Formulation

### A. Multilevel thresholding and the objective under study

Let $I:\Omega\to\{0,1,\dots,L-1\}$ be a single-channel image on a pixel grid $\Omega$, with $L=256$ intensity levels and normalized histogram $h(\ell)=|\{x\in\Omega: I(x)=\ell\}|/|\Omega|$. A $k$-class multilevel thresholding is a set of $k-1$ ordered thresholds
$$
\mathbf{t}=(t_1,\dots,t_{k-1}),\qquad 0<t_1<t_2<\cdots<t_{k-1}<L,
$$
partitioning the intensity range into $k$ contiguous bands $C_1,\dots,C_k$. The literature this paper examines optimizes $\mathbf{t}$ to maximize the Kapur entropy criterion
$$
F_{\text{Kapur}}(\mathbf{t})=\sum_{j=1}^{k} H_j,\qquad
H_j=-\sum_{\ell\in C_j}\frac{h(\ell)}{\omega_j}\ln\frac{h(\ell)}{\omega_j},\quad
\omega_j=\sum_{\ell\in C_j}h(\ell).
$$
$F_{\text{Kapur}}$ is a separable function of the histogram alone. Its exact global maximizer is computable in $O\!\big((k-1)L^2\big)$ by dynamic programming [Menotti2015]; we use that maximizer, denoted $\mathbf{t}^\star$ with value $F^\star=F_{\text{Kapur}}(\mathbf{t}^\star)$, purely as a *reference optimum*, not as a contribution.

### B. The two-stage pipeline, made explicit

Every method in this family produces a segmentation through two stages that the literature rarely separates:

**Stage 1 (optimization).** A search procedure $\mathcal{A}$ — a metaheuristic, a quantum-inspired variant, or an exact solver — returns thresholds $\hat{\mathbf{t}}=\mathcal{A}(h)$ intended to maximize $F_{\text{Kapur}}$.

**Stage 2 (decoding).** A decoding rule $D$ maps the $k$ intensity bands induced by $\hat{\mathbf t}$ to a binary object mask $M=D(I,\hat{\mathbf t})\in\{0,1\}^{\Omega}$. The rule selects which band(s) constitute the object and may apply spatial post-processing.

Clinical quality is measured on $M$ against a ground-truth mask $G$ by the Dice coefficient
$$
\mathrm{Dice}(M,G)=\frac{2\,|M\cap G|}{|M|+|G|}\in[0,1].
$$
The separation matters because Stage 1 and Stage 2 live in different spaces: Stage 1 acts on the histogram $h$ and is scored by $F_{\text{Kapur}}$; Stage 2 acts on the image $I$ and is scored by Dice. A decade of work optimizes Stage 1. The variable that determines $\mathrm{Dice}$ is not obviously the variable that $\mathcal A$ moves.

### C. The optimization gap and the hit criterion

For a search output $\hat{\mathbf t}$ we quantify its distance from the global optimum by the relative objective gap
$$
\gamma(\hat{\mathbf t})=\frac{F^\star-F_{\text{Kapur}}(\hat{\mathbf t})}{|F^\star|},
$$
and we say $\mathcal A$ *hits* the optimum on an image when $\gamma(\hat{\mathbf t})\le\tau$ with $\tau=10^{-4}$. The hit rate of a method at a given $k$ is the fraction of (image, seed) pairs on which it hits. This is the same convergence criterion, at a five-orders-of-magnitude tighter tolerance, used by Hammouche et al. [Hammouche2010].

### D. The intensity ceiling

Because Stage 2 selects among *intensity* bands, no method in this family can produce a mask finer than the best possible thresholding of $I$. We make that limit precise. For a target label, the *level-set oracle* is the highest Dice attainable by any monotone selection of an intensity super-level set,
$$
\mathrm{Dice}^{\uparrow}(I,G)=\max_{\theta}\ \mathrm{Dice}\big(\{x:I(x)\ge\theta\},\,G\big),
$$
and, more generally, the purity-prefix construction of [Lipton2014] gives the optimal Dice attainable by *any* function of intensity — the tightest possible ceiling for a Stage-2 rule that reads only $I$. This is a known result about $F_1$/Dice maximization; we apply it here as a per-image diagnostic (Section VI-B), and claim the *application and decomposition*, not the theorem. The oracle uses the test-time ground truth $G$ and is therefore an unreachable upper bound (class C), not a method.

### E. Confound: the intensity-zero background

Skull-stripped MRI leaves a large exact-zero background: on the BraTS FLAIR cohort, $\approx 65\%$ of tumor-bearing slices have a dominant zero bin. Whether that bin is included in $h$ changes $\mathbf t^\star$ outright. We therefore treat `include_zero_bg` as a first-class experimental factor and report both settings throughout, rather than choosing the one that flatters any method.

---

## IV. Experimental Protocol

### A. Data and splits

We use the BraTS 2020 training collection (369 pre-operative multimodal MRI cases; 368 after one case fails the tumor-slice criterion, yielding the analysis cohort $n=368$). Two clinically standard targets are studied: whole tumor on FLAIR (`wt_flair`) and enhancing tumor on T1ce (`et_t1ce`), the latter deliberately retained as the hard case. For every learned component, cases are split into five folds **at the patient level**, stratified by grade and by WT-volume tertile; all five folds are mutually disjoint and cover the full cohort, so no slice of a test patient ever contributes to training (leakage audit in Section V, prereg condition A3).

### B. Grid

The main grid crosses 2 targets $\times$ 2 `include_zero_bg` settings $\times$ 7 threshold counts $k\in\{2,3,4,5,6,8,10\}$ $\times$ (9 search procedures $\times$ 5 seeds $+$ exact DP $+$ 5 classical thresholders) $\times$ 4 decoding rules, for 463,680 optimizer cells in total. The nine search procedures are GA, PSO, GOA, a bug-fixed GOA variant, GWO, WOA, MPA, the quantum-inspired QIGOA, and uniform random search. All metaheuristics receive an **identical hard budget** of 5,000 function evaluations and identical population size, so that any difference between them cannot arise from unequal tuning. Random search at equal evaluation budget is included as the floor that any purposeful optimizer must clear.

### C. Metrics

Segmentation quality is reported with a full battery to preclude single-metric cherry-picking: Dice, 95th-percentile Hausdorff distance (HD95), and the Normalized Surface Dice at tolerances $\{1,3,5\}$ mm. The unit of analysis is the patient. Empty predicted masks are retained in HD95 with the image-diagonal penalty rather than dropped, since dropping them would bias the count in favor of thresholding at large $k$.

### D. Statistics

Paired comparisons against the DP-exact reference use the Wilcoxon signed-rank test. **Equivalence** — the claim that two methods produce clinically indistinguishable masks — is tested by two one-sided tests (TOST) at margins $\delta\in\{0.01,0.05\}$ Dice, reported as the smallest margin $\delta_{\text{ach}}$ at which equivalence holds. Omnibus ranking across methods uses Friedman with a Nemenyi critical-difference diagram. All confidence intervals are bootstrap (10,000 resamples over patients). No smoothing, no post-hoc exclusion of unfavorable cells: the analysis protocol and its decision thresholds were pre-registered before the grid was run, and the two pre-registered tripwires (Sections V-A and VI-A) are reported as they fired.

### E. Reproducibility

Each run writes a manifest recording the git commit, config hash, seeds, dataset version, and output paths; every table and figure below traces to a named CSV under `results/` through the provenance ledger `docs/RESULTS.md`. The full grid was executed on a fixed-budget cloud harness with deterministic seeding.

---

## V. Results

We organize the results as a chain of refutation tests. Each subsection states a question whose answer *could* break the paper's thesis, then reports what the data return. The thesis — that the optimization gap the literature contests does not project onto the clinical mask — survives on both of its logical branches.

### A. Do the optimizers reach the Kapur optimum? No.

The first tripwire pre-registered a demanding success condition: hit rate $\ge 0.99$ for every method at every $k$. It fails completely. **None of the 63 (method, $k$) combinations reaches 0.99** (Table II, upper block). The hit rate decays monotonically with the number of thresholds for every procedure. At $k=2$ the strongest solvers approach but do not cross the bar (MPA and WOA 0.981, PSO 0.972); by $k=6$ several procedures — GA, GOA, and random search — reach the optimum on essentially no image (0.000). The quantum-inspired QIGOA is unremarkable within this spread (0.867 at $k=2$, 0.208 at $k=4$, 0.004 at $k=10$), and never separates from the classical metaheuristics it is meant to improve upon. Random search at equal budget is the floor (0.515 at $k=2$, 0.001 at $k=4$).

This reproduces, on $n=368$ with clinical ground truth and at a tolerance five orders of magnitude tighter, the finding of Hammouche et al. [Hammouche2010] that population methods fail to attain the multilevel optimum for $k>2$. Under the paper's single thesis this is the *second* branch: if the optimizers do not even reach the optimum, then a decade of engineering is narrowing a gap whose relevance is exactly what the next test measures.

### B. Does the optimization gap project onto the clinical mask? No. (Thesis.)

Holding the reference at the true global optimum, we compare each metaheuristic's Dice against the DP-exact Dice, patient by patient, at the primary operating point ($k=4$, `brightest` decoding). Across all 36 comparisons (2 targets $\times$ 2 backgrounds $\times$ 9 methods) the **median per-patient Dice difference is exactly zero** (Table II, lower block). Mean differences are bounded within $[-0.0042,+0.0042]$ Dice. Equivalence by TOST holds at the $\delta=0.05$ margin in **36 of 36** comparisons, and at the tighter $\delta=0.01$ margin in **36 of 36**; the smallest margin at which equivalence can be declared is at most **0.70%** Dice across the entire block.

The two branches together are the result. A method can miss the Kapur optimum badly enough that its hit rate falls to zero (Section V-A), yet its clinical mask is statistically equivalent to the mask produced by the exact global optimum (this section). The distance in objective space that the literature spends its effort closing does not move the mask. **The optimization gap does not project onto the clinical target.**

### C. Where does the gap live? Not in intensity.

If closing the Kapur gap does not help, the natural question is whether the information needed to segment the tumor is present in the image at all, or whether intensity thresholding is simply the wrong instrument. We answer this by decomposing the ceiling. For `wt_flair` we compare, per patient, the level-set oracle — the highest Dice any intensity-only rule can achieve, using the test-time ground truth — against a 2-D U-Net trained out-of-fold on the *same single FLAIR slice* that the thresholding methods see at inference.

The U-Net exceeds the intensity ceiling (Table III, Fig. 3). Its median Dice is **0.9234** (IQR $[0.8666,0.9497]$) against the oracle's **0.8532**, a paired median gain of **+0.0503** Dice (bootstrap 95% CI $[+0.0413,+0.0646]$). The U-Net wins on **293 of 368 patients (79.6%)**; the Wilcoxon test gives $p=2.77\times10^{-32}$ with a rank-biserial effect size of **0.712**. The gain is consistent across all five folds (per-fold median Dice 0.9185, 0.9238, 0.9224, 0.9289, 0.9249).

The interpretation is a decomposition, stated carefully. Roughly five Dice points that *no* intensity-only rule can reach — not even one granted a perfect choice of threshold — are recovered from *the very same pixels* by a model that reads spatial structure. The failure of thresholding is therefore not a limit of the information in the input; it is a limit of the intensity-only hypothesis class. The gap is *not in the intensity*, not *not in the pixels*. We do not claim to establish the achievable ceiling on BraTS — that bound is already reported by François and Tinarrage [Francois2026]; we quantify and *decompose* it.

Two honesty constraints attach to this comparison. The oracle uses the test-time ground truth (class C) while the U-Net is scored strictly out-of-fold (class B), so this is an information decomposition, not a claim that the U-Net beats a fair baseline. And the U-Net covers `wt_flair` at a single seed; the enhancing-tumor target, whose intensity ceiling is far lower (median oracle Dice 0.6351), is left to the intensity oracle and classical thresholders in this work.

### D. Goodhart on the number of thresholds.

The remaining question concerns how the field selects $k$. The surrogate that the literature reports — PSNR — is a monotone function of quantization error and therefore increases with $k$ by construction (Lloyd–Max). The data confirm this without exception: mean PSNR rises monotonically across every $k$ step on all four target$\times$background settings (from $21.5$–$25.0$ dB at $k=2$ to $36.5$–$36.9$ dB at $k=10$), and PSNR selects the largest available $k=10$ in **16 of 16** configurations. The Dice-optimal $k$, by contrast, is 2 or 3, and never 10 outside one degenerate cell. The disagreement between the argmax of the reported surrogate and the argmax of clinical quality is thus universal and structural.

The clinical cost of choosing $k$ by PSNR, however, is not fixed by the optimizer or the metric — it is governed by the arbitrary Stage-2 decoding rule. Holding the optimizer at DP-exact, the per-patient Dice lost by selecting $k$ with PSNR instead of Dice ranges from **0.0009 to 0.3210** across decoding rules, a spread of more than two orders of magnitude in which the only thing that varies is the decoder (Fig. 4). Under the primary `brightest` rule the loss is 0.126 (`wt_flair`, zero-bg excluded) and 0.102 (zero-bg included); under `morph` it reaches 0.321.

We report the parts of P3 that do not survive as forthrightly as the parts that do. The pre-registered secondary form — a per-patient rank correlation $\rho(k,\mathrm{Dice})<-0.5$ — fails in all 16 configurations, and its sign flips with the decoding rule (from $-0.937$ under `morph` to $+0.288$ under `upper_union` on `wt_flair`, and to $+0.991$ under `brightest` on `et_t1ce`). The simple statement "higher $k$ gives lower Dice" is therefore not supported in general and is withdrawn. Empty-mask rate does not rise with $k$ (it stays $\approx 0$ everywhere, contrary to our own prior expectation). And within a fixed $k$, PSNR and Dice correlate *positively* across methods (up to $+0.891$): the pathology is on the $k$ axis, not the method axis. What survives is the load-bearing claim — the surrogate used to choose model complexity is structurally maximized at the wrong value — and it converges with the rest of the paper onto a single mechanism: the mask is set by decoding, and the optimizer is scenery.

---

## VI. Discussion

### A. Why the gap does not project: the mask is set in Stage 2

The three tests converge on one mechanism. The optimizer acts on the histogram and is scored by $F_{\text{Kapur}}$; the Dice is fixed downstream, by which bands the decoding rule selects and by whatever spatial post-processing it applies. When the two stages are held apart, the evidence is direct. Replacing every metaheuristic with the exact global optimum leaves Dice unchanged (Section V-B), so Stage 1 is not where the mask is decided. Conversely, changing only the decoding rule — with the optimizer pinned at DP-exact — moves the clinical cost of a mis-chosen $k$ by more than two orders of magnitude (Section V-D). The clearest single demonstration is that a decoding rule which injects spatial structure breaks the intensity ceiling outright: under morphological decoding the exact optimizer reaches a median WT Dice of 0.8941, above the 0.8532 level-set oracle that bounds *any* intensity-only rule. A stage that the field treats as an afterthought is the stage that determines the result.

This reframes the degeneracy honestly, and it is worth stating what we do *not* claim. We do not attribute a specific decoding rule to the literature; papers in this family use region growing, $k$-means with morphology, or morphological reconstruction, and many never build a binary mask or touch ground truth at all. The claim is structural, not an accusation: whatever Stage-2 rule a given paper adopts, that is where its Dice is set, and the Stage-1 optimization it reports on is not the variable that moves the clinical mask. This is the dilemma the title names — optimizing the wrong variable — and it holds regardless of which decoding a reader has in mind.

### B. A diagnostic that costs microseconds

The level-set ceiling of Section III-D is not only an analytical device; it is computable before any optimizer is written. Given the per-level object purity $p(\ell)=\Pr(\text{object}\mid I=\ell)$, the highest Dice attainable by any function of intensity follows from the purity-prefix construction [Lipton2014]: sort the $L$ levels by purity and take the best prefix. For $L=256$ this is a sort of 256 numbers — $O(L\log L)$, microseconds per image. A practitioner can therefore compute, from the labeled histogram alone, the Dice ceiling that the *entire family* of intensity-threshold methods shares, before implementing a single search procedure. Where that ceiling is far from the clinical requirement — as it is for enhancing tumor, median oracle Dice 0.6351 — the diagnosis is available in advance: no optimizer, exact or otherwise, and no choice of $k$, will close the distance, because the distance is not in intensity. We claim this application and the ceiling decomposition it enables; the underlying theorem is Lipton et al.'s, and the fact that thresholding on BraTS has a ceiling in this range is François and Tinarrage's [Francois2026].

### C. Limitations

The U-Net rung of the decomposition covers whole tumor on FLAIR at a single seed; multi-seed variance and the enhancing-tumor target, where the intensity ceiling is low and a learned model would test the decomposition on the hard case, are left to future work. The oracle–U-Net comparison is an information decomposition, not a fair-baseline benchmark: the oracle consumes test-time ground truth (class C) while the U-Net is scored out-of-fold (class B). The evaluation is on BraTS 2020 only; external validation on an independent cohort is deferred, and we note that the commonly used LGG collection overlaps the TCGA-LGG cases already present in BraTS, so it would not constitute a genuinely external test. Finally, the surrogate analysis targets PSNR, the dominant reported measure in this literature; SSIM and FSIM share the monotone-in-$k$ structure but are not exhaustively swept here.

---

## II. Related Work

Multilevel thresholding by metaheuristic optimization of Kapur or Otsu criteria is a large and active literature, and this paper's contribution is best located against four groups of prior work rather than an enumeration of it.

**Exact solvers.** The exact global optimum of the Kapur and Otsu criteria is a solved problem: Menotti et al. [Menotti2015] give a dynamic program at $O((k-1)L^2)$ that returns the optimum in under 160 ms, and later work confirms exact dynamic programming outperforming metaheuristics on Otsu [Merzban2019]. We use this exact optimum as a reference and claim no algorithmic novelty in computing it; a paper whose thesis is that the field does not cite the exact solution must itself cite it.

**Metaheuristic comparisons without ground truth.** Comparative studies of population methods on the multilevel problem — including the observation that recent algorithms fail to attain the optimum for $k>2$ [Hammouche2010] and that many modern metaheuristics do not segment better than older ones [Mousavirad2023] — are conducted on natural images without segmentation ground truth. That is precisely the setting in which the degeneracy we report is invisible: without a clinical mask, one cannot observe that the objective gap fails to project onto Dice. Our contribution is to run the comparison in a domain that *has* ground truth and to measure the projection directly.

**The ceiling and its theorem.** That intensity thresholding on BraTS has a bounded achievable Dice is reported by François and Tinarrage [Francois2026], who give a mean oracle Dice of $0.83\pm0.18$ on FLAIR; we therefore make no claim to establishing a ceiling. The optimality of a level-set / purity-prefix selection for $F_1$/Dice is due to Lipton et al. [Lipton2014] and the RankSEG line [Dai2023]; we apply it as a diagnostic and claim neither result as our own. Our contribution is the *decomposition* — separating the intensity ceiling from the pixel ceiling with a learned model on identical input — which neither line performs.

**Metric critique on the $k$ axis.** That PSNR is a poor proxy for segmentation quality, and biased across the number of thresholds, has been argued from 2016 onward [Fardo2016] and recently sharpened to a bias of evaluation metrics toward particular objective functions [HegazyGabr2026a]. Those works lack clinical ground truth, Dice, and the $k$ axis in a medical setting; the group producing them is publishing rapidly on adjacent problems, including dynamic programming that selects the threshold count [HegazyGabr2026b], which is why we prioritize an early preprint. We extend the metric critique into the domain where a clinical target exists and show the cost is real but decoder-dependent.

Finally, on the specific method that motivated this study: the quantum-inspired grasshopper optimizer is best understood without its two metaphors. Quantum-inspired evolutionary algorithms are estimation-of-distribution algorithms on classical hardware [Platel2009], with no proven quantum advantage; the grasshopper optimizer has been shown to be a particle-swarm variant [Harandi2024]. QIGOA is thus an EDA-style probabilistic update over a PSO-like search, and quantum-inspired thresholding itself dates to 2014 [Dey2014]. We position it accordingly and make no quantum-advantage claim.

---

## I. Introduction

For over a decade, a steady stream of papers has proposed new metaheuristic and quantum-inspired optimizers for multilevel image thresholding, and applied them to brain tumor MRI. The reported improvements are measured almost entirely in the optimizer's own currency: a higher Kapur or Otsu objective, a better PSNR, a favorable convergence curve. The brain tumor benchmarks these methods run on — BraTS above all — ship with expert segmentation masks. Those masks are rarely opened.

This paper opens them, and the picture inverts. We hold the optimization at its exact global optimum, computable in milliseconds [Menotti2015], and ask a single question with a clinical answer: does the objective distance the field competes to close move the segmentation mask? On the full BraTS 2020 cohort ($n=368$), with a fully separated optimization-then-decoding pipeline and a complete statistical protocol, the answer is no. Metaheuristics do not reach the Kapur optimum — no method clears a 0.99 hit rate at any threshold count, and the hit rate collapses to zero as $k$ grows — yet their clinical masks are statistically equivalent to the exact optimum's, with a median per-patient Dice difference of exactly zero. The gap is real and the mask does not feel it.

This is not merely a negative result about one optimizer. The thesis holds on both of its branches at once: if every metaheuristic reached the optimum, the optimizer would be decorative; since none does, a decade of engineering is closing a gap that provably does not project onto the clinical target. Either way, the field is optimizing the wrong variable.

We make the following contributions.

1. **A measurement.** On a domain with clinical ground truth, we show the optimization gap that the literature contests does not project onto the segmentation mask — a claim that is immortal before the experiment, since it holds whether or not the optimizers converge, and we verify both branches on $n=368$.
2. **A ceiling decomposition.** Comparing the intensity-only level-set ceiling against a 2-D U-Net on identical input, we separate the segmentation gap into what is *not in the intensity* from what is *not in the pixels*. On whole tumor the learned model exceeds the intensity ceiling by five Dice points, locating the gap in spatial structure rather than in the input.
3. **A diagnostic and a protocol.** We give an $O(L\log L)$ procedure that computes the Dice ceiling of the entire intensity-threshold family from the labeled histogram alone, before any optimizer is written, and a short evaluation-protocol checklist that would have surfaced the degeneracy.

We claim none of the underlying theorems. The exact solver is Menotti et al.'s [Menotti2015], the level-set optimality is Lipton et al.'s [Lipton2014], and the existence of a thresholding ceiling on BraTS is François and Tinarrage's [Francois2026]. We do not claim quantum advantage, we do not claim a speed record, and we do not claim to establish the ceiling. What is ours is the measurement, the decomposition, and the diagnostic.

---

## VII. Conclusion

A decade of optimizers has been improving a number that does not reach the patient. We showed, on the full BraTS 2020 cohort, that the metaheuristic and quantum-inspired methods contesting the Kapur objective neither reach its optimum nor need to: their clinical masks are indistinguishable from the exact optimum's, because the mask is set by a decoding stage the field treats as an afterthought. Decomposing the ceiling with a learned model on identical input places the remaining gap in spatial structure, not in intensity — and the same conclusion is reachable in microseconds, before any optimizer is written, from the labeled histogram alone. The honest reframing is not that these methods fail, but that they answer a question whose answer the clinical mask cannot hear. The instrument to check this was in the dataset the whole time.

