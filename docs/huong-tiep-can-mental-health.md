# Hướng tiếp cận paper — Trustworthy Digital Phenotyping for Depression

> **Kính gửi thầy — tóm tắt tiếng Việt (đọc nhanh).**
> Đây là hướng tiếp cận mới em đề xuất cho luận án, thay cho hướng QIGOA (thresholding lượng tử) vì gap của
> QIGOA hẹp, khó đạt tầm Q1. Hướng mới: **AI đáng tin cậy (trustworthy) để sàng lọc trầm cảm từ giọng nói
> và cảm biến thụ động (điện thoại/wearable)**, chỉ dùng **dữ liệu công khai**, chạy được trên Kaggle.
> Điểm mấu chốt: em KHÔNG chạy theo "phân loại trầm cảm trên một bộ dữ liệu" (đã bão hòa và nhiều nghiên
> cứu bị *shortcut learning*), mà nhắm vào khoảng trống còn mở thật: **mô hình phải TỔNG QUÁT HÓA qua bộ
> dữ liệu/ngôn ngữ/thiết bị, có XÁC SUẤT ĐƯỢC HIỆU CHỈNH (calibration) + LỢI ÍCH LÂM SÀNG (net-benefit) +
> CÔNG BẰNG theo nhóm** — ba tiêu chí này chưa công trình nào gộp lại trên một quy trình đánh giá thống
> nhất. Toàn bộ định vị đã được em kiểm chứng bằng rà soát tài liệu 2022–2026 (mọi trích dẫn đều là bài
> thật; các bài 2026 em đánh dấu cần kiểm lại DOI). Rất mong thầy góp ý về trọng tâm và phạm vi.

---

## Proposed working title
**Trustworthy Digital Phenotyping for Depression: Generalizable, Calibrated, and Equitable Screening from Speech and Passive Sensing.**

*First paper (conference) working title:* *"Beyond In-Corpus Accuracy: Shortcut-Robust and Externally-Validated Speech-Based Depression Screening across Languages."*

---

## 1. Clinical motivation
Depression is among the largest global contributors to disability, and the **treatment gap is enormous** — a large share of people, especially in low-resource settings, are never screened or diagnosed (WHO). Standard screening relies on clinician time and self-report scales, which do not scale. **Speech** (a 2–3 minute recording) and **passive smartphone/wearable sensing** offer objective, low-cost, remotely-collectable behavioural signals that could extend screening and monitoring far beyond the clinic — *if* the models are trustworthy enough to deploy.

> *Ghi chú:* các con số gánh nặng bệnh cụ thể (số người mắc, tỉ lệ chưa điều trị, tử vong do tự sát) sẽ
> được em trích đúng nguồn WHO/GBD trong bản chính thức; ở đây em chỉ nêu định tính để tránh sai số liệu.

## 2. The problem with the current literature (what is saturated vs still open)
A structured review of 2022–2026 work shows the field is **not** short of depression classifiers — it is short of *trustworthy, deployable* ones:

- **Single-corpus classification is saturated**, and worse, **frequently invalid**: several audits show state-of-the-art models on the benchmark clinical-interview dataset (DAIC-WOZ) achieve high scores by exploiting *shortcuts* (e.g. the interviewer's prompts) rather than depression-specific signal (Burdisso et al., ClinicalNLP@NAACL 2024; Patapati et al., ICMI 2025). This critique is **already established** — the contribution is not to re-discover it, but to build on it.
- **Generalization is recognised but unsolved.** The flagship cross-dataset passive-sensing benchmark (GLOBEM; Xu et al., IMWUT 2022) reports that ~19 algorithms, including dedicated domain-generalization methods, barely beat a majority-class baseline across cohorts. In speech, cross-lingual/cross-corpus transfer collapses (e.g. foundation-model probing across French/Italian corpora, 2024). These are **negative/benchmark results that motivate the work**, not solutions.
- **Calibration and clinical utility are largely absent.** Almost no digital-phenotyping paper reports whether its probability outputs are *calibrated* or whether they yield *net clinical benefit* (decision-curve analysis). A rare exemplar exists (Weber et al., Front. Psychiatry 2025), confirming this is an open, high-value axis.
- **Equity is only partially addressed** (gender documented; age/language/cross-lingual and *joint* calibration-fairness thin).

## 3. Research gap (verified) and central hypothesis
**No existing work treats generalization, calibration/clinical-utility, and subgroup equity as jointly-optimised, first-class objectives *under distribution shift*, on public speech + passive-sensing data, within a single leakage-audited external-validation protocol.**

**Hypothesis:** a screening approach whose *primary success criteria* are (i) generalization measured across dataset/language/device shift, (ii) calibrated risk with demonstrated net benefit, and (iii) equitable performance across subgroups — will be more clinically deployable than the current accuracy-on-one-corpus paradigm, and this can be developed and validated entirely on public data.

## 4. Proposed contributions
1. A **leakage-audited, external-validation protocol** for speech/sensing depression screening (subject-disjoint splits; patient-only-utterance training to remove interviewer shortcuts; leave-one-dataset-out / zero-shot cross-lingual evaluation).
2. **Calibration + clinical-utility as headline metrics** — reliability/ECE, post-hoc recalibration, conformal uncertainty, and **decision-curve / net-benefit** analysis under distribution shift (the most open axis).
3. A **joint fairness–calibration treatment**: subgroup calibration/coverage gaps and mitigation across gender/age/language, coupled with (not separate from) calibration.
4. A **cross-modality** study bridging the currently-siloed speech and passive-sensing literatures, culminating in a longitudinal early-warning signal.

*(Honest scope note for the advisor: this is a **trustworthy-ML contribution with strong clinical motivation** — the novelty is methodological rigour + deployability, not a new disease target. It is led by external validation + net benefit so that it stays clinically meaningful.)*

## 5. Data, methods, and evaluation (all public, moderate compute)
- **Public datasets — speech:** DAIC-WOZ / E-DAIC (English), Androids (Italian), MODMA (Chinese; also EEG), EATD (Mandarin), D-Vlog (in-the-wild) → cross-lingual external testing. **Passive sensing:** GLOBEM (multi-year, the key generalization/longitudinal substrate), StudentLife, DEPRESJON/PSYKOSE (actigraphy). All are openly available under research licences (to be confirmed per dataset).
- **Backbone (Kaggle-feasible):** frozen **WavLM** speech representations (mid-layers, which are strongest for depression) + a lightweight head — no large-scale pretraining needed; temporal models + the GLOBEM benchmark harness for sensing.
- **Metrics/protocol:** AUROC + **AUPRC**; **ECE / Brier / reliability diagrams** + recalibration + conformal sets; **decision-curve analysis / net benefit**; subgroup AUROC/calibration gaps + equalized-odds; in-domain vs external gap reported explicitly; reproducibility with fixed seeds and Wilcoxon/Friedman + Holm tests.
- **Integrity:** this is a *proposed* design — **no experimental numbers are reported until real runs exist**; every quantitative claim in future drafts will trace to a re-runnable script.

## 6. Thesis structure (conference → journal, 4 papers)
| Paper | Focus | Data | Type |
|---|---|---|---|
| **P1** | Shortcut-robust + externally-validated speech screening across languages | DAIC/E-DAIC → LODO Androids/MODMA/EATD | Conference (Interspeech/ICASSP) |
| **P2** | **Calibration + net-benefit** of speech depression models (cross-corpus) | same speech corpora | Journal (JMIR / npj Digital Medicine) |
| **P3** | **Fairness + calibration** across modalities | speech + GLOBEM + (text) | Journal |
| **P4** | Longitudinal, calibrated, equitable early-warning (**deterioration/trajectory**) | GLOBEM (multi-year) + replication | Flagship journal (IMWUT / npj Digital Medicine) |

**Immediate deliverable = P1**, which alone is a self-contained conference paper and de-risks the whole programme.

## 7. Honest limitations to discuss with the advisor
1. **Longitudinal relapse labels are scarce in public data.** GLOBEM provides periodic depression-scale trajectories but **no clinician-verified relapse events** (the ideal cohort, RADAR-MDD, is access-controlled). → P4 targets *deterioration/severity-trajectory* forecasting, not clinician-verified relapse, unless we secure gated/collaborator data.
2. **This is a rigour/trustworthiness contribution**, not a new clinical modality — we must lead with external validation + net benefit to keep clinical reviewers convinced.
3. **Dataset licences and a few very recent (2026) citations still need confirmation** before the formal manuscript.

## 8. Questions for the advisor
- Trọng tâm P1 nên nghiêng **speech** (em đề xuất, vì nhẹ và cross-lingual rõ) hay khởi động bằng **passive sensing (GLOBEM)**?
- Thầy có hướng tới một **venue** cụ thể (Interspeech/ICASSP vs JMIR/npj Digital Medicine) để em định dạng ngay từ đầu không?
- Có khả năng tiếp cận **dữ liệu lâm sàng** (giọng nói/relapse có nhãn) qua hợp tác của thầy không? Nếu có, P4 sẽ mạnh hơn nhiều (relapse thật thay vì trajectory).

## References (verified; 2026 items flagged for DOI re-check)
1. J. Burdisso et al., "DAIC-WOZ: On the Validity of Using the Therapist's Prompts…," *ClinicalNLP @ NAACL*, 2024. arXiv:2404.14463.
2. Patapati et al., "Most DAIC-WOZ Depression Classifiers Are Invalid…," *ICMI Companion*, 2025. doi:10.1145/3747327.3763034.
3. X. Xu et al., "GLOBEM: Cross-Dataset Generalization of Longitudinal Human Behavior Modeling," *ACM IMWUT*, 2022. doi:10.1145/3569485; dataset arXiv:2211.02733.
4. "Probing Mental Health Information in Speech Foundation Models," 2024. arXiv:2409.19042.
5. Dang et al., "Fairness and bias correction in ML for depression prediction across four populations," *Scientific Reports*, 2024. doi:10.1038/s41598-024-58427-7.
6. Weber et al., "Depression diagnosis from patient interviews using multimodal ML" (calibration + net benefit), *Frontiers in Psychiatry*, 2025. doi:10.3389/fpsyt.2025.1694762.
7. Li et al., "Fair Uncertainty Quantification for Depression Prediction," 2025. arXiv:2505.04931.
8. Amin et al., "Mobile sensing for longitudinal prediction of depression severity: systematic review," *JMIR*, 2025. doi:10.2196/57418.
9. Mancini et al., "Promoting the Responsible Development of Speech Datasets for Mental Health…," *JAIR* 82, 2025. arXiv:2406.04116.
10. S. Chen et al., "WavLM: Large-Scale Self-Supervised Pre-Training for Full Stack Speech Processing," *IEEE JSTSP*, 2022.
11. A. Vickers, E. Elkin, "Decision Curve Analysis," *Medical Decision Making*, 2006. *(net-benefit methodology)*.
12. Datasets: Gratch et al., DAIC-WOZ (*LREC* 2014); AVEC-2019/E-DAIC; Cai et al., MODMA; R. Wang et al., StudentLife (*UbiComp* 2014).

> *Ghi chú liêm chính:* các bài 2026 (vd audit đa-probe, interviewer-effects mở rộng) là thật nhưng nằm sau
> mốc kiểm tra của công cụ; em sẽ xác minh DOI/venue cuối trước khi đưa vào bản nộp.
