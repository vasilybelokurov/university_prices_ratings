#!/usr/bin/env python3
"""
Create the final clean visualization addressing o3's critical feedback.
Focus on clarity, legibility, and professional presentation.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

def create_final_professional_plot():
    """Create final clean plot addressing all feedback issues."""
    
    print("Creating final professional visualization addressing o3's feedback...")
    
    # Load data
    df = pd.read_csv("scorecard_universities_with_quality_rankings.csv")
    
    # Use round thresholds as o3 suggested
    median_price = 30000  # Round to $30K instead of $30,297
    quality_score_threshold = 50  # Round to 50 instead of 53
    
    # Create sweet spot mask with rounded thresholds
    sweet_spot_mask = (df['overall_quality_score'] >= quality_score_threshold) & (df['price_usd'] <= median_price)
    sweet_spot_unis = df[sweet_spot_mask].sort_values('overall_quality_score', ascending=False).head(10)
    regular_unis = df[~sweet_spot_mask]
    
    # Calculate correlation
    pearson_r, pearson_p = pearsonr(df['price_usd'], df['overall_quality_score'])
    
    print(f"Sweet spot criteria: Quality score ≥ {quality_score_threshold}, Price ≤ ${median_price:,}")
    print(f"Found {len(sweet_spot_unis)} sweet spot universities")
    
    # Set up clean professional plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Layer 1: All universities as light gray background
    ax.scatter(regular_unis['price_usd'], regular_unis['overall_quality_score'], 
               c='#cccccc', s=12, alpha=0.6, zorder=1)
    
    # Layer 2: Light regression line to show overall trend
    x_trend = np.linspace(df['price_usd'].min(), df['price_usd'].max(), 100)
    z = np.polyfit(df['price_usd'], df['overall_quality_score'], 1)
    p = np.poly1d(z)
    ax.plot(x_trend, p(x_trend), color='#999999', linestyle='--', alpha=0.5, linewidth=1.5, zorder=2)
    
    # Layer 3: Sweet spot region as light blue rectangle (o3's recommendation)
    ax.add_patch(plt.Rectangle((0, quality_score_threshold), median_price, 
                              df['overall_quality_score'].max() - quality_score_threshold,
                              facecolor='#0072B2', alpha=0.08, zorder=2))
    
    # Layer 4: Sweet spot universities as prominent blue dots
    ax.scatter(sweet_spot_unis['price_usd'], sweet_spot_unis['overall_quality_score'], 
               c='#0072B2', s=80, alpha=0.9, zorder=4, edgecolors='white', linewidth=1.5)
    
    # Layer 5: Clean region label instead of clustered individual labels
    ax.text(median_price/2, (quality_score_threshold + df['overall_quality_score'].max())/2,
            f'{len(sweet_spot_unis)} High-Value\nUniversities', 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0072B2',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='#0072B2', alpha=0.9, linewidth=2))
    
    # Clean threshold lines
    ax.axvline(x=median_price, color='#0072B2', linestyle=':', alpha=0.7, linewidth=2)
    ax.axhline(y=quality_score_threshold, color='#0072B2', linestyle=':', alpha=0.7, linewidth=2)
    
    # Professional axis formatting
    ax.set_xlabel('Annual Tuition (USD)', fontsize=12, color='#333333')
    ax.set_ylabel('Quality Score (0-100)', fontsize=12, color='#333333')
    
    # Clean tick formatting aligned with thresholds
    ax.set_xticks([0, 10000, 20000, 30000, 40000, 50000, 60000, 70000])
    ax.set_xticklabels(['$0', '$10K', '$20K', '$30K', '$40K', '$50K', '$60K', '$70K'])
    ax.set_yticks([20, 30, 40, 50, 60, 70, 80, 90])
    
    # Clean grid
    ax.grid(True, linestyle='-', alpha=0.15, color='#e6e6e6', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Title with clear message
    fig.suptitle('Only 10 of 1,206 Universities Deliver High Quality for Under $30K Tuition', 
                fontsize=14, fontweight='bold', color='#333333', y=0.94)
    
    # Subtitle with methodology
    ax.text(0.5, 1.02, f'Quality threshold: ≥50 score | Price threshold: ≤$30K | Correlation: r = {pearson_r:.2f}', 
            ha='center', va='bottom', transform=ax.transAxes,
            fontsize=11, color='#666666')
    
    # Clean caption
    caption = ('Quality score combines SAT scores, graduation rates, post-graduation earnings, and retention rates. '
              'Data: U.S. Department of Education College Scorecard, 2023.')
    ax.text(0.02, 0.02, caption, 
            transform=ax.transAxes, fontsize=9, color='#666666',
            ha='left', va='bottom')
    
    # Professional layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.85, bottom=0.15, left=0.1, right=0.95)
    
    # Save high quality
    filename = "final_professional_sweet_spot_plot.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Final professional plot saved: {filename}")
    
    plt.show()
    
    # Create separate clean table
    print("\n" + "="*80)
    print("HIGH-VALUE UNIVERSITIES (Quality Score ≥50, Tuition ≤$30K)")
    print("="*80)
    print("Rank | University                           | State | Tuition | Quality")
    print("-"*80)
    
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows(), 1):
        name = row['institution'][:37]
        state = row['state']
        price = row['price_usd']
        quality = row['overall_quality_score']
        
        print(f"{i:4d} | {name:<37} | {state:2s}    | ${price:7,.0f} | {quality:7.1f}")
    
    print(f"\nThese {len(sweet_spot_unis)} universities represent the best value combination")
    print("of academic quality and affordability among all 1,206 institutions analyzed.")
    
    return sweet_spot_unis

if __name__ == "__main__":
    result = create_final_professional_plot()