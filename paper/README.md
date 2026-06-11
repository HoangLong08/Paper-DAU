# Paper: QIGOA for Multilevel Brain MRI Thresholding

**Target venue:** *Journal of Computer Science and Cybernetics* (JCC, Vietnam Academy of Science and Technology) — Scopus-indexed.

## Files

| File | Purpose |
|------|---------|
| `paper.tex` | Main manuscript (LaTeX) |
| `paper.bib` | BibTeX references (24 entries, all resolved) |
| `figures/` | All 5 PNG figures from the experiments |
| `TinLatex.tex`, `TinLatex.cls`, `TinLatex.sty` | JCC template engine (do not modify) |
| `Dih.tex`, `Vnfonts.tex` | Vietnamese font macros (template requirement) |
| `IEEEtranS.bst`, `setbmp.tex`, `seteps.tex`, `setps.tex`, `setwmf.tex` | Template helpers |

## How to compile

### Option A — Overleaf (recommended, easiest)

1. Go to https://overleaf.com → **New Project → Upload Project**.
2. Zip the entire `paper/` folder (right-click → Send to → Compressed) and upload.
3. In Overleaf, open `paper.tex` and click **Recompile**.
4. The PDF will be ready in 10–20 seconds.

### Option B — Local (need MiKTeX or TeX Live)

```bash
cd paper/
pdflatex paper
bibtex paper
pdflatex paper
pdflatex paper
```

Final output: `paper.pdf`.

## Authors (đã điền)

- **Long Nguyen Vo Hoang** (first author + corresponding) — `longnvh@dau.edu.vn`
- **Do Phu Hao** (advisor / co-author) — `haodp@dau.edu.vn`
- Affiliation: Danang Architecture University, Da Nang, Viet Nam.

Nếu cần thêm khoa cụ thể (vd. "Faculty of Information Technology") hoặc địa chỉ chi tiết, sửa trực tiếp trong `paper.tex` (block `\author{...}`).

## Việc còn lại

- `Received on XX, 2026` / `Accepted on XX, 2026` — để trống, editor sẽ điền khi accept.

## Paper structure

| Section | Pages (estimate) |
|---|---|
| Title, abstract, keywords | 0.5 |
| 1. Introduction | 1.5 |
| 2. Related Work | 1.0 |
| 3. Background | 1.0 |
| 4. Proposed QIGOA | 2.0 |
| 5. Experimental Setup | 1.0 |
| 6. Results and Discussion | 3.0 |
| 7. Conclusion | 0.3 |
| References | 1.0 |
| **Total** | **~11 pages** |

JCC requires min 8, max 15 pages — within range.

## Key claims defended

1. QIGOA beats parent GOA in ALL 10 (k, fitness) configurations — `p < 10⁻⁷`
2. QIGOA beats MPA, WOA at high-k (k≥6) and Tsallis k=8
3. QIGOA beats GA, GWO at k=10 Kapur
4. QIGOA reaches statistical parity with PSO, GA, GWO on standard k=2..5
5. Friedman test confirms QIGOA in top group for 8/10 configurations
