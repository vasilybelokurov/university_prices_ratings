#!/usr/bin/env python3
"""
Create clean visualization with numbered sweet spot universities and a legend box.
Much cleaner approach than trying to label everything on the plot.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr

def create_numbered_legend_plot():
    """Create plot with numbered universities and clean legend box."""
    
    print("Creating visualization with numbered legend...")
    
    # Load data
    df = pd.read_csv("scorecard_universities_with_quality_rankings.csv")
    
    # Define sweet spot criteria
    median_price = df['price_usd'].median()
    top_25_quality_threshold = df['quality_ranking'].quantile(0.25)
    
    # Create sweet spot mask
    sweet_spot_mask = (df['quality_ranking'] <= top_25_quality_threshold) & (df['price_usd'] <= median_price)
    sweet_spot_unis = df[sweet_spot_mask].sort_values('quality_ranking').head(10)
    regular_unis = df[~sweet_spot_mask]
    
    # Calculate correlation
    pearson_r, pearson_p = pearsonr(df['price_usd'], df['overall_quality_score'])
    
    print(f"Sweet spot criteria: Quality rank ≤ {top_25_quality_threshold:.0f}, Price ≤ ${median_price:,.0f}")
    print(f"Found {len(sweet_spot_unis)} sweet spot universities")
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    # Plot all universities as gray background
    ax.scatter(regular_unis['price_usd'], regular_unis['overall_quality_score'], 
               c='lightgray', s=20, alpha=0.5, zorder=1)
    
    # Plot sweet spot universities as numbered points
    colors = ['red', 'orange', 'gold', 'green', 'blue', 'purple', 'brown', 'pink', 'olive', 'cyan']
    
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows()):
        # Plot the point
        ax.scatter(row['price_usd'], row['overall_quality_score'], 
                   c=colors[i], s=150, alpha=0.9, zorder=3, 
                   edgecolors='black', linewidth=2)
        
        # Add number label on the point
        ax.text(row['price_usd'], row['overall_quality_score'], str(i+1), 
                ha='center', va='center', fontsize=12, fontweight='bold', 
                color='white', zorder=4)
    
    # Add threshold lines
    ax.axvline(x=median_price, color='blue', linestyle='--', alpha=0.7, linewidth=2,
               label=f'Median Price (${median_price:,.0f})')
    
    # Convert quality ranking threshold to quality score for the line
    quality_score_threshold = df[df['quality_ranking'] <= top_25_quality_threshold]['overall_quality_score'].min()
    ax.axhline(y=quality_score_threshold, color='green', linestyle='--', alpha=0.7, linewidth=2,
               label=f'Top 25% Quality (Score ≥ {quality_score_threshold:.0f})')
    
    # Styling
    ax.set_xlabel('Annual Tuition (USD)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Quality Score', fontsize=14, fontweight='bold')
    ax.set_title('Sweet Spot Universities: High Quality + Reasonable Price\n'
                f'1,206 US Universities (Correlation: r = {pearson_r:.3f})', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Format axes
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=12)
    
    # Create legend box with university names
    legend_text = "SWEET SPOT UNIVERSITIES:\n" + "-" * 35 + "\n"
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows(), 1):
        name = row['institution']
        if len(name) > 25:
            name = name[:22] + "..."
        price = row['price_usd']
        rank = row['quality_ranking']
        legend_text += f"{i:2d}. {name:<25} (#{rank:.0f}, ${price:,.0f})\n"
    
    legend_text += f"\nCriteria: Quality rank ≤ {top_25_quality_threshold:.0f}, Price ≤ ${median_price:,.0f}"
    
    # Position legend box
    ax.text(0.98, 0.98, legend_text, 
            transform=ax.transAxes, fontsize=10, ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                     edgecolor='black', alpha=0.9, linewidth=1),
            family='monospace')
    
    plt.tight_layout()
    
    # Save the plot
    filename = "numbered_sweet_spot_universities.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Numbered legend plot saved: {filename}")
    
    plt.show()
    
    # Print clean table
    print("\n" + "="*75)
    print("SWEET SPOT UNIVERSITIES (Numbered on Plot)")
    print("="*75)
    print("No. | University                        | State | Rank | Price    | Score")
    print("-"*75)
    
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows(), 1):
        name = row['institution'][:32]
        state = row['state']
        rank = row['quality_ranking']
        price = row['price_usd']
        score = row['overall_quality_score']
        
        print(f"{i:3d} | {name:<32} | {state:2s}   | #{rank:3.0f} | ${price:7,.0f} | {score:5.1f}")

if __name__ == "__main__":
    create_numbered_legend_plot()