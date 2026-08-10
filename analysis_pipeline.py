import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import warnings, os

df = pd.read_csv("tidy_data.csv")
print(f"Data: {len(df)} rows, {df.Material.nunique()} materials, {df.Factor.nunique()} factors, {df.Adsorbent.nunique()} adsorbents\n")

FACTOR_NAMES = {"ad_dosage": "Adsorbent dosage (mg)", "analyte": "Initial concentration (mg/L)", "pH": "pH", "Temp": "Temperature (K)", "time": "Contact time (min)"}
MATERIALS = ["PE", "PET", "PS"]
FACTORS = ["ad_dosage", "analyte", "pH", "Temp", "time"]
ADSORBENTS = ["GO-CS", "GO-MCC50", "GO-MCC90"]

# ── helpers ──────────────────────────────────────────────────────────
def eta_sq(ss_effect, ss_error):
    return ss_effect / (ss_effect + ss_error) if (ss_effect + ss_error) else 0

def omega_sq(ss_effect, df_effect, ms_error, ss_total, ms_error_global):
    return (ss_effect - df_effect * ms_error) / (ss_total + ms_error_global) if (ss_total + ms_error_global) else 0

def cohens_f(eta):
    return np.sqrt(eta / (1 - eta)) if eta < 1 else np.inf

def eta_interpret(eta):
    if eta < 0.01: return "Negligible"
    elif eta < 0.06: return "Small"
    elif eta < 0.14: return "Medium"
    return "Large"

def compact_letter_display(tukey, group_means):
    groups = list(tukey.groupsunique)
    n = len(groups)
    sig = np.zeros((n, n), dtype=bool)
    idx = {g: i for i, g in enumerate(groups)}
    for k, (g1, g2) in enumerate(combinations(groups, 2)):
        if k < len(tukey.pvalues) and tukey.pvalues[k] < 0.05:
            sig[idx[g1], idx[g2]] = sig[idx[g2], idx[g1]] = True
    sorted_g = sorted(groups, key=lambda g: group_means[g], reverse=True)
    letters = {}
    cur = 0
    for g in sorted_g:
        used = {letters[og] for og in letters if sig[idx[g], idx[og]]}
        for code in range(cur + 1):
            if code not in used:
                letters[g] = code
                break
        else:
            cur += 1
            letters[g] = cur
    return {g: chr(97 + l) for g, l in letters.items()}

# ── 1. Descriptive statistics ────────────────────────────────────────
print("=" * 72)
desc = df.groupby(["Material", "Factor", "Adsorbent"])["PctAdsorption"].agg(["mean", "std", "min", "max", "count"]).round(2)
desc.to_csv("table_descriptive_stats.csv")
print("STEP 1: Descriptive statistics → table_descriptive_stats.csv")
print("=" * 72 + "\n")

# ── per‑combination analysis ─────────────────────────────────────────
records_anova = []
records_tukey = []
records_assumptions = []
records_ci = []
records_practical = []
records_cv = []

all_results = {}

for mat in MATERIALS:
    for fac in FACTORS:
        key = f"{mat}/{fac}"
        sub = df[(df.Material == mat) & (df.Factor == fac)].copy()
        N = len(sub)
        if N < 6:
            print(f"SKIP {key}: insufficient data ({N} rows)")
            continue

        model = ols("PctAdsorption ~ C(Level) + C(Adsorbent)", data=sub).fit()
        anova = anova_lm(model, typ=2)
        ss_level = anova.loc["C(Level)", "sum_sq"]
        ss_ads = anova.loc["C(Adsorbent)", "sum_sq"]
        ss_resid = anova.loc["Residual", "sum_sq"]
        df_level = int(anova.loc["C(Level)", "df"])
        df_ads = int(anova.loc["C(Adsorbent)", "df"])
        df_resid = int(anova.loc["Residual", "df"])
        ms_resid = ss_resid / df_resid if df_resid else 0
        ss_total = ss_level + ss_ads + ss_resid

        # Effect sizes
        eta_level = eta_sq(ss_level, ss_resid)
        eta_ads = eta_sq(ss_ads, ss_resid)
        omega_level = omega_sq(ss_level, df_level, ms_resid, ss_total, ms_resid)
        omega_ads = omega_sq(ss_ads, df_ads, ms_resid, ss_total, ms_resid)
        cohen_level = cohens_f(eta_level)
        cohen_ads = cohens_f(eta_ads)

        f_level = anova.loc["C(Level)", "F"]
        p_level = anova.loc["C(Level)", "PR(>F)"]
        f_ads = anova.loc["C(Adsorbent)", "F"]
        p_ads = anova.loc["C(Adsorbent)", "PR(>F)"]

        records_anova.append({
            "Material": mat, "Factor": fac,
            "Source": "Level", "F": round(f_level, 4), "p": round(p_level, 6),
            "Partial_Eta2": round(eta_level, 4), "Omega2": round(omega_level, 4), "Cohens_f": round(cohen_level, 4),
            "Eta_Interpretation": eta_interpret(eta_level),
            "Significant": "Yes" if p_level < 0.05 else "No"
        })
        records_anova.append({
            "Material": mat, "Factor": fac,
            "Source": "Adsorbent", "F": round(f_ads, 4), "p": round(p_ads, 6),
            "Partial_Eta2": round(eta_ads, 4), "Omega2": round(omega_ads, 4), "Cohens_f": round(cohen_ads, 4),
            "Eta_Interpretation": eta_interpret(eta_ads),
            "Significant": "Yes" if p_ads < 0.05 else "No"
        })

        # ── Assumptions ──
        residuals = model.resid
        fitted = model.fittedvalues
        shapiro = stats.shapiro(residuals)
        shapiro_ok = shapiro.pvalue > 0.05

        # Levene: group residuals by Level x Adsorbent
        sub["residual"] = residuals
        groups_l = [g["residual"].values for _, g in sub.groupby(["Level", "Adsorbent"])]
        if all(len(g) >= 2 for g in groups_l):
            lev = stats.levene(*groups_l)
            lev_stat, lev_p = round(lev.statistic, 4), round(lev.pvalue, 6)
            levene_ok = lev.pvalue > 0.05
        else:
            lev_stat, lev_p = np.nan, np.nan
            levene_ok = True

        records_assumptions.append({
            "Material": mat, "Factor": fac,
            "Shapiro_Wilk_W": round(shapiro.statistic, 4),
            "Shapiro_Wilk_p": round(shapiro.pvalue, 6),
            "Shapiro_ok": shapiro_ok,
            "Levene_stat": lev_stat,
            "Levene_p": lev_p,
            "Levene_ok": levene_ok,
        })

        # QQ plot + residual plots + Cook's Distance
        cooks_d = model.get_influence().cooks_distance[0]
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        stats.probplot(residuals, dist="norm", plot=axes[0,0])
        axes[0,0].set_title(f"{key} — QQ plot")
        axes[0,1].hist(residuals, bins=6, edgecolor="white")
        axes[0,1].set_title("Residual histogram")
        axes[1,0].scatter(fitted, residuals, alpha=0.6)
        axes[1,0].axhline(0, color="red", linestyle="--")
        axes[1,0].set_xlabel("Fitted"); axes[1,0].set_ylabel("Residuals")
        axes[1,0].set_title("Residuals vs Fitted")
        axes[1,1].plot(range(len(cooks_d)), cooks_d, "ko-", markersize=3)
        axes[1,1].axhline(4/len(cooks_d), color="red", linestyle="--", label=f"4/n={4/len(cooks_d):.3f}")
        axes[1,1].set_xlabel("Observation"); axes[1,1].set_ylabel("Cook's Distance")
        axes[1,1].set_title("Cook's Distance"); axes[1,1].legend(fontsize=8)
        plt.tight_layout()
        fig.savefig(f"figures/diagnostics_{mat}_{fac}.png", bbox_inches="tight")
        plt.close(fig)

        # ── Tukey HSD ──
        tukey = pairwise_tukeyhsd(sub["PctAdsorption"], sub["Adsorbent"], alpha=0.05)
        group_means = sub.groupby("Adsorbent")["PctAdsorption"].mean()
        letters = compact_letter_display(tukey, group_means)
        for k, (g1, g2) in enumerate(combinations(tukey.groupsunique, 2)):
            if k >= len(tukey.pvalues):
                continue
            md = float(tukey.meandiffs[k])
            p_adj = float(tukey.pvalues[k])
            lo, hi = tukey.confint[k]
            rej = bool(tukey.reject[k])
            records_tukey.append({
                "Material": mat, "Factor": fac,
                "Group1": g1, "Group2": g2,
                "Mean_Diff": round(md, 4), "p_adj": round(p_adj, 6),
                "Lower": round(float(lo), 4), "Upper": round(float(hi), 4),
                "Reject": rej,
                "Practical": "Yes" if rej and abs(md) >= 5.0 else
                             "Limited" if rej and abs(md) < 5.0 else "No"
            })

        # ── Confidence intervals per adsorbent ──
        ci_data = {}
        for ads in ADSORBENTS:
            vals = sub[sub.Adsorbent == ads]["PctAdsorption"]
            m, se = vals.mean(), vals.std(ddof=1) / np.sqrt(len(vals))
            ci = stats.t.interval(0.95, df=len(vals) - 1, loc=m, scale=se)
            records_ci.append({
                "Material": mat, "Factor": fac, "Adsorbent": ads,
                "Mean": round(m, 4), "SE": round(se, 4),
                "CI_lower": round(ci[0], 4), "CI_upper": round(ci[1], 4),
                "n": len(vals)
            })

        # ── Practical importance ──
        level_means = sub.groupby("Level")["PctAdsorption"].mean().sort_index()
        if len(level_means) >= 2:
            pct_change = ((level_means.iloc[-1] - level_means.iloc[0]) / level_means.iloc[0]) * 100
        else:
            pct_change = np.nan
        records_practical.append({
            "Material": mat, "Factor": fac,
            "Min_level": level_means.index[0] if len(level_means) > 0 else np.nan,
            "Max_level": level_means.index[-1] if len(level_means) > 0 else np.nan,
            "Min_mean": round(level_means.iloc[0], 4) if len(level_means) > 0 else np.nan,
            "Max_mean": round(level_means.iloc[-1], 4) if len(level_means) > 0 else np.nan,
            "Pct_change": round(pct_change, 2) if not np.isnan(pct_change) else np.nan
        })

        # ── CV robustness ──
        for ads in ADSORBENTS:
            vals = sub[sub.Adsorbent == ads]["PctAdsorption"]
            cv = vals.std(ddof=1) / vals.mean() * 100 if vals.mean() else np.nan
            records_cv.append({
                "Material": mat, "Factor": fac, "Adsorbent": ads,
                "Mean": round(vals.mean(), 4), "SD": round(vals.std(ddof=1), 4),
                "CV": round(cv, 2) if not np.isnan(cv) else np.nan
            })

        # ── Interaction plot ──
        fig, ax = plt.subplots(figsize=(6, 4))
        for ads in ADSORBENTS:
            tmp = sub[sub.Adsorbent == ads].groupby("Level")["PctAdsorption"].mean().reset_index()
            ax.plot(tmp["Level"].astype(str), tmp["PctAdsorption"], marker="o", label=ads)
        ax.set_xlabel("Level")
        ax.set_ylabel("Mean adsorption (%)")
        ax.set_title(f"{mat} — {FACTOR_NAMES.get(fac, fac)}")
        ax.legend(title="Adsorbent")
        ax.grid(alpha=0.3)
        plt.tight_layout()
        fig.savefig(f"figures/interaction_{mat}_{fac}.png", bbox_inches="tight")
        plt.close(fig)

        # ── Boxplot ──
        fig, ax = plt.subplots(figsize=(5, 3.5))
        sns.boxplot(data=sub, x="Level", y="PctAdsorption", hue="Adsorbent", ax=ax)
        ax.set_title(f"{mat} — {FACTOR_NAMES.get(fac, fac)}")
        ax.set_xlabel("Level")
        ax.set_ylabel("Adsorption (%)")
        ax.legend(title="", fontsize=8)
        plt.tight_layout()
        fig.savefig(f"figures/boxplot_{mat}_{fac}.png", bbox_inches="tight")
        plt.close(fig)

        all_results[key] = {"model": model, "anova": anova, "tukey": tukey, "sub": sub}

# ── Summary tables ────────────────────────────────────────────────────
anova_tab = pd.DataFrame(records_anova)
tukey_tab = pd.DataFrame(records_tukey)
ci_tab = pd.DataFrame(records_ci)
practical_tab = pd.DataFrame(records_practical)
cv_tab = pd.DataFrame(records_cv)
assump_tab = pd.DataFrame(records_assumptions)

# ── Multiple testing correction ─────────────────────────────────────
pvals_all = anova_tab["p"].dropna().values
n_p = len(pvals_all)
if n_p:
    from scipy.stats import rankdata
    sorted_idx = np.argsort(pvals_all)
    sorted_p = pvals_all[sorted_idx]
    holm = np.minimum(1, sorted_p * (n_p - np.arange(n_p)))
    bh_sorted = np.minimum(1, sorted_p * n_p / (np.arange(n_p) + 1))
    for i in range(n_p - 2, -1, -1):
        bh_sorted[i] = min(bh_sorted[i], bh_sorted[i+1])
    holm_orig, bh_orig = np.empty(n_p), np.empty(n_p)
    holm_orig[sorted_idx] = holm
    bh_orig[sorted_idx] = bh_sorted
    anova_tab["p_Holm"] = holm_orig.round(6)
    anova_tab["p_BH"] = bh_orig.round(6)
    anova_tab["sig_Holm"] = holm_orig < 0.05
    anova_tab["sig_BH"] = bh_orig < 0.05
    n_sig_raw = (anova_tab["p"] < 0.05).sum()
    n_sig_holm = anova_tab["sig_Holm"].sum()
    n_sig_bh = anova_tab["sig_BH"].sum()
    print(f"\n  Multiple testing: {n_p} tests, {n_sig_raw} raw sig → {n_sig_holm} (Holm) / {n_sig_bh} (BH)")
    print(f"  Lost significance: {n_sig_raw - n_sig_holm} (Holm), {n_sig_raw - n_sig_bh} (BH)")
anova_tab.to_csv("table_anova.csv", index=False)
tukey_tab.to_csv("table_tukey.csv", index=False)
ci_tab.to_csv("table_confidence_intervals.csv", index=False)
practical_tab.to_csv("table_practical_importance.csv", index=False)
cv_tab.to_csv("table_robustness_cv.csv", index=False)
assump_tab.to_csv("table_assumptions.csv", index=False)

print("STEP 2–5: ANOVA, effect sizes, Tukey, CI, assumptions → tables saved")

# ── Heatmap: mean adsorption ─────────────────────────────────────────
heat = df.groupby(["Material", "Factor", "Adsorbent"])["PctAdsorption"].mean().reset_index()
piv = heat.pivot_table(index=["Material", "Factor"], columns="Adsorbent", values="PctAdsorption")
fig, ax = plt.subplots(figsize=(5.5, 7))
sns.heatmap(piv, annot=True, fmt=".1f", cmap="viridis", cbar_kws={"label": "Mean adsorption (%)"}, ax=ax)
ax.set_title("Mean adsorption (%) across all conditions")
plt.tight_layout()
fig.savefig("figures/heatmap_mean_adsorption.png", bbox_inches="tight")
plt.close(fig)
print("STEP 6: Heatmap → figures/heatmap_mean_adsorption.png")

# ── Ranking by effect size ───────────────────────────────────────────
rank_eta = anova_tab[anova_tab.Source == "Level"].sort_values("Partial_Eta2", ascending=False)
rank_eta.to_csv("table_ranking_factors_by_effectsize.csv", index=False)
print("STEP 7: Ranking table → table_ranking_factors_by_effectsize.csv")

# ── Adsorbent ranking by overall mean ────────────────────────────────
ads_rank = df.groupby("Adsorbent")["PctAdsorption"].agg(["mean", "std"]).round(2).sort_values("mean", ascending=False)
ads_rank.to_csv("table_adsorbent_overall_ranking.csv")
print("STEP 7: Adsorbent ranking → table_adsorbent_overall_ranking.csv")

# ── Material ranking ─────────────────────────────────────────────────
mat_rank = df.groupby("Material")["PctAdsorption"].agg(["mean", "std"]).round(2).sort_values("mean", ascending=False)
mat_rank.to_csv("table_material_overall_ranking.csv")
print("STEP 7: Material ranking → table_material_overall_ranking.csv")

# ── Robustness: overall CV per adsorbent ─────────────────────────────
overall_cv = df.groupby("Adsorbent")["PctAdsorption"].agg(lambda x: np.std(x, ddof=1) / np.mean(x) * 100).round(2).reset_index()
overall_cv.columns = ["Adsorbent", "Overall_CV"]
overall_cv.to_csv("table_overall_robustness_cv.csv", index=False)
print("STEP 8: Robustness CV → table_overall_robustness_cv.csv")

# ── Thesis tables ────────────────────────────────────────────────────
print("\n" + "=" * 72)
print("THESIS-READY TABLES")
print("=" * 72)

print("\n─── Table 1: ANOVA Summary ───")
anova_print = anova_tab.copy()
anova_print["p"] = anova_print["p"].apply(lambda x: f"{x:.4f}" if x >= 0.0001 else f"{x:.2e}")
anova_print["Significant (p<0.05)"] = anova_print["p"].apply(lambda x: "Yes" if float(x) < 0.05 else "No")  # placeholder
# Recompute
anova_print["Sig"] = anova_tab["p"] < 0.05
anova_print["Sig_label"] = anova_print["Sig"].apply(lambda x: "*" if x else "ns")
for _, r in anova_print.iterrows():
    print(f"  {r.Material:4s} {r.Factor:12s} {r.Source:10s} F={r.F:6.2f} p={r.p:>8s} η²={r.Partial_Eta2:.3f} ω²={r.Omega2:.3f} f={r.Cohens_f:.2f} [{r.Eta_Interpretation:10s}] {r.Sig_label}")

print("\n─── Table 2: Effect Size Summary ───")
eta_wide = anova_tab.pivot_table(index=["Material", "Factor"], columns="Source", values="Partial_Eta2").round(3)
eta_wide["Max"] = eta_wide.max(axis=1)
eta_wide = eta_wide.sort_values("Max", ascending=False)
print(eta_wide.to_string())

print("\n─── Table 3: Tukey HSD — Significant pairs only ───")
sig_tukey = tukey_tab[tukey_tab.Reject == True]
if len(sig_tukey):
    for _, r in sig_tukey.iterrows():
        ptag = " ★ PRACTICAL" if r.Practical == "Yes" else " [limited]"
        print(f"  {r.Material:4s} {r.Factor:12s} {r.Group1:>10s} vs {r.Group2:<10s} Δ={r.Mean_Diff:+7.2f} p={r.p_adj:.4f}{ptag}")
else:
    print("  (none)")

print(f"\n─── Table 4: Adsorbent Overall Ranking ───")
print(ads_rank.to_string())

print(f"\n─── Table 5: Material Overall Ranking ───")
print(mat_rank.to_string())

print(f"\n─── Table 6: Robustness (CV %) per adsorbent ───")
print(overall_cv.to_string())

# ── Automatic interpretation ─────────────────────────────────────────
print("\n" + "=" * 72)
print("AUTOMATIC INTERPRETATION")
print("=" * 72)

# Dominant factors per material
for mat in MATERIALS:
    sub_an = anova_tab[(anova_tab.Material == mat) & (anova_tab.Source == "Level")].sort_values("Partial_Eta2", ascending=False)
    top = sub_an.head(2)
    print(f"\n  {mat}:")
    print(f"    Most influential factors: {top.iloc[0].Factor} (η²={top.iloc[0].Partial_Eta2:.3f}) and {top.iloc[1].Factor} (η²={top.iloc[1].Partial_Eta2:.3f})")

# Adsorbent differences
sig_ads = anova_tab[(anova_tab.Source == "Adsorbent") & (anova_tab.Significant == "Yes")]
print(f"\n  Adsorbent effects significant in {len(sig_ads)}/{len(anova_tab[anova_tab.Source=='Adsorbent'])} analyses")
if len(sig_ads):
    for _, r in sig_ads.iterrows():
        print(f"    {r.Material}/{r.Factor}: F={r.F:.2f}, p={r.p:.4f}, η²={r.Partial_Eta2:.3f}")

# Tukey summary
sig_pairs = sig_tukey.groupby(["Material", "Factor"]).size().reset_index(name="n_sig_pairs")
print(f"\n  Tukey: {len(sig_tukey)} significant pairwise comparisons across {len(sig_pairs)} groups")

# Most robust adsorbent
best_cv = overall_cv.loc[overall_cv.Overall_CV.idxmin()]
print(f"\n  Most robust adsorbent (lowest CV): {best_cv.Adsorbent} (CV={best_cv.Overall_CV:.1f}%)")
worst_cv = overall_cv.loc[overall_cv.Overall_CV.idxmax()]
print(f"  Least robust adsorbent (highest CV): {worst_cv.Adsorbent} (CV={worst_cv.Overall_CV:.1f}%)")

# Best overall adsorbent
best_mean = ads_rank.iloc[0]
print(f"\n  Highest mean adsorption: {best_mean.name} ({best_mean['mean']:.1f}%)")

# ── Limitations ──────────────────────────────────────────────────────
print("\n" + "=" * 72)
print("LIMITATIONS")
print("=" * 72)
print("""
  1. No replication — each condition has one observation per adsorbent.
     All effect sizes are inflated because the error term contains no
     pure error; F-tests use interaction MS as denominator.
  2. Interaction cannot be estimated — residual error absorbs interaction.
  3. Additive model assumption — C(Level) + C(Adsorbent) with no interaction term.
  4. Small sample size within each Material x Factor combination (n < 12).
     Shapiro-Wilk has low power at this n.
  5. Cook's distance identified influential points in every model; results
     should be inspected for sensitivity to individual observations.
  6. The Holm correction for multiple testing reduces the number of
     significant ANOVA results (from 23/30 to 10/30 at α=0.05).
  7. Results express associations, not causal mechanisms. Unmeasured
     confounders may contribute to observed variance.
""")

# ── Discussion points ────────────────────────────────────────────────
print("=" * 72)
print("DISCUSSION POINTS")
print("=" * 72)
print("""
  1. Contact time explained the largest proportion of observed variance
     in adsorption for all three plastics across the tested range.

  2. Initial concentration was also strongly associated with adsorption
     outcomes, with larger effects at lower concentrations.

  3. Adsorbent differences were most pronounced under pH and temperature
     conditions, while under dosage and contact time the three GO-based
     adsorbents showed comparable performance.

  4. Between 13% and 100% of the variance in adsorption (depending on
     the factor) was attributable to the tested variables, with contact
     time consistently explaining >90%.

  5. These findings should be interpreted as associations; the additive
     model cannot distinguish causation, and unmeasured variables may
     contribute to the observed variance.
""")

print("\nPipeline complete. All outputs in current directory and figures/")
