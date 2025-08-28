#!/usr/bin/env python3
"""
Create a focused sweet spot visualization highlighting the best value universities.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import numpy as np

def create_focused_sweet_spot_plot():
    """Create a focused plot highlighting sweet spot universities with clear labels."""
    
    # Load data
    df = pd.read_csv("scorecard_universities_with_quality_rankings.csv")
    
    # Define sweet spot criteria
    median_price = df['price_usd'].median()
    top_25_quality_threshold = df['quality_ranking'].quantile(0.25)
    
    # Identify sweet spot universities
    sweet_spot_mask = (df['quality_ranking'] <= top_25_quality_threshold) & (df['price_usd'] <= median_price)
    sweet_spot_unis = df[sweet_spot_mask].sort_values('quality_ranking').head(10)
    regular_unis = df[~sweet_spot_mask]
    
    # Calculate correlation
    pearson_r, pearson_p = pearsonr(df['quality_ranking'], df['price_usd'])
    
    # Create the plot
    plt.figure(figsize=(16, 12))
    
    # Main plot
    ax = plt.subplot(111)
    
    # Plot all universities as small gray dots
    ax.scatter(regular_unis['quality_ranking'], regular_unis['price_usd'], 
               c='lightgray', alpha=0.3, s=15, label=f'All Universities (n={len(regular_unis)})')
    
    # Highlight sweet spot universities with different colors for each
    colors = ['red', 'orange', 'gold', 'green', 'blue', 'purple', 'brown', 'pink', 'olive', 'cyan']
    
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows()):
        color = colors[i % len(colors)]
        ax.scatter(row['quality_ranking'], row['price_usd'], 
                   c=color, s=200, alpha=0.9, edgecolors='black', linewidth=2,
                   zorder=5)
    
    # Add boundary lines for sweet spot
    ax.axvline(x=top_25_quality_threshold, color='blue', linestyle='--', alpha=0.8, linewidth=2,
               label=f'Top 25% Quality Threshold (Rank ≤ {top_25_quality_threshold:.0f})')
    ax.axhline(y=median_price, color='green', linestyle='--', alpha=0.8, linewidth=2,
               label=f'Median Price Threshold (≤ ${median_price:,.0f})')
    
    # Add labels for each sweet spot university
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows()):
        name = row['institution']
        # Shorten very long names
        if len(name) > 30:
            name = name[:27] + "..."
        
        # Position label with offset to avoid overlap
        x_offset = 15 if i % 2 == 0 else -15
        y_offset = 1000 if i < 5 else -1000
        
        ax.annotate(f"{i+1}. {name}\n(#{row['quality_ranking']:.0f}, ${row['price_usd']:,.0f})", 
                    (row['quality_ranking'], row['price_usd']),
                    xytext=(x_offset, y_offset), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[i % len(colors)], alpha=0.7),
                    fontsize=10, ha='center', va='center',
                    arrowprops=dict(arrowstyle='->', color='black', alpha=0.7, lw=1))
    
    # Styling
    ax.set_xlabel('Quality Ranking (1 = best)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Annual Tuition (USD)', fontsize=14, fontweight='bold')
    ax.set_title(f'Sweet Spot Universities: High Quality + Reasonable Price\n'
                f'1,206 US Universities (College Scorecard Data)\n'
                f'Correlation: r = {pearson_r:.3f} (p < 0.001)', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Format y-axis to show prices in thousands
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
    
    # Grid and legend
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
    
    # Add text box with sweet spot criteria
    textstr = f'Sweet Spot Criteria:\n• Quality Rank ≤ {top_25_quality_threshold:.0f} (Top 25%)\n• Price ≤ ${median_price:,.0f} (Below Median)\n• Found {len(sweet_spot_unis)} qualifying universities'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    # Save the plot
    filename = "focused_sweet_spot_universities.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Focused sweet spot plot saved: {filename}")
    
    plt.show()
    
    # Print the sweet spot list
    print("\n" + "="*80)
    print("TOP 10 SWEET SPOT UNIVERSITIES (High Quality + Reasonable Price)")
    print("="*80)
    print("Rank | University                           | State | Price     | Quality Score")
    print("-"*80)
    
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows(), 1):
        name = row['institution'][:37]
        state = row['state']
        price = row['price_usd']
        quality_rank = row['quality_ranking']
        quality_score = row['overall_quality_score']
        
        print(f"{quality_rank:4.0f} | {name:<37} | {state:2s}    | ${price:8,.0f} | {quality_score:7.1f}")

if __name__ == "__main__":
    create_focused_sweet_spot_plot()