"""
Calculate Inter-Annotator Cohen's Kappa Agreement.

This script calculates Cohen's Kappa between the two annotators
and reports the mean Kappa across all categories.
"""

import pandas as pd
import os
import numpy as np
from sklearn.metrics import cohen_kappa_score

# File paths
ANNOTATOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'annotator_agreements')
ANNOTATOR_1_FILE = os.path.join(ANNOTATOR_DIR, 'annotator_1.csv')
ANNOTATOR_2_FILE = os.path.join(ANNOTATOR_DIR, 'annotator_2.csv')

# Debt categories
DEBT_CATEGORIES = [
    'Computing Management Debt',
    'IaC code debt',
    'Dependency management',
    'Security debt',
    'Networking debt',
    'environment-Based configuration debt',
    'monitoring and logging debt',
    'test debt'
]

def calculate_inter_annotator_kappa():
    """Calculate Inter-Annotator Cohen's Kappa."""
    
    print("=" * 80)
    print("Inter-Annotator Cohen's Kappa Agreement")
    print("=" * 80)
    
    # Load files
    print("\nLoading files...")
    ann1_df = pd.read_csv(ANNOTATOR_1_FILE)
    ann2_df = pd.read_csv(ANNOTATOR_2_FILE)
    
    total_instances = min(len(ann1_df), len(ann2_df))
    
    print(f"  Annotator 1: {len(ann1_df)} rows")
    print(f"  Annotator 2: {len(ann2_df)} rows")
    print(f"  Comparing: {total_instances} instances")
    
    # Calculate median values and Kappa for each category
    print("\n" + "=" * 80)
    print("Inter-Annotator Cohen's Kappa by Category")
    print("=" * 80)
    
    results = []
    
    for category in DEBT_CATEGORIES:
        if category not in ann1_df.columns or category not in ann2_df.columns:
            continue
        
        ann1_values = ann1_df[category][:total_instances].values
        ann2_values = ann2_df[category][:total_instances].values
        
        # Calculate inter-annotator Kappa
        kappa_inter = cohen_kappa_score(ann1_values, ann2_values)
        
        results.append({
            'category': category,
            'kappa_inter': kappa_inter
        })
        
        print(f"\n{category}:")
        print(f"  Inter-annotator Kappa: {kappa_inter:.4f}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    
    kappa_values = [r['kappa_inter'] for r in results]
    mean_kappa = np.mean(kappa_values)
    median_kappa = np.median(kappa_values)
    
    print(f"\nMean Inter-annotator Kappa: {mean_kappa:.4f}")
    print(f"Median Inter-annotator Kappa: {median_kappa:.4f}")
    
    # Detailed table
    print("\n" + "=" * 80)
    print("Detailed Results Table")
    print("=" * 80)
    
    print(f"\n{'Category':<45} {'Inter-Ann Kappa':>16}")
    print("-" * 65)
    
    for r in results:
        print(f"{r['category']:<45} {r['kappa_inter']:>16.4f}")
    
    print(f"\n{'MEAN':<45} {mean_kappa:>16.4f}")
    
    print("\n" + "=" * 80)
    print("Interpretation")
    print("=" * 80)
    
    print(f"\nMean Inter-annotator Kappa: {mean_kappa:.4f}")
    
    if mean_kappa >= 0.81:
        print("  → Almost Perfect agreement")
    elif mean_kappa >= 0.61:
        print("  → Substantial agreement")
    elif mean_kappa >= 0.41:
        print("  → Moderate agreement")
    else:
        print("  → Fair agreement")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    calculate_inter_annotator_kappa()
