#!/usr/bin/env python3
"""
Create a clean, professional visualization following o3's best practices.
Single scatter plot with clear message: "Which universities offer high quality at reasonable price?"
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text
from scipy.stats import pearsonr

def create_professional_sweet_spot_plot():
    """Create a clean, professional plot following o3's design principles."""
    
    print("Creating professional visualization following best practices...")
    
    # Load data
    df = pd.read_csv("scorecard_universities_with_quality_rankings.csv")
    
    # Define sweet spot criteria (top 25% quality, below median price)
    median_price = df['price_usd'].median()
    top_25_quality_threshold = df['quality_ranking'].quantile(0.25)
    
    # Create sweet spot mask
    sweet_spot_mask = (df['quality_ranking'] <= top_25_quality_threshold) & (df['price_usd'] <= median_price)
    sweet_spot_unis = df[sweet_spot_mask].sort_values('quality_ranking').head(10)
    regular_unis = df[~sweet_spot_mask]
    
    # Calculate correlation for subtitle
    pearson_r, pearson_p = pearsonr(df['quality_ranking'], df['price_usd'])
    
    print(f"Sweet spot criteria: Quality rank ≤ {top_25_quality_threshold:.0f}, Price ≤ ${median_price:,.0f}")
    print(f"Found {len(sweet_spot_unis)} sweet spot universities to highlight")
    
    # Set up the plot with professional styling
    plt.style.use('default')  # Clean slate
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Layer 1: Context - all other universities as light gray dots
    ax.scatter(regular_unis['price_usd'], regular_unis['overall_quality_score'], 
               c='#9d9d9d', s=8, alpha=0.25, zorder=1)
    
    # Layer 2: Sweet spot universities - larger, saturated blue
    ax.scatter(sweet_spot_unis['price_usd'], sweet_spot_unis['overall_quality_score'], 
               c='#0072B2', s=60, alpha=0.9, zorder=3, edgecolors='white', linewidth=0.5)
    
    # Layer 3: Sweet spot region (optional but powerful)
    ax.axvline(x=median_price, color='#0072B2', linestyle=':', alpha=0.4, linewidth=1.5)
    ax.text(median_price + 1000, ax.get_ylim()[1] * 0.95, 
            f'Reasonable Price\n≤ ${median_price:,.0f}', 
            color='#0072B2', fontsize=9, ha='left', va='top',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#0072B2', alpha=0.8))
    
    # Quality threshold line
    # Convert quality ranking to quality score threshold for visualization
    quality_score_threshold = df[df['quality_ranking'] <= top_25_quality_threshold]['overall_quality_score'].min()
    ax.axhline(y=quality_score_threshold, color='#0072B2', linestyle=':', alpha=0.4, linewidth=1.5)
    ax.text(ax.get_xlim()[0] + 2000, quality_score_threshold + 1, 
            f'High Quality\n≥ {quality_score_threshold:.0f} Score', 
            color='#0072B2', fontsize=9, ha='left', va='bottom',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#0072B2', alpha=0.8))
    
    # Labels for sweet spot universities - with automatic repulsion
    texts = []
    for _, row in sweet_spot_unis.iterrows():
        # Shorten long names
        name = row['institution']
        if len(name) > 25:
            # Smart shortening for common patterns
            name = name.replace('University of ', 'Univ. of ')
            name = name.replace('College of ', 'College of ')
            name = name.replace('California State University', 'Cal State')
            if len(name) > 25:
                name = name[:22] + "..."
        
        text = ax.annotate(name, 
                          (row['price_usd'], row['overall_quality_score']),
                          xytext=(5, 5), textcoords='offset points',
                          fontsize=8, fontweight='bold', color='#2b2b2b',
                          bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                   edgecolor='#0072B2', alpha=0.9, linewidth=0.5),
                          zorder=4)
        texts.append(text)
    
    # Use adjust_text to prevent label overlap
    adjust_text(texts, ax=ax, 
                expand_points=(1.2, 1.2), expand_text=(1.1, 1.1),
                arrowprops=dict(arrowstyle='->', color='#0072B2', alpha=0.7, lw=0.8))
    
    # Professional styling
    ax.set_xlabel('Annual Tuition (USD)', fontsize=11, fontweight='normal', color='#2b2b2b')
    ax.set_ylabel('Quality Score (College Scorecard Metrics)', fontsize=11, fontweight='normal', color='#2b2b2b')
    
    # Format axes
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax.tick_params(axis='both', which='major', labelsize=9, color='#2b2b2b')
    
    # Grid - thin, light grey
    ax.grid(True, linestyle='-', alpha=0.2, color='#e6e6e6', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Title and subtitle
    fig.suptitle('Ten Universities Combine High Quality with Reasonable Tuition', 
                fontsize=14, fontweight='bold', color='#2b2b2b', y=0.96)
    ax.text(0.5, 1.02, f'1,206 U.S. universities analyzed (r = {pearson_r:.3f})', 
            ha='center', va='bottom', transform=ax.transAxes,
            fontsize=11, color='#666666')
    
    # Caption
    caption_text = ('Quality = Composite score from SAT, graduation rates, earnings, retention. '
                   'Price = Annual tuition. Data: U.S. Dept. of Education College Scorecard 2023.')
    ax.text(0.02, 0.02, caption_text, 
            transform=ax.transAxes, fontsize=8, color='#666666',
            ha='left', va='bottom', wrap=True)
    
    # Source credit
    ax.text(0.98, 0.02, 'Analysis: University Price-Quality Study', 
            transform=ax.transAxes, fontsize=8, color='#999999',
            ha='right', va='bottom')
    
    # Set margins and layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, bottom=0.15, left=0.12, right=0.96)
    
    # Save with high quality
    filename = "professional_sweet_spot_analysis.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"✅ Professional visualization saved: {filename}")
    
    plt.show()
    
    # Print the clean results table
    print("\n" + "="*70)
    print("SWEET SPOT UNIVERSITIES (High Quality + Reasonable Tuition)")
    print("="*70)
    print("University                        | State | Price    | Quality")
    print("-"*70)
    
    for _, row in sweet_spot_unis.iterrows():
        name = row['institution'][:32].ljust(32)
        state = row['state']
        price = row['price_usd']
        quality_score = row['overall_quality_score']
        
        print(f"{name} | {state:2s}    | ${price:7,.0f} | {quality_score:6.1f}")
    
    print(f"\nCriteria: Quality score ≥ {quality_score_threshold:.0f}, Price ≤ ${median_price:,.0f}")
    print(f"These {len(sweet_spot_unis)} universities offer the best combination of academic quality and affordability.")

if __name__ == "__main__":
    create_professional_sweet_spot_plot()