#!/usr/bin/env python3
"""
Final comprehensive analysis of US universities using College Scorecard quality rankings.
1206 universities with real tuition data and quality-based rankings.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_and_analyze_data():
    """Load the ranked university data and perform comprehensive analysis."""
    
    logger.info("Loading College Scorecard university rankings data...")
    
    try:
        df = pd.read_csv("scorecard_universities_with_quality_rankings.csv")
        logger.info(f"✅ Loaded data for {len(df)} universities")
        
        # Data quality check
        logger.info(f"Universities with price data: {df['price_usd'].notna().sum()}")
        logger.info(f"Universities with quality rankings: {df['quality_ranking'].notna().sum()}")
        
        return df
    
    except FileNotFoundError:
        logger.error("❌ Scorecard ranking data not found. Run implement_scorecard_ranking_system.py first.")
        return None

def comprehensive_analysis(df):
    """Run comprehensive price vs ranking analysis."""
    
    logger.info("\nCOMPREHENSIVE PRICE VS QUALITY ANALYSIS:")
    logger.info("=" * 60)
    
    # Filter for universities with both price and ranking data
    analysis_df = df[(df['price_usd'].notna()) & (df['quality_ranking'].notna())].copy()
    logger.info(f"Universities in analysis: {len(analysis_df)}")
    
    # Price statistics
    price_stats = analysis_df['price_usd'].describe()
    logger.info(f"\nPRICE STATISTICS (USD per year):")
    logger.info(f"  Min: ${price_stats['min']:,.0f}")
    logger.info(f"  25th percentile: ${price_stats['25%']:,.0f}")
    logger.info(f"  Median: ${price_stats['50%']:,.0f}")
    logger.info(f"  75th percentile: ${price_stats['75%']:,.0f}")
    logger.info(f"  Max: ${price_stats['max']:,.0f}")
    logger.info(f"  Mean: ${price_stats['mean']:,.0f}")
    
    # Quality ranking statistics
    rank_stats = analysis_df['quality_ranking'].describe()
    logger.info(f"\nQUALITY RANKING STATISTICS:")
    logger.info(f"  Best ranking: {rank_stats['min']:.0f}")
    logger.info(f"  25th percentile: {rank_stats['25%']:.0f}")
    logger.info(f"  Median ranking: {rank_stats['50%']:.0f}")
    logger.info(f"  75th percentile: {rank_stats['75%']:.0f}")
    logger.info(f"  Worst ranking: {rank_stats['max']:.0f}")
    
    # Correlation analysis
    pearson_r, pearson_p = pearsonr(analysis_df['quality_ranking'], analysis_df['price_usd'])
    spearman_r, spearman_p = spearmanr(analysis_df['quality_ranking'], analysis_df['price_usd'])
    
    logger.info(f"\nCORRELATION ANALYSIS:")
    logger.info(f"  Pearson correlation: r = {pearson_r:.3f} (p = {pearson_p:.3f})")
    logger.info(f"  Spearman correlation: ρ = {spearman_r:.3f} (p = {spearman_p:.3f})")
    
    if pearson_p < 0.001:
        logger.info("  ✅ HIGHLY SIGNIFICANT correlation (p < 0.001)")
    elif pearson_p < 0.01:
        logger.info("  ✅ SIGNIFICANT correlation (p < 0.01)")
    elif pearson_p < 0.05:
        logger.info("  ✅ Significant correlation (p < 0.05)")
    else:
        logger.info("  ❌ No significant correlation")
    
    # Interpretation
    if pearson_r > 0:
        logger.info("  📈 POSITIVE correlation: Higher rankings (worse) → Higher prices")
        logger.info("     This suggests LOWER quality universities charge MORE!")
    else:
        logger.info("  📉 NEGATIVE correlation: Higher rankings (worse) → Lower prices")
        logger.info("     This suggests HIGHER quality universities charge MORE!")
    
    return analysis_df, pearson_r, spearman_r

def find_sweet_spot_universities(df):
    """Find universities in the sweet spot of price vs quality."""
    
    logger.info("\nFINDING SWEET SPOT UNIVERSITIES:")
    logger.info("=" * 50)
    logger.info("(High quality + reasonable price)")
    
    # Define sweet spot criteria
    # Top 25% quality (ranking <= 300) + Bottom 50% price
    median_price = df['price_usd'].median()
    top_25_quality_threshold = df['quality_ranking'].quantile(0.25)
    
    logger.info(f"Sweet spot criteria:")
    logger.info(f"  Quality ranking ≤ {top_25_quality_threshold:.0f} (top 25%)")
    logger.info(f"  Price ≤ ${median_price:,.0f} (bottom 50%)")
    
    # Find sweet spot universities
    sweet_spot = df[
        (df['quality_ranking'] <= top_25_quality_threshold) & 
        (df['price_usd'] <= median_price)
    ].sort_values('quality_ranking').head(20)
    
    logger.info(f"\nTOP 20 SWEET SPOT UNIVERSITIES:")
    logger.info("-" * 80)
    logger.info("Rank | University                           | State | Price    | Score")
    logger.info("-" * 80)
    
    for _, row in sweet_spot.iterrows():
        name = row['institution'][:37]
        state = row['state']
        price = row['price_usd']
        rank = row['quality_ranking']
        score = row['overall_quality_score']
        
        logger.info(f"{rank:4.0f} | {name:<37} | {state:2s}    | ${price:8,.0f} | {score:5.1f}")
    
    return sweet_spot

def create_comprehensive_visualizations(df, pearson_r, spearman_r):
    """Create comprehensive visualizations for the analysis with sweet spot highlighting."""
    
    logger.info("\nCreating comprehensive visualizations with sweet spot highlighting...")
    
    # Identify sweet spot universities
    median_price = df['price_usd'].median()
    top_25_quality_threshold = df['quality_ranking'].quantile(0.25)
    
    sweet_spot_mask = (df['quality_ranking'] <= top_25_quality_threshold) & (df['price_usd'] <= median_price)
    sweet_spot_unis = df[sweet_spot_mask].sort_values('quality_ranking').head(10)
    
    logger.info(f"Sweet spot criteria: Quality rank ≤ {top_25_quality_threshold:.0f}, Price ≤ ${median_price:,.0f}")
    logger.info(f"Found {len(sweet_spot_unis)} sweet spot universities for highlighting")
    
    # Set style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(24, 16))
    
    # Main scatter plot with sweet spot highlighting
    ax1 = plt.subplot(2, 3, (1, 2))
    
    # Plot all universities in light gray
    regular_mask = ~sweet_spot_mask
    ax1.scatter(df[regular_mask]['quality_ranking'], df[regular_mask]['price_usd'], 
               c='lightgray', alpha=0.4, s=20, label='All Universities')
    
    # Highlight sweet spot universities in bright colors
    scatter_sweet = ax1.scatter(sweet_spot_unis['quality_ranking'], sweet_spot_unis['price_usd'], 
                               c='red', s=100, alpha=0.9, edgecolors='darkred', linewidth=2,
                               label=f'Sweet Spot Universities (n={len(sweet_spot_unis)})')
    
    # Add sweet spot boundary lines
    ax1.axvline(x=top_25_quality_threshold, color='blue', linestyle='--', alpha=0.7, 
                label=f'Top 25% Quality (Rank ≤ {top_25_quality_threshold:.0f})')
    ax1.axhline(y=median_price, color='green', linestyle='--', alpha=0.7, 
                label=f'Median Price (≤ ${median_price:,.0f})')
    
    # Label the top sweet spot universities
    for _, row in sweet_spot_unis.head(5).iterrows():
        # Create shorter labels
        name = row['institution']
        if len(name) > 25:
            name = name[:22] + "..."
        
        ax1.annotate(f"{name}\n(#{row['quality_ranking']:.0f}, ${row['price_usd']:,.0f})", 
                    (row['quality_ranking'], row['price_usd']),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                    fontsize=8, ha='left')
    
    ax1.set_xlabel('Quality Ranking (1 = best)', fontsize=12)
    ax1.set_ylabel('Annual Tuition (USD)', fontsize=12)
    ax1.set_title(f'US Universities: Price vs Quality Ranking with Sweet Spot Highlighted\\n1,206 Universities with College Scorecard Data\\nPearson r = {pearson_r:.3f}, Spearman ρ = {spearman_r:.3f}', fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)
    
    # Price distribution with sweet spot threshold
    ax2 = plt.subplot(2, 3, 3)
    ax2.hist(df['price_usd'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    ax2.axvline(x=median_price, color='green', linestyle='--', linewidth=2, label=f'Sweet Spot Threshold: ${median_price:,.0f}')
    ax2.set_xlabel('Annual Tuition (USD)', fontsize=10)
    ax2.set_ylabel('Number of Universities', fontsize=10)
    ax2.set_title('Price Distribution', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Quality ranking distribution with sweet spot threshold
    ax3 = plt.subplot(2, 3, 4)
    ax3.hist(df['quality_ranking'], bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
    ax3.axvline(x=top_25_quality_threshold, color='blue', linestyle='--', linewidth=2, 
                label=f'Sweet Spot Threshold: Rank {top_25_quality_threshold:.0f}')
    ax3.set_xlabel('Quality Ranking', fontsize=10)
    ax3.set_ylabel('Number of Universities', fontsize=10)
    ax3.set_title('Quality Ranking Distribution', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Sweet spot universities table
    ax4 = plt.subplot(2, 3, 5)
    ax4.axis('off')
    ax4.set_title('Top 10 Sweet Spot Universities', fontsize=12, pad=20)
    
    # Create table data
    table_data = []
    for i, (_, row) in enumerate(sweet_spot_unis.head(10).iterrows(), 1):
        name = row['institution'][:30] + "..." if len(row['institution']) > 30 else row['institution']
        table_data.append([
            f"{i}.", 
            name,
            row['state'],
            f"#{row['quality_ranking']:.0f}",
            f"${row['price_usd']:,.0f}"
        ])
    
    table = ax4.table(cellText=table_data,
                     colLabels=['#', 'University', 'State', 'Rank', 'Price'],
                     cellLoc='left',
                     loc='center',
                     colWidths=[0.08, 0.5, 0.1, 0.12, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)
    
    # Style the table
    for i in range(len(table_data) + 1):
        for j in range(5):
            cell = table[(i, j)]
            if i == 0:  # Header
                cell.set_facecolor('#40466e')
                cell.set_text_props(weight='bold', color='white')
            else:  # Data rows
                if i % 2 == 0:
                    cell.set_facecolor('#f1f1f2')
                else:
                    cell.set_facecolor('white')
    
    # Value analysis scatter plot with sweet spot highlighted
    ax5 = plt.subplot(2, 3, 6)
    ax5.scatter(df[regular_mask]['overall_quality_score'], df[regular_mask]['price_usd'], 
               alpha=0.4, s=20, color='lightgray', label='All Universities')
    ax5.scatter(sweet_spot_unis['overall_quality_score'], sweet_spot_unis['price_usd'], 
               alpha=0.9, s=80, color='red', edgecolors='darkred', linewidth=1,
               label='Sweet Spot Universities')
    ax5.set_xlabel('Quality Score', fontsize=10)
    ax5.set_ylabel('Annual Tuition (USD)', fontsize=10)
    ax5.set_title('Price vs Quality Score (Sweet Spot Highlighted)', fontsize=12)
    ax5.grid(True, alpha=0.3)
    ax5.legend()
    
    plt.tight_layout()
    
    # Save the plot
    filename = "comprehensive_scorecard_analysis_with_sweet_spot.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    logger.info(f"✅ Enhanced visualization with sweet spot highlighting saved: {filename}")
    
    plt.show()
    
    return sweet_spot_unis

def value_analysis(df):
    """Perform value analysis to find best value universities."""
    
    logger.info("\nVALUE ANALYSIS:")
    logger.info("=" * 40)
    logger.info("Finding universities with best value (quality per dollar)")
    
    # Create value score: normalize quality score (0-100) and price
    df = df.copy()
    
    # Normalize price to 0-100 scale (lower price = higher score)
    price_min, price_max = df['price_usd'].min(), df['price_usd'].max()
    df['price_score'] = 100 * (price_max - df['price_usd']) / (price_max - price_min)
    
    # Calculate value score (70% quality, 30% price affordability)
    df['value_score'] = 0.7 * df['overall_quality_score'] + 0.3 * df['price_score']
    
    # Top 20 best value universities
    best_value = df.nlargest(20, 'value_score')
    
    logger.info("\nTOP 20 BEST VALUE UNIVERSITIES:")
    logger.info("-" * 90)
    logger.info("University                               | State | Price     | Quality | Value")
    logger.info("-" * 90)
    
    for _, row in best_value.iterrows():
        name = row['institution'][:40]
        state = row['state']
        price = row['price_usd']
        qual_score = row['overall_quality_score']
        value_score = row['value_score']
        
        logger.info(f"{name:<40} | {state:2s}    | ${price:8,.0f} | {qual_score:7.1f} | {value_score:5.1f}")
    
    return best_value

def main():
    print("=" * 80)
    print("FINAL COMPREHENSIVE ANALYSIS: COLLEGE SCORECARD RANKINGS")
    print("=" * 80)
    
    # Load data
    df = load_and_analyze_data()
    
    if df is None:
        print("❌ ERROR: Cannot load data")
        return None
    
    # Comprehensive analysis
    analysis_df, pearson_r, spearman_r = comprehensive_analysis(df)
    
    # Find sweet spot universities
    sweet_spot = find_sweet_spot_universities(analysis_df)
    
    # Value analysis
    best_value = value_analysis(analysis_df)
    
    # Create visualizations with sweet spot highlighting
    sweet_spot_from_viz = create_comprehensive_visualizations(analysis_df, pearson_r, spearman_r)
    
    # Save final results
    sweet_spot.to_csv("sweet_spot_universities_scorecard.csv", index=False)
    best_value.to_csv("best_value_universities_scorecard.csv", index=False)
    analysis_df.to_csv("complete_analysis_scorecard.csv", index=False)
    
    print("\n" + "=" * 80)
    print("SUCCESS: COMPREHENSIVE ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Total universities analyzed: {len(analysis_df)}")
    print(f"Correlation (Pearson): r = {pearson_r:.3f}")
    print(f"Correlation (Spearman): ρ = {spearman_r:.3f}")
    print(f"Sweet spot universities: {len(sweet_spot)}")
    print(f"Best value universities: {len(best_value)}")
    print("\nFiles saved:")
    print("  - comprehensive_scorecard_analysis.png")
    print("  - sweet_spot_universities_scorecard.csv")
    print("  - best_value_universities_scorecard.csv")
    print("  - complete_analysis_scorecard.csv")
    print("\n🎉 REAL DATA ANALYSIS COMPLETE WITH 1,206 UNIVERSITIES!")
    
    return analysis_df

if __name__ == "__main__":
    results = main()