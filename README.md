# Grading Reliability Analysis

**Author:** Lawrence Angrave

Tests whether multiple graders applied the same scoring standards when each grader was randomly assigned a different set of exams.

## When to use this

**Appropriate when:**
- Graders were randomly assigned to students (each exam graded by exactly one person)
- You want to check whether graders scored similarly overall
- Scores are ordinal (e.g. 0–100, letter grades, rubric levels)

**Not appropriate when:**
- The same exam was graded by multiple graders — use Fleiss' Kappa or Krippendorff's Alpha instead, which directly measure pairwise agreement on the same item
- Graders were not randomly assigned (e.g. one grader took all the hard exams), since systematic differences in exam difficulty would confound the result
- You have fewer than ~5 scores per grader (low statistical power)

## Statistical method

The primary test is **Kruskal-Wallis**, a non-parametric one-way ANOVA on ranks:

> H₀: all graders draw scores from the same distribution

It is preferred over standard ANOVA because grading scores are ordinal and typically skewed (many high scores), which violates ANOVA's normality assumption. Kruskal-Wallis makes no such assumption.

If the test is significant (p < 0.05), **Dunn's post-hoc test** with Bonferroni correction is run automatically to identify which specific grader pairs differ.

The script also reports **η²** (eta-squared) as an effect size: values near 0 indicate negligible differences between graders regardless of sample size.

## Data format

Tab-separated file (`.tsv`) with a header row and two columns:

| TA      | score |
|---------|-------|
| Alice   | 90    |
| Alice   | 100   |
| Bob     | 80    |
| Bob     | 90    |

- Column 1: grader name or ID
- Column 2: numeric score
- Each row is one student's score from one grader
- Graders do not need to have graded the same number of exams

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install pandas scipy scikit-posthocs matplotlib
```

## Usage

```bash
python3 grading_reliability.py              # defaults to scores.tsv
python3 grading_reliability.py myfile.tsv  # specify a different file
```

## Output

- Descriptive statistics (count, mean, median, std, min, max) per grader
- Kruskal-Wallis H statistic, p-value, and η² effect size
- Dunn's post-hoc table (only printed when the overall test is significant)
- `score_distributions.png` — stacked bar chart of score proportions and box plots per grader
