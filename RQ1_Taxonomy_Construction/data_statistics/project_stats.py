import os

import pandas as pd

filtered_projects = pd.read_csv('./terraform_based_repos.csv')
comment_summary_df = pd.read_csv("./comment_summary.csv")

def summarize_column(df: pd.DataFrame, col: str) -> dict:
    """Return min/median/mean/max for a numeric column."""
    s = pd.to_numeric(df[col], errors="coerce")
    return {
        "min": s.min(),
        "median": s.median(),
        "mean": s.mean(),
        "max": s.max(),
    }

if __name__ == '__main__':

    # Columns to analyze
    columns_to_analyze = [
        "num_commits", 'num_contributors', 'age_months',
        "num_stars", 'num_forks', 'iac_total_blocks',
        'iac_total_depth', 'iac_total_loc'
    ]

    comment_summary = summarize_column(comment_summary_df, "num_meaningful_unique")

    # Calculate statistics (min, median, mean, max)
    statistics = filtered_projects[columns_to_analyze].agg(['min', 'median', 'mean', 'max']).round(2)

    # Format numbers: suppress .00
    def format_number(num):
        if isinstance(num, float):
            formatted = f"{num:,.2f}"
            return formatted.rstrip('0').rstrip('.') if formatted.endswith(".00") else formatted
        return f"{num:,}"

    # Generate LaTeX table
    latex_table = f"""
    \\begin{{table}}[h!]
        \\fontsize{{7}}{{6.25}}\\selectfont
        \\centering
        \\caption{{Statistics of the {len(filtered_projects)} Selected TF-based Projects}}
        \\label{{tab:statistics}}
        \\begin{{tabular}}{{lcccc}}
            \\toprule
            \\textbf{{Metric}} & \\textbf{{Min.}} & \\textbf{{Median($\\bar{{x}}$)}} & \\textbf{{Mean($\\mu$)}} & \\textbf{{Max.}} \\\\
            \\midrule
            Age (months) & {format_number(statistics['age_months']['min'])} & {format_number(statistics['age_months']['median'])} & {format_number(statistics['age_months']['mean'])} & {format_number(statistics['age_months']['max'])} \\\\
            Maintainers & {format_number(statistics['num_contributors']['min'])} & {format_number(statistics['num_contributors']['median'])} & {format_number(statistics['num_contributors']['mean'])} & {format_number(statistics['num_contributors']['max'])} \\\\
            Commits & {format_number(statistics['num_commits']['min'])} & {format_number(statistics['num_commits']['median'])} & {format_number(statistics['num_commits']['mean'])} & {format_number(statistics['num_commits']['max'])} \\\\
            Stars & {format_number(statistics['num_stars']['min'])} & {format_number(statistics['num_stars']['median'])} & {format_number(statistics['num_stars']['mean'])} & {format_number(statistics['num_stars']['max'])} \\\\
            Forks & {format_number(statistics['num_forks']['min'])} & {format_number(statistics['num_forks']['median'])} & {format_number(statistics['num_forks']['mean'])} & {format_number(statistics['num_forks']['max'])} \\\\
            TF Blocks & {format_number(statistics['iac_total_blocks']['min'])} & {format_number(statistics['iac_total_blocks']['median'])} & {format_number(statistics['iac_total_blocks']['mean'])} & {format_number(statistics['iac_total_blocks']['max'])} \\\\
            TF LOC & {format_number(statistics['iac_total_loc']['min'])} & {format_number(statistics['iac_total_loc']['median'])} & {format_number(statistics['iac_total_loc']['mean'])} & {format_number(statistics['iac_total_loc']['max'])} \\\\
            TF Comments & {format_number(comment_summary["min"])} & {format_number(comment_summary["median"])} & {format_number(comment_summary["mean"])} & {format_number(comment_summary["max"])} \\\\
            
            \\bottomrule
        \\end{{tabular}}
    \\end{{table}}
    """

    # Output the LaTeX table
    print(latex_table)
