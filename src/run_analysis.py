"""Run the SQL pipeline in DuckDB, fit a cost model, export tables and figures.

Usage (from the repository root):
    python src/run_analysis.py
"""
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import statsmodels.formula.api as smf

import style

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
SOURCE = "Medical Cost Personal Dataset, Lantz (2019), Machine Learning with R"
SEGMENTS = ["Non-smoker", "Smoker, BMI under 30", "Smoker, BMI 30+"]
USD = mtick.StrMethodFormatter("${x:,.0f}")


def run_sql(con):
    con.execute((SQL / "00_staging.sql").read_text())
    results = {}
    for path in sorted(SQL.glob("0[1-9]_*.sql")):
        df = con.execute(path.read_text()).df()
        df.to_csv(TABLES / f"{path.stem}.csv", index=False)
        results[path.stem] = df
    return results


def fit_models(members):
    """Compare a main-effects model with one that adds a smoker x obesity interaction."""
    members = members.assign(smoker=members.is_smoker.astype(int), obese=members.is_obese.astype(int))
    base = "charges ~ age + bmi + children + C(sex) + C(region) + smoker + obese"
    m1 = smf.ols(base, data=members).fit()
    m2 = smf.ols(base + " + smoker:obese", data=members).fit()
    fit = pd.DataFrame({
        "model": ["Main effects", "Main effects + smoker x obesity"],
        "r_squared": [round(m1.rsquared, 3), round(m2.rsquared, 3)],
        "adj_r_squared": [round(m1.rsquared_adj, 3), round(m2.rsquared_adj, 3)],
        "rmse_usd": [round(m1.mse_resid ** 0.5), round(m2.mse_resid ** 0.5)],
    })
    ci = m2.conf_int()
    coefs = pd.DataFrame({
        "term": m2.params.index,
        "coefficient_usd": m2.params.round(0).values,
        "ci_low": ci[0].round(0).values,
        "ci_high": ci[1].round(0).values,
        "p_value": m2.pvalues.round(4).values,
    })
    fit.to_csv(TABLES / "06_model_fit.csv", index=False)
    coefs.to_csv(TABLES / "07_model_coefficients.csv", index=False)
    return fit, coefs


def fig_age_scatter(members):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for i, seg in enumerate(SEGMENTS):
        d = members[members.risk_segment == seg]
        ax.scatter(d.age, d.charges, s=14, color=style.SERIES[i], alpha=0.75,
                   edgecolors=style.SURFACE, linewidths=0.6, label=f"{seg} (n={len(d)})")
    ax.yaxis.set_major_formatter(USD)
    ax.set_xlabel("Age")
    ax.set_ylabel("Annual charges")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, fontsize=9, borderaxespad=0.2)
    ax.set_title("Charges rise with age in three bands set by smoking and BMI", pad=30)
    style.finish(fig, FIGURES / "01_charges_by_age_segment.png", SOURCE)


def fig_segments(df):
    labels = [f"{s}\n{b}" for s, b in zip(df.smoking_status, df.bmi_group)]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    colors = [style.SERIES[0], style.SERIES[0], style.SERIES[1], style.SERIES[2]]
    ax.bar(labels, df.avg_charges, color=colors, width=0.55)
    for x, (v, m) in enumerate(zip(df.avg_charges, df.cost_multiple_vs_baseline)):
        ax.text(x, v + 700, f"${v:,.0f}\n{m:.1f}x", ha="center", fontsize=9, color=style.TEXT)
    ax.yaxis.set_major_formatter(USD)
    ax.set_ylim(0, df.avg_charges.max() * 1.2)
    ax.grid(axis="x", visible=False)
    ax.set_title("Obesity adds little cost alone but nearly doubles cost for smokers")
    style.finish(fig, FIGURES / "02_smoker_bmi_interaction.png", SOURCE)


def fig_concentration(df):
    d = df.dropna(subset=["pct_of_charges"]).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 3.4))
    y = range(len(d))
    ax.barh([i + 0.18 for i in y], d.pct_of_members, height=0.34, color=style.NEUTRAL, label="Share of members")
    ax.barh([i - 0.18 for i in y], d.pct_of_charges, height=0.34, color=style.SERIES[0], label="Share of charges")
    for i, (m, c) in enumerate(zip(d.pct_of_members, d.pct_of_charges)):
        ax.text(m + 0.8, i + 0.18, f"{m:.0f}%", va="center", fontsize=8, color=style.TEXT_2)
        ax.text(c + 0.8, i - 0.18, f"{c:.0f}%", va="center", fontsize=8, color=style.TEXT)
    ax.set_yticks(list(y), d.member_group)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.set_xlim(0, 65)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=9, borderaxespad=0.2)
    ax.set_title("A small group of members drives most of the cost", pad=28)
    style.finish(fig, FIGURES / "03_cost_concentration.png", SOURCE)


def main():
    style.apply()
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    r = run_sql(con)
    members = con.execute("SELECT * FROM stg_members_segmented").df()
    fit, coefs = fit_models(members)
    fig_age_scatter(members)
    fig_segments(r["03_risk_segments"])
    fig_concentration(r["02_cost_concentration"])
    for name, df in {**r, "model_fit": fit, "coefficients": coefs}.items():
        print(f"\n== {name} ==\n{df.to_string(index=False)}")


if __name__ == "__main__":
    main()
