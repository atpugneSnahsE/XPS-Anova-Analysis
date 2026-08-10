import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import warnings
warnings.filterwarnings("ignore")

tidy = pd.read_csv("tidy_data.csv")

FACTOR_LABELS = {
    "ad_dosage": "Adsorbent dosage",
    "analyte": "Initial concentration",
    "pH": "pH",
    "Temp": "Temperature",
    "time": "Contact time",
}

anova_rows = []
tukey_rows = []

for material in ["PE", "PET", "PS"]:
    for factor in FACTOR_LABELS:
        sub = tidy[(tidy.Material == material) & (tidy.Factor == factor)].copy()
        sub["Level"] = sub["Level"].astype("category")
        sub["Adsorbent"] = sub["Adsorbent"].astype("category")

        # Two-way ANOVA WITHOUT replication (1 obs per Level x Adsorbent cell)
        # Additive model; residual = interaction/error term (standard "two-factor
        # without replication" design, same as Excel's Anova: Two-Factor Without Replication)
        model = ols("PctAdsorption ~ C(Level) + C(Adsorbent)", data=sub).fit()
        aov = sm.stats.anova_lm(model, typ=2)

        for factor_name in ["C(Level)", "C(Adsorbent)"]:
            anova_rows.append({
                "Material": material,
                "Factor": FACTOR_LABELS[factor],
                "Source": "Level (the variable itself)" if factor_name == "C(Level)" else "Adsorbent",
                "df": aov.loc[factor_name, "df"],
                "F": aov.loc[factor_name, "F"],
                "p_value": aov.loc[factor_name, "PR(>F)"],
                "Significant (p<0.05)": aov.loc[factor_name, "PR(>F)"] < 0.05,
            })

        # Tukey HSD post-hoc on Adsorbent (which adsorbent differs from which,
        # pooling across all levels of this factor)
        tukey = pairwise_tukeyhsd(sub["PctAdsorption"], sub["Adsorbent"], alpha=0.05)
        tukey_df = pd.DataFrame(tukey.summary().data[1:], columns=tukey.summary().data[0])
        tukey_df.insert(0, "Factor", FACTOR_LABELS[factor])
        tukey_df.insert(0, "Material", material)
        tukey_rows.append(tukey_df)

anova_results = pd.DataFrame(anova_rows)
tukey_results = pd.concat(tukey_rows, ignore_index=True)

anova_results.to_csv("anova_results.csv", index=False)
tukey_results.to_csv("tukey_results.csv", index=False)

print("=== TWO-WAY ANOVA (no replication) ===")
print(anova_results.to_string(index=False))
print("\n=== TUKEY HSD (Adsorbent comparisons) ===")
print(tukey_results.to_string(index=False))