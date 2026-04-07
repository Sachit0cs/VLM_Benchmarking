#!/usr/bin/env python3
"""Generate a detailed perturbation report with multiple visualizations.

Input JSON schema (example):
{
  "clip": {"asr": 0.03, "ods": 0.06, "sbr": 0.0, "pairs": 300},
  "resnet18": {"asr": 0.14, "ods": 0.07, "sbr": 0.0, "pairs": 300}
}

Usage:
  python scripts/generate_perturbation_report.py \
    --input temp/eval_perturb_20260407_173401_metrics.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

try:
  from reportlab.lib import colors
  from reportlab.lib.pagesizes import A4
  from reportlab.lib.styles import getSampleStyleSheet
  from reportlab.platypus import Image as RLImage
  from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
  HAS_REPORTLAB = True
except ImportError:
  HAS_REPORTLAB = False


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def load_metrics(input_path: Path) -> pd.DataFrame:
    with input_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, dict) or not payload:
        raise ValueError("Input JSON must be a non-empty object keyed by model name.")

    rows: List[Dict[str, float]] = []
    for model_name, metrics in payload.items():
        if not isinstance(metrics, dict):
            continue

        rows.append(
            {
                "model": str(model_name),
                "asr": max(0.0, min(1.0, _safe_float(metrics.get("asr")))),
                "ods": max(0.0, min(1.0, _safe_float(metrics.get("ods")))),
                "sbr": max(0.0, min(1.0, _safe_float(metrics.get("sbr")))),
                "pairs": max(0.0, _safe_float(metrics.get("pairs"))),
            }
        )

    if not rows:
        raise ValueError("No valid model metrics found in JSON file.")

    df = pd.DataFrame(rows)

    # Weighted risk index; higher values indicate weaker robustness.
    df["risk_score"] = (
        0.55 * df["asr"] +
        0.35 * df["ods"] +
        0.10 * df["sbr"]
    )
    df["robustness_score"] = 1.0 - df["risk_score"]

    pairs_nonzero = df["pairs"].replace(0, np.nan)
    df["attack_successes"] = df["asr"] * pairs_nonzero
    df["drift_events"] = df["ods"] * pairs_nonzero
    df["semantic_breaks"] = df["sbr"] * pairs_nonzero
    df[["attack_successes", "drift_events", "semantic_breaks"]] = df[
        ["attack_successes", "drift_events", "semantic_breaks"]
    ].fillna(0.0)

    # $1000$-pair normalized projection for easier cross-run comparison.
    df["proj_successes_per_1000"] = df["asr"] * 1000.0
    df["proj_drift_per_1000"] = df["ods"] * 1000.0

    if len(df) > 1:
        z = (df["risk_score"] - df["risk_score"].mean()) / df["risk_score"].std(ddof=0)
        df["risk_zscore"] = z
    else:
        df["risk_zscore"] = 0.0

    df = df.sort_values("risk_score", ascending=False).reset_index(drop=True)
    df["risk_rank"] = np.arange(1, len(df) + 1)

    return df


def _save_fig(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def create_plots(df: pd.DataFrame, plots_dir: Path) -> List[Tuple[str, str, str]]:
    plots_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="talk")

    outputs: List[Tuple[str, str, str]] = []

    # 1) Grouped metric comparison.
    fig, ax = plt.subplots(figsize=(13, 6))
    melt = df.melt(id_vars=["model"], value_vars=["asr", "ods", "sbr"], var_name="metric", value_name="value")
    sns.barplot(data=melt, x="model", y="value", hue="metric", ax=ax)
    ax.set_title("Core Metric Comparison by Model")
    ax.set_ylabel("Rate")
    ax.set_xlabel("Model")
    ax.set_ylim(0, max(0.2, melt["value"].max() * 1.2))
    ax.tick_params(axis="x", rotation=25)
    p = plots_dir / "01_metric_comparison.png"
    _save_fig(fig, p)
    outputs.append(("Core Metric Comparison", "01_metric_comparison.png", "Side-by-side ASR, ODS, and SBR for each model."))

    # 2) Risk ranking bar chart.
    fig, ax = plt.subplots(figsize=(12, 6))
    ordered = df.sort_values("risk_score", ascending=False)
    sns.barplot(data=ordered, x="model", y="risk_score", hue="model", palette="Reds_r", legend=False, ax=ax)
    ax.set_title("Weighted Risk Score Ranking (Higher = More Vulnerable)")
    ax.set_ylabel("Risk Score")
    ax.set_xlabel("Model")
    ax.tick_params(axis="x", rotation=25)
    for i, val in enumerate(ordered["risk_score"]):
        ax.text(i, val + 0.004, f"{val:.3f}", ha="center", va="bottom", fontsize=10)
    p = plots_dir / "02_risk_ranking.png"
    _save_fig(fig, p)
    outputs.append(("Risk Ranking", "02_risk_ranking.png", "Composite vulnerability score with weighted metrics."))

    # 3) Robustness score chart.
    fig, ax = plt.subplots(figsize=(12, 6))
    ordered_r = df.sort_values("robustness_score", ascending=False)
    sns.barplot(data=ordered_r, x="model", y="robustness_score", hue="model", palette="Greens", legend=False, ax=ax)
    ax.set_title("Robustness Score by Model (Higher = Better)")
    ax.set_ylabel("Robustness Score")
    ax.set_xlabel("Model")
    ax.tick_params(axis="x", rotation=25)
    ax.set_ylim(0, 1.0)
    p = plots_dir / "03_robustness_scores.png"
    _save_fig(fig, p)
    outputs.append(("Robustness Scores", "03_robustness_scores.png", "Inverse of weighted risk for easy model ranking."))

    # 4) ASR vs ODS scatter bubble plot.
    fig, ax = plt.subplots(figsize=(10, 8))
    size = np.maximum(df["pairs"], 1.0) * 2.5
    sc = ax.scatter(df["asr"], df["ods"], s=size, c=df["risk_score"], cmap="magma", alpha=0.8, edgecolor="black")
    for _, row in df.iterrows():
        ax.annotate(row["model"], (row["asr"], row["ods"]), xytext=(6, 6), textcoords="offset points", fontsize=10)
    ax.set_title("ASR vs ODS (Bubble Size = Pair Count)")
    ax.set_xlabel("ASR")
    ax.set_ylabel("ODS")
    cb = fig.colorbar(sc, ax=ax)
    cb.set_label("Risk Score")
    p = plots_dir / "04_asr_ods_bubble.png"
    _save_fig(fig, p)
    outputs.append(("ASR-ODS Bubble Plot", "04_asr_ods_bubble.png", "Relationship between attack success and output drift."))

    # 5) Metric heatmap.
    fig, ax = plt.subplots(figsize=(11, 5))
    heat_df = df.set_index("model")[["asr", "ods", "sbr", "risk_score", "robustness_score"]]
    sns.heatmap(heat_df, annot=True, fmt=".3f", cmap="YlOrRd", linewidths=0.4, cbar_kws={"label": "Score"}, ax=ax)
    ax.set_title("Model-by-Metric Heatmap")
    ax.set_xlabel("Metric")
    ax.set_ylabel("Model")
    p = plots_dir / "05_metric_heatmap.png"
    _save_fig(fig, p)
    outputs.append(("Metric Heatmap", "05_metric_heatmap.png", "Consolidated intensity map across all key metrics."))

    # 6) Correlation matrix.
    fig, ax = plt.subplots(figsize=(8, 6))
    corr = df[["asr", "ods", "sbr", "risk_score", "robustness_score", "pairs"]].corr(numeric_only=True)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0.0, linewidths=0.4, ax=ax)
    ax.set_title("Metric Correlation Structure")
    p = plots_dir / "06_correlation_heatmap.png"
    _save_fig(fig, p)
    outputs.append(("Correlation Heatmap", "06_correlation_heatmap.png", "Linear relationships between attack and robustness metrics."))

    # 7) Radar plot for normalized profile.
    categories = ["asr", "ods", "sbr", "risk_score"]
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, polar=True)
    norm_df = df.copy()
    for col in categories:
        max_v = max(norm_df[col].max(), 1e-9)
        norm_df[col] = norm_df[col] / max_v
    for _, row in norm_df.iterrows():
        values = [row[c] for c in categories]
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=row["model"])
        ax.fill(angles, values, alpha=0.08)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([c.upper() for c in categories])
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.5", "0.75", "1.0"])
    ax.set_title("Normalized Vulnerability Profiles (Radar)", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.15), frameon=False)
    p = plots_dir / "07_radar_profiles.png"
    _save_fig(fig, p)
    outputs.append(("Radar Profiles", "07_radar_profiles.png", "Normalized per-model vulnerability signature."))

    # 8) Parallel coordinates.
    fig, ax = plt.subplots(figsize=(12, 7))
    par = df[["model", "asr", "ods", "sbr", "risk_score", "robustness_score"]].copy()
    scaled = par.copy()
    for col in ["asr", "ods", "sbr", "risk_score", "robustness_score"]:
        cmin, cmax = scaled[col].min(), scaled[col].max()
        if cmax - cmin > 1e-9:
            scaled[col] = (scaled[col] - cmin) / (cmax - cmin)
        else:
            scaled[col] = 0.5
    from pandas.plotting import parallel_coordinates
    parallel_coordinates(scaled, "model", colormap=plt.cm.tab10, ax=ax, alpha=0.8)
    ax.set_title("Parallel Coordinates of Scaled Metrics")
    ax.set_ylabel("Scaled Value")
    ax.set_xlabel("Metric Axis")
    ax.legend(loc="upper right", frameon=False)
    p = plots_dir / "08_parallel_coordinates.png"
    _save_fig(fig, p)
    outputs.append(("Parallel Coordinates", "08_parallel_coordinates.png", "Multi-metric trajectory of each model on a normalized axis."))

    # 9) Expected events per 1000 pairs.
    fig, ax = plt.subplots(figsize=(12, 6))
    evt = df.melt(
        id_vars=["model"],
        value_vars=["proj_successes_per_1000", "proj_drift_per_1000"],
        var_name="projection_type",
        value_name="events",
    )
    evt["projection_type"] = evt["projection_type"].map(
        {
            "proj_successes_per_1000": "Projected Attack Successes",
            "proj_drift_per_1000": "Projected Drift Events",
        }
    )
    sns.barplot(data=evt, x="model", y="events", hue="projection_type", ax=ax)
    ax.set_title("Projected Failure Events per 1000 Pairs")
    ax.set_ylabel("Events / 1000")
    ax.set_xlabel("Model")
    ax.tick_params(axis="x", rotation=25)
    p = plots_dir / "09_projected_events.png"
    _save_fig(fig, p)
    outputs.append(("Projected Failure Events", "09_projected_events.png", "Normalized operational-risk projection per 1000 pairs."))

    # 10) Gap-to-best robustness lollipop chart.
    fig, ax = plt.subplots(figsize=(12, 6))
    best = df["robustness_score"].max()
    gap = best - df["robustness_score"]
    x = np.arange(len(df))
    ax.hlines(y=x, xmin=0, xmax=gap, color="#4c72b0", alpha=0.8, linewidth=2)
    ax.plot(gap, x, "o", color="#dd8452", markersize=8)
    ax.set_yticks(x)
    ax.set_yticklabels(df["model"])
    ax.invert_yaxis()
    ax.set_xlabel("Gap to Best Robustness")
    ax.set_title("Model Distance from Best Robustness")
    p = plots_dir / "10_gap_to_best.png"
    _save_fig(fig, p)
    outputs.append(("Gap-to-Best", "10_gap_to_best.png", "How far each model is from the strongest observed robustness."))

    return outputs


def _pct(v: float) -> str:
    return f"{v * 100:.2f}%"


def _table_html(df: pd.DataFrame) -> str:
    display = df[[
        "risk_rank", "model", "pairs", "asr", "ods", "sbr", "risk_score", "robustness_score",
        "proj_successes_per_1000", "proj_drift_per_1000", "risk_zscore"
    ]].copy()
    display = display.rename(columns={
        "risk_rank": "Rank (Risk)",
        "model": "Model",
        "pairs": "Pairs",
        "asr": "ASR",
        "ods": "ODS",
        "sbr": "SBR",
        "risk_score": "Risk Score",
        "robustness_score": "Robustness",
        "proj_successes_per_1000": "Projected Successes / 1000",
        "proj_drift_per_1000": "Projected Drift / 1000",
        "risk_zscore": "Risk Z-Score",
    })

    for col in ["ASR", "ODS", "SBR", "Risk Score", "Robustness"]:
        display[col] = display[col].map(lambda x: f"{x:.4f}")
    display["Pairs"] = display["Pairs"].map(lambda x: f"{x:.0f}")
    display["Projected Successes / 1000"] = display["Projected Successes / 1000"].map(lambda x: f"{x:.1f}")
    display["Projected Drift / 1000"] = display["Projected Drift / 1000"].map(lambda x: f"{x:.1f}")
    display["Risk Z-Score"] = display["Risk Z-Score"].map(lambda x: f"{x:.3f}")

    return display.to_html(index=False, escape=True, classes="metrics-table")


def write_html_report(
    report_path: Path,
    source_json: Path,
    df: pd.DataFrame,
    plot_specs: List[Tuple[str, str, str]],
) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    worst = df.sort_values("risk_score", ascending=False).iloc[0]
    best = df.sort_values("robustness_score", ascending=False).iloc[0]
    avg_asr = float(df["asr"].mean())
    avg_ods = float(df["ods"].mean())
    avg_sbr = float(df["sbr"].mean())
    avg_risk = float(df["risk_score"].mean())
    spread = float(df["risk_score"].max() - df["risk_score"].min())

    cards = [
        ("Models Evaluated", f"{len(df)}"),
        ("Average ASR", _pct(avg_asr)),
        ("Average ODS", _pct(avg_ods)),
        ("Average SBR", _pct(avg_sbr)),
        ("Average Risk", f"{avg_risk:.4f}"),
        ("Risk Spread", f"{spread:.4f}"),
    ]

    card_html = "".join(
        f"<div class='card'><h3>{title}</h3><p>{value}</p></div>" for title, value in cards
    )

    plots_html = ""
    for idx, (title, filename, note) in enumerate(plot_specs, start=1):
        plots_html += (
            f"<section class='plot'>"
            f"<h3>{idx}. {title}</h3>"
            f"<p>{note}</p>"
            f"<img src='./plots/{filename}' alt='{title}' />"
            f"</section>"
        )

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Perturbation Metrics Report</title>
  <style>
    :root {{
      --bg: #f4efe8;
      --panel: #fffdf9;
      --ink: #1f2933;
      --accent: #b54d2e;
      --accent-2: #3b7a57;
      --line: #decfbc;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Palatino Linotype", "Book Antiqua", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at 20% 10%, #fbead5 0%, transparent 35%),
        radial-gradient(circle at 80% 0%, #e9f3e5 0%, transparent 30%),
        var(--bg);
      line-height: 1.45;
    }}
    .wrap {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px;
    }}
    .hero {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 22px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.06);
      margin-bottom: 20px;
    }}
    h1 {{ margin: 0 0 10px; color: var(--accent); font-size: 2rem; }}
    h2 {{ color: #3a4a5a; margin-top: 28px; }}
    h3 {{ color: #2d3f52; margin-bottom: 6px; }}
    .meta {{ font-size: 0.95rem; color: #465766; }}
    .cards {{
      margin-top: 16px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 12px;
    }}
    .card {{
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fff;
      padding: 12px;
    }}
    .card h3 {{ margin: 0 0 4px; font-size: 0.95rem; color: #5d6d79; }}
    .card p {{ margin: 0; font-size: 1.15rem; font-weight: 700; color: #1f2933; }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    }}
    .metrics-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.92rem;
      overflow: hidden;
    }}
    .metrics-table th, .metrics-table td {{
      border: 1px solid var(--line);
      padding: 8px;
      text-align: center;
    }}
    .metrics-table th {{
      background: #f7efe4;
      color: #314558;
      position: sticky;
      top: 0;
    }}
    .plot {{
      border: 1px solid var(--line);
      border-radius: 12px;
      background: #fff;
      padding: 14px;
      margin: 16px 0;
    }}
    .plot img {{ width: 100%; border-radius: 8px; border: 1px solid #ebe1d3; }}
    .insight {{
      border-left: 4px solid var(--accent-2);
      background: #f2f8f1;
      padding: 10px 14px;
      margin: 10px 0;
      border-radius: 8px;
    }}
    @media (max-width: 760px) {{
      .wrap {{ padding: 14px; }}
      h1 {{ font-size: 1.55rem; }}
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <section class=\"hero\">
      <h1>Perturbation Evaluation Report</h1>
      <div class=\"meta\">
        Source file: {source_json}<br/>
        Generated at: {now}<br/>
        Report scope: model-level perturbation robustness metrics and comparative risk analytics
      </div>
      <div class=\"cards\">{card_html}</div>
    </section>

    <section class=\"panel\">
      <h2>Executive Summary</h2>
      <p>
        The most vulnerable model by weighted perturbation risk is <strong>{worst['model']}</strong>
        with risk score <strong>{worst['risk_score']:.4f}</strong>.
        The strongest model by robustness is <strong>{best['model']}</strong>
        with robustness score <strong>{best['robustness_score']:.4f}</strong>.
      </p>
      <div class=\"insight\">Average ASR is {_pct(avg_asr)}, indicating mean susceptibility to perturbation-triggered prediction changes.</div>
      <div class=\"insight\">Average ODS is {_pct(avg_ods)}, capturing output instability under perturbation.</div>
      <div class=\"insight\">Risk spread is {spread:.4f}, measuring separation between strongest and weakest models under this perturbation setup.</div>
    </section>

    <section class=\"panel\">
      <h2>Detailed Metric Table</h2>
      {_table_html(df)}
    </section>

    <section class=\"panel\">
      <h2>Visual Analysis</h2>
      {plots_html}
    </section>
  </div>
</body>
</html>
"""

    report_path.write_text(html, encoding="utf-8")


def write_pdf_report(
    pdf_path: Path,
    source_json: Path,
    df: pd.DataFrame,
    plot_specs: List[Tuple[str, str, str]],
    plots_dir: Path,
) -> bool:
    if not HAS_REPORTLAB:
        return False

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    story = []

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worst = df.sort_values("risk_score", ascending=False).iloc[0]
    best = df.sort_values("robustness_score", ascending=False).iloc[0]

    story.append(Paragraph("Perturbation Evaluation Report", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Source file: {source_json}", styles["Normal"]))
    story.append(Paragraph(f"Generated at: {now}", styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    story.append(Paragraph(
        (
            f"Most vulnerable model: <b>{worst['model']}</b> "
            f"(risk score {worst['risk_score']:.4f}). "
            f"Most robust model: <b>{best['model']}</b> "
            f"(robustness {best['robustness_score']:.4f})."
        ),
        styles["Normal"],
    ))
    story.append(Paragraph(f"Average ASR: {_pct(float(df['asr'].mean()))}", styles["Normal"]))
    story.append(Paragraph(f"Average ODS: {_pct(float(df['ods'].mean()))}", styles["Normal"]))
    story.append(Paragraph(f"Average SBR: {_pct(float(df['sbr'].mean()))}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Detailed Metric Table", styles["Heading2"]))
    table_df = df[[
        "risk_rank", "model", "pairs", "asr", "ods", "sbr", "risk_score", "robustness_score",
        "proj_successes_per_1000", "proj_drift_per_1000", "risk_zscore"
    ]].copy()
    table_data = [[
        "Rank", "Model", "Pairs", "ASR", "ODS", "SBR", "Risk", "Robust", "Succ/1000", "Drift/1000", "Z"
    ]]
    for _, r in table_df.iterrows():
        table_data.append([
            f"{int(r['risk_rank'])}",
            str(r["model"]),
            f"{r['pairs']:.0f}",
            f"{r['asr']:.4f}",
            f"{r['ods']:.4f}",
            f"{r['sbr']:.4f}",
            f"{r['risk_score']:.4f}",
            f"{r['robustness_score']:.4f}",
            f"{r['proj_successes_per_1000']:.1f}",
            f"{r['proj_drift_per_1000']:.1f}",
            f"{r['risk_zscore']:.3f}",
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[28, 70, 40, 38, 38, 38, 40, 45, 52, 52, 28],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0e1cc")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#203247")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c8b9a7")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#faf5ee")]),
    ]))
    story.append(table)
    story.append(PageBreak())

    story.append(Paragraph("Visual Analysis", styles["Heading1"]))
    story.append(Spacer(1, 8))

    for idx, (title, filename, note) in enumerate(plot_specs, start=1):
        plot_path = plots_dir / filename
        if not plot_path.exists():
            continue

        story.append(Paragraph(f"{idx}. {title}", styles["Heading2"]))
        story.append(Paragraph(note, styles["Normal"]))
        story.append(Spacer(1, 6))
        img = RLImage(str(plot_path), width=520, height=310)
        story.append(img)
        story.append(Spacer(1, 8))
        if idx < len(plot_specs):
            story.append(PageBreak())

    doc.build(story)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate detailed perturbation HTML/PDF report with many plots.")
    parser.add_argument("--input", required=True, help="Path to perturbation metrics JSON file.")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to save report. Defaults to the input file directory.",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Output report base name. Defaults to '<input_stem>_report_<timestamp>'.",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir = Path(args.output_dir).resolve() if args.output_dir else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = args.name if args.name else f"{input_path.stem}_report_{stamp}"

    report_path = output_dir / f"{base_name}.html"
    pdf_path = output_dir / f"{base_name}.pdf"
    plots_dir = output_dir / "plots"

    df = load_metrics(input_path)
    plot_specs = create_plots(df, plots_dir)
    write_html_report(report_path=report_path, source_json=input_path, df=df, plot_specs=plot_specs)
    pdf_ok = write_pdf_report(pdf_path=pdf_path, source_json=input_path, df=df, plot_specs=plot_specs, plots_dir=plots_dir)

    csv_path = output_dir / f"{base_name}_summary.csv"
    df.to_csv(csv_path, index=False)

    print(f"Report saved: {report_path}")
    if pdf_ok:
        print(f"PDF report saved: {pdf_path}")
    else:
        print("PDF report skipped: reportlab is not installed in this environment.")
    print(f"Summary CSV saved: {csv_path}")
    print(f"Plot directory: {plots_dir}")


if __name__ == "__main__":
    main()
