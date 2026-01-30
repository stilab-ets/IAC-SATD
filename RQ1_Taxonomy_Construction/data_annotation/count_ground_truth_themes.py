"""
Count theme statistics in ground_truth_filtered.csv

This script provides counts and statistics for all themes/labels
in the ground truth dataset.
"""

import pandas as pd
import os
from collections import Counter

# File paths
GT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'ground_truth',
    'ground_truth_filtered.csv'
)

# Theme columns
THEME_COLUMNS = [f'Theme {i}' for i in range(1, 13)]

def count_theme_statistics():
    """Count and analyze theme statistics in ground truth."""
    
    print("=" * 80)
    print("Theme Count Statistics from Ground Truth")
    print("=" * 80)
    
    # Load file
    print(f"\nLoading file: {GT_FILE}")
    
    if not os.path.exists(GT_FILE):
        print(f"❌ File not found: {GT_FILE}")
        return
    
    df = pd.read_csv(GT_FILE)
    
    print(f"  Total instances: {len(df)}")
    print(f"  Total columns: {len(df.columns)}")
    
    # Count all themes
    print("\n" + "=" * 80)
    print("Counting Themes Across All Theme Columns")
    print("=" * 80)
    
    all_themes = []
    
    for col in THEME_COLUMNS:
        if col in df.columns:
            for val in df[col]:
                if pd.notna(val) and str(val).strip() != '' and str(val).strip().lower() != 'none':
                    all_themes.append(str(val).strip())
    
    theme_counts = Counter(all_themes)
    
    print(f"\nTotal theme occurrences: {len(all_themes)}")
    print(f"Unique themes: {len(theme_counts)}")
    
    # Sort by frequency
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Display statistics
    print("\n" + "=" * 80)
    print("Theme Frequency Distribution (Normalized by Instances)")
    print("=" * 80)
    
    total_instances = len(df)
    
    print(f"\n{'Rank':<6} {'Theme':<60} {'Count':>8} {'% of Instances':>15}")
    print("-" * 95)
    
    for rank, (theme, count) in enumerate(sorted_themes, 1):
        percentage = count / total_instances * 100
        print(f"{rank:<6} {theme:<60} {count:>8} {percentage:>14.1f}%")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    
    counts = [count for _, count in sorted_themes]
    
    print(f"\nTotal instances: {total_instances}")
    print(f"Total theme occurrences: {len(all_themes)}")
    print(f"Unique themes: {len(theme_counts)}")
    print(f"Average themes per instance: {len(all_themes) / total_instances:.2f}")
    print(f"\nMost common theme: {sorted_themes[0][0]} ({sorted_themes[0][1]} occurrences, {sorted_themes[0][1]/total_instances*100:.1f}% of instances)")
    print(f"Least common theme: {sorted_themes[-1][0]} ({sorted_themes[-1][1]} occurrences, {sorted_themes[-1][1]/total_instances*100:.1f}% of instances)")
    print(f"Average occurrences per theme: {sum(counts) / len(counts):.1f}")
    print(f"Median occurrences: {sorted(counts)[len(counts)//2]}")
    
    # Themes by frequency range
    print("\n" + "=" * 80)
    print("Themes by Frequency Range")
    print("=" * 80)
    
    ranges = [
        (100, float('inf'), 'Very High (≥100)'),
        (50, 99, 'High (50-99)'),
        (20, 49, 'Medium (20-49)'),
        (10, 19, 'Low (10-19)'),
        (1, 9, 'Very Low (1-9)')
    ]
    
    for min_val, max_val, label in ranges:
        count = len([c for c in counts if min_val <= c <= max_val])
        if count > 0:
            print(f"{label}: {count} themes")
    
    # Per-theme column statistics
    print("\n" + "=" * 80)
    print("Statistics by Theme Column")
    print("=" * 80)
    
    print(f"\n{'Theme Column':<15} {'Non-empty':>12} {'Unique Themes':>15}")
    print("-" * 45)
    
    for col in THEME_COLUMNS:
        if col in df.columns:
            non_empty = df[col].notna().sum()
            unique = df[col].nunique()
            print(f"{col:<15} {non_empty:>12} {unique:>15}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    count_theme_statistics()
