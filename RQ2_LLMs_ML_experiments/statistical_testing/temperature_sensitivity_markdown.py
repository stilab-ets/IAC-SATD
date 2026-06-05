from pathlib import Path

import pandas as pd


SCENARIOS = {
    "zero_shots": {
        "title": "Zero-Shot LLMs",
        "models": ["chatgpt", "claude", "deepseek", "gemini", "gemma", "qwen"],
        "display": {
            "chatgpt": "ChatGPT Zero-Shot",
            "claude": "Claude Zero-Shot",
            "deepseek": "DeepSeek Zero-Shot",
            "gemini": "Gemini Zero-Shot",
            "gemma": "Gemma Zero-Shot",
            "qwen": "Qwen Zero-Shot",
        },
    },
    "few_shots": {
        "title": "Few-Shot RAG LLMs",
        "models": [
            "chatgpt_rag_openai_precomputed",
            "claude_rag_openai_precomputed",
            "deepseek_rag_openai_precomputed",
            "gemini_rag_openai_precomputed",
            "gemma_rag_openai_precomputed",
            "qwen_rag_openai_precomputed",
        ],
        "display": {
            "chatgpt_rag_openai_precomputed": "ChatGPT Few-Shot",
            "claude_rag_openai_precomputed": "Claude Few-Shot",
            "deepseek_rag_openai_precomputed": "DeepSeek Few-Shot",
            "gemini_rag_openai_precomputed": "Gemini Few-Shot",
            "gemma_rag_openai_precomputed": "Gemma Few-Shot",
            "qwen_rag_openai_precomputed": "Qwen Few-Shot",
        },
    },
}


def load_report(report_csv: Path) -> pd.DataFrame:
    return pd.read_csv(report_csv)


def format_metric_summary(report_df: pd.DataFrame, metric: str) -> dict:
    row = report_df[report_df["metric"] == metric].iloc[0]
    return {
        "best_temperature": float(row["best_temperature"]),
        "best_median": float(row["best_median"]),
        "worst_temperature": float(row["worst_temperature"]),
        "worst_median": float(row["worst_median"]),
        "median_gap": float(row["median_gap"]),
        "median_of_temperature_medians": float(row["median_of_temperature_medians"]),
    }


def build_summary_rows(base_dir: Path, scenario_key: str, models: list[str], display: dict[str, str]) -> list[dict]:
    rows = []
    for model_key in models:
        report_csv = base_dir / scenario_key / model_key / "Weighted" / "sensitivity_report.csv"
        report_df = load_report(report_csv)
        f1 = format_metric_summary(report_df, "f1-score")
        relative_f1_gap = (f1["median_gap"] / f1["median_of_temperature_medians"]) * 100 if f1["median_of_temperature_medians"] else 0.0
        rows.append(
            {
                "model": display[model_key],
                "best_temperature": f1["best_temperature"],
                "best_median": f1["best_median"],
                "worst_temperature": f1["worst_temperature"],
                "worst_median": f1["worst_median"],
                "absolute_gap": f1["median_gap"],
                "relative_gap_pct": relative_f1_gap,
            }
        )
    return rows


def build_analysis_paragraph(report_df: pd.DataFrame) -> str:
    precision = format_metric_summary(report_df, "precision")
    recall = format_metric_summary(report_df, "recall")
    f1 = format_metric_summary(report_df, "f1-score")
    relative_f1_gap = (f1["median_gap"] / f1["median_of_temperature_medians"]) * 100 if f1["median_of_temperature_medians"] else 0.0

    return (
        f"The median Weighted F1 varies from <strong>{f1['worst_median']:.3f}</strong> "
        f"at <strong>T={f1['worst_temperature']:.1f}</strong> to <strong>{f1['best_median']:.3f}</strong> "
        f"at <strong>T={f1['best_temperature']:.1f}</strong>, "
        f"yielding an absolute gap of <strong>{f1['median_gap']:.3f}</strong> "
        f"and a relative variation of <strong>{relative_f1_gap:.2f}%</strong>. "
        f"Weighted Precision varies by <strong>{precision['median_gap']:.3f}</strong> across temperatures, "
        f"and Weighted Recall varies by <strong>{recall['median_gap']:.3f}</strong>."
    )


def relative_posix(path: Path, start: Path) -> str:
    return path.relative_to(start).as_posix()


def render_model_cell(base_dir: Path, scenario_key: str, model_key: str, display_name: str) -> str:
    model_dir = base_dir / scenario_key / model_key / "Weighted"
    report_csv = model_dir / "sensitivity_report.csv"
    plot_png = model_dir / "temperature_lines_median.png"

    report_df = load_report(report_csv)
    analysis = build_analysis_paragraph(report_df)
    img_src = relative_posix(plot_png, base_dir)

    return (
        "<td valign=\"top\" width=\"33%\">\n"
        f"<p><strong>{display_name}</strong></p>\n"
        f"<img src=\"{img_src}\" alt=\"{display_name} weighted temperature sensitivity\" width=\"100%\">\n"
        f"<p>{analysis}</p>\n"
        "</td>"
    )


def render_summary_table(base_dir: Path, scenario_key: str, scenario_cfg: dict) -> str:
    rows = build_summary_rows(base_dir, scenario_key, scenario_cfg["models"], scenario_cfg["display"])
    lines = [
        f"### {scenario_cfg['title']} Summary",
        "",
        "| Model | Highest T | Highest Median W-F1 | Lowest T | Lowest Median W-F1 | Absolute Gap | Relative Variation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {row['best_temperature']:.1f} | {row['best_median']:.3f} | "
            f"{row['worst_temperature']:.1f} | {row['worst_median']:.3f} | {row['absolute_gap']:.3f} | {row['relative_gap_pct']:.2f}% |"
        )
    lines.append("")
    return "\n".join(lines)


def render_scenario_section(base_dir: Path, scenario_key: str, scenario_cfg: dict) -> str:
    title = scenario_cfg["title"]
    models = scenario_cfg["models"]
    display = scenario_cfg["display"]

    lines = [f"## {title}", "", "<table>", ""]

    for idx in range(0, len(models), 3):
        chunk = models[idx: idx + 3]
        lines.append("<tr>")
        for model_key in chunk:
            lines.append(render_model_cell(base_dir, scenario_key, model_key, display[model_key]))
        if len(chunk) < 3:
            for _ in range(3 - len(chunk)):
                lines.append("<td></td>")
        lines.append("</tr>")
        lines.append("")

    lines.append("</table>")
    lines.append("")
    return "\n".join(lines)


def build_markdown(base_dir: Path) -> str:
    parts = [
        "# Temperature Sensitivity Analysis",
        "",
        "This report summarizes the **first temperature sensitivity analysis** using **Weighted Precision, Weighted Recall, and Weighted F1-score** only.",
        "",
        "Method summary:",
        "- Each figure uses the **median** across the 5 folds at each temperature.",
        "- Sensitivity is interpreted from the **temperature medians across the different folds**.",
        "- Let `m(T)` denote the median Weighted F1 at temperature `T`.",
        "- The measures are computed as follows:",
        "",
        "```text",
        "Absolute gap = max_T m(T) - min_T m(T)",
        "",
        "Relative variation (%) = [Absolute gap / median_T m(T)] * 100",
        "```",
        "- The short analysis below each figure focuses on the practical gap in **Weighted F1** across temperatures.",
        "",
    ]

    for scenario_key, scenario_cfg in SCENARIOS.items():
        parts.append(render_summary_table(base_dir, scenario_key, scenario_cfg))
        parts.append(render_scenario_section(base_dir, scenario_key, scenario_cfg))

    return "\n".join(parts).rstrip() + "\n"


def build_reviewer_response(base_dir: Path) -> str:
    def scenario_paragraph(scenario_key: str, scenario_cfg: dict) -> str:
        rows = build_summary_rows(base_dir, scenario_key, scenario_cfg["models"], scenario_cfg["display"])
        abs_gaps = [row["absolute_gap"] for row in rows]
        rel_gaps = [row["relative_gap_pct"] for row in rows]
        max_abs = max(abs_gaps)
        min_abs = min(abs_gaps)
        max_rel = max(rel_gaps)
        min_rel = min(rel_gaps)
        most_stable = min(rows, key=lambda r: r["absolute_gap"])
        least_stable = max(rows, key=lambda r: r["absolute_gap"])

        return (
            f"For the {scenario_cfg['title'].lower()} setting, the median Weighted F1 variation across temperatures "
            f"ranges from {min_abs:.3f} to {max_abs:.3f} in absolute terms, corresponding to relative variation between "
            f"{min_rel:.2f}% and {max_rel:.2f}%. The most stable model in this setting is {most_stable['model']} "
            f"(absolute gap {most_stable['absolute_gap']:.3f}), while the largest observed variation appears for "
            f"{least_stable['model']} (absolute gap {least_stable['absolute_gap']:.3f})."
        )

    lines = [
        "# Reviewer Response Draft",
        "",
        "We thank the reviewer for pointing out that the original manuscript stated that temperature values were varied, but did not analyze their effect explicitly.",
        "",
        "In response, we conducted a dedicated temperature sensitivity analysis for the LLM-based models using the Weighted Precision, Weighted Recall, and Weighted F1-score results.",
        "",
        "Our revised analysis focuses on the median weighted values across the five folds at each tested temperature (`0.0` to `0.6`). For each model, we report the best and worst median Weighted F1 values, together with the absolute and relative variation across temperatures.",
        "",
        "Let `m(T)` denote the median Weighted F1 at temperature `T`.",
        "",
        "```text",
        "Absolute gap = max_T m(T) - min_T m(T)",
        "",
        "Relative variation (%) = [Absolute gap / median_T m(T)] * 100",
        "```",
        "",
        scenario_paragraph("zero_shots", SCENARIOS["zero_shots"]),
        "",
        scenario_paragraph("few_shots", SCENARIOS["few_shots"]),
        "",
        "Overall, the observed temperature-related variation is limited in practical magnitude for most models. We therefore interpret temperature as having a measurable but generally modest effect on weighted performance, rather than changing the main conclusions of the model comparisons.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    base_dir = Path(__file__).resolve().parent / "performance_analysis" / "temperature_sensitivity"
    output_md = base_dir / "weighted_temperature_sensitivity_report.md"
    output_response = base_dir / "reviewer_response_temperature_sensitivity.md"
    output_md.write_text(build_markdown(base_dir), encoding="utf-8")
    output_response.write_text(build_reviewer_response(base_dir), encoding="utf-8")
    print(f"[saved] {output_md}")
    print(f"[saved] {output_response}")


if __name__ == "__main__":
    main()
