# grading_reliability.py — see README.md for usage, data format, and method.
# Copyright 2027 Lawrence Angrave

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
import sys
import pandas as pd
from scipy.stats import kruskal
import scikit_posthocs as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TSV_FILE = sys.argv[1] if len(sys.argv) > 1 else "scores.tsv"
ALPHA = 0.05

# ── Load data ─────────────────────────────────────────────────────────────────

df = pd.read_csv(TSV_FILE, sep="\t")
df.columns = [c.strip().lower() for c in df.columns]

if len(df.columns) < 2:
    raise ValueError("File must have at least two columns: grader name and score.")

grader_col, score_col = df.columns[0], df.columns[1]
df[score_col] = pd.to_numeric(df[score_col], errors="coerce")
df = df.dropna(subset=[score_col]).copy()
df[score_col] = df[score_col].astype(int)

graders = sorted(df[grader_col].unique())
groups = {g: df[df[grader_col] == g][score_col].values for g in graders}

if len(graders) < 2:
    raise ValueError("Need at least two graders to compare.")

print(f"File   : {TSV_FILE}")
print(f"Graders: {graders}")
print(f"Scores : {sorted(df[score_col].unique())}")
print()

# ── Descriptive statistics ────────────────────────────────────────────────────

print("═" * 52)
print("DESCRIPTIVE STATISTICS")
print("═" * 52)
desc = df.groupby(grader_col)[score_col].agg(
    n="count", mean="mean", median="median", std="std", min="min", max="max"
).round(2)
print(desc.to_string())
print()

# ── Kruskal-Wallis test ───────────────────────────────────────────────────────

print("═" * 52)
print("KRUSKAL-WALLIS TEST")
print("═" * 52)

H, p_value = kruskal(*groups.values())
k = len(graders)
n = len(df)
eta2 = (H - k + 1) / (n - k)  # effect size η²

print(f"  H({k - 1}) = {H:.3f},  p = {p_value:.4f},  η² = {max(eta2, 0):.4f}")
print()

if p_value < ALPHA:
    print(f"  SIGNIFICANT (p < {ALPHA}): at least one grader scores differently.")
    print()
    print("─" * 52)
    print("DUNN'S POST-HOC TEST  (Bonferroni correction)")
    print("─" * 52)
    dunn = sp.posthoc_dunn(
        df, val_col=score_col, group_col=grader_col, p_adjust="bonferroni"
    )
    print(dunn.round(4).to_string())
    print()
    print(f"  Adjusted p-values < {ALPHA} indicate a significant pair.")
else:
    print(f"  NOT significant (p ≥ {ALPHA}): graders' distributions are consistent")
    print("  with random assignment from the same population.")

print()

# ── Plot ──────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle(
    f"Grading Reliability  |  Kruskal-Wallis H({k - 1}) = {H:.2f},  p = {p_value:.3f}",
    fontsize=13, fontweight="bold"
)

all_scores = sorted(df[score_col].unique())
contingency = (
    df.groupby([grader_col, score_col])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=all_scores, fill_value=0)
)
proportions = contingency.div(contingency.sum(axis=1), axis=0)
proportions.plot(kind="bar", stacked=True, ax=axes[0], colormap="RdYlGn", edgecolor="white")
axes[0].set_title("Score Distribution per Grader (proportions)")
axes[0].set_xlabel("Grader")
axes[0].set_ylabel("Proportion")
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=30, ha="right")
axes[0].legend(title="Score", bbox_to_anchor=(1.01, 1), loc="upper left")

axes[1].boxplot([groups[g] for g in graders], tick_labels=graders, patch_artist=True)
axes[1].set_title("Score Distributions")
axes[1].set_xlabel("Grader")
axes[1].set_ylabel("Score")
axes[1].tick_params(axis="x", rotation=30)

plt.tight_layout()
plt.savefig("score_distributions.png", dpi=150, bbox_inches="tight")
print("Plot saved → score_distributions.png")
