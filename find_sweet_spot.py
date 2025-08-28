#!/usr/bin/env python3
"""
Find universities in the "sweet spot" - good rankings at reasonable prices.
Uses value analysis to identify best price-to-ranking ratios.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SweetSpotAnalyzer:
    def __init__(self):
        self.data = None
        
    def load_data(self) -> bool:
        """Load the combined university data."""
        try:
            self.data = pd.read_csv('combined_university_data.csv')
            logger.info(f"Loaded data for {len(self.data)} universities")
            return True
        except FileNotFoundError:
            logger.error("Combined data file not found. Run plot_analysis.py first.")
            return False
            
    def calculate_value_scores(self) -> pd.DataFrame:
        """Calculate value scores for each university."""
        df = self.data.copy()
        
        # Create value metrics
        # 1. Rank percentile (lower rank = better = higher percentile)
        df['rank_percentile'] = 100 - ((df['rank'] - df['rank'].min()) / 
                                      (df['rank'].max() - df['rank'].min()) * 100)
        
        # 2. Price percentile (lower price = better = higher percentile) 
        df['price_percentile'] = 100 - ((df['price_usd'] - df['price_usd'].min()) / 
                                       (df['price_usd'].max() - df['price_usd'].min()) * 100)
        
        # 3. Value score (combination of good ranking and reasonable price)
        # Weight ranking slightly higher (60%) than price (40%)
        df['value_score'] = (0.6 * df['rank_percentile']) + (0.4 * df['price_percentile'])
        
        # 4. Alternative metric: Price per ranking point
        # Lower is better (good rank at low price)
        df['price_per_rank_point'] = df['price_usd'] / (101 - df['rank'])  # Invert rank for calculation
        
        # 5. Calculate country-specific value scores
        for country in df['country'].unique():
            country_mask = df['country'] == country
            country_data = df[country_mask]
            
            # Within-country rank percentile
            df.loc[country_mask, f'{country.lower()}_rank_percentile'] = (
                100 - ((country_data['rank'] - country_data['rank'].min()) / 
                      (country_data['rank'].max() - country_data['rank'].min()) * 100)
            )
            
            # Within-country price percentile
            df.loc[country_mask, f'{country.lower()}_price_percentile'] = (
                100 - ((country_data['price_usd'] - country_data['price_usd'].min()) / 
                      (country_data['price_usd'].max() - country_data['price_usd'].min()) * 100)
            )
            
            # Within-country value score
            df.loc[country_mask, f'{country.lower()}_value_score'] = (
                0.6 * df.loc[country_mask, f'{country.lower()}_rank_percentile'] + 
                0.4 * df.loc[country_mask, f'{country.lower()}_price_percentile']
            )
        
        return df
        
    def find_sweet_spot_universities(self, df: pd.DataFrame, top_n: int = 15) -> Dict:
        """Find universities offering the best value."""
        logger.info(f"Finding top {top_n} value universities...")
        
        results = {}
        
        # Overall best value
        overall_best = df.nlargest(top_n, 'value_score')[
            ['name', 'country', 'rank', 'price_usd', 'value_score', 'type']
        ].copy()
        overall_best['price_formatted'] = overall_best['price_usd'].apply(lambda x: f"${x:,.0f}")
        results['overall'] = overall_best
        
        # Best value by country
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            country_col = f'{country.lower()}_value_score'
            
            country_best = country_data.nlargest(top_n, country_col)[
                ['name', 'rank', 'price_usd', country_col, 'type']
            ].copy()
            country_best['price_formatted'] = country_best['price_usd'].apply(lambda x: f"${x:,.0f}")
            results[country] = country_best
            
        # Specific value categories
        
        # 1. Elite bargains (top 25 rank, reasonable price)
        elite_threshold = df['rank'].quantile(0.25)  # Top 25% rankings
        price_threshold = df['price_usd'].quantile(0.6)  # Below 60th percentile price
        
        elite_bargains = df[
            (df['rank'] <= elite_threshold) & 
            (df['price_usd'] <= price_threshold)
        ].sort_values('rank')[
            ['name', 'country', 'rank', 'price_usd', 'value_score', 'type']
        ]
        elite_bargains['price_formatted'] = elite_bargains['price_usd'].apply(lambda x: f"${x:,.0f}")
        results['elite_bargains'] = elite_bargains
        
        # 2. Budget champions (very low price, decent ranking)
        budget_threshold = df['price_usd'].quantile(0.25)  # Bottom 25% prices
        rank_threshold = df['rank'].quantile(0.7)  # Better than 70th percentile rank
        
        budget_champions = df[
            (df['price_usd'] <= budget_threshold) & 
            (df['rank'] <= rank_threshold)
        ].sort_values('value_score', ascending=False)[
            ['name', 'country', 'rank', 'price_usd', 'value_score', 'type']
        ]
        budget_champions['price_formatted'] = budget_champions['price_usd'].apply(lambda x: f"${x:,.0f}")
        results['budget_champions'] = budget_champions
        
        # 3. International value (UK universities for US students)
        if 'UK' in df['country'].values:
            uk_for_intl = df[df['country'] == 'UK'].sort_values('value_score', ascending=False)[
                ['name', 'rank', 'price_usd', 'value_score']
            ].head(10)
            uk_for_intl['price_formatted'] = uk_for_intl['price_usd'].apply(lambda x: f"${x:,.0f}")
            results['uk_international_value'] = uk_for_intl
            
        return results
        
    def create_sweet_spot_visualization(self, df: pd.DataFrame) -> plt.Figure:
        """Create visualization highlighting sweet spot universities."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Value score scatter plot
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            color = '#1f77b4' if country == 'US' else '#ff7f0e'
            ax1.scatter(country_data['rank'], country_data['price_usd'], 
                       c=country_data['value_score'], cmap='RdYlGn', 
                       s=80, alpha=0.7, edgecolors=color, linewidth=1)
        
        # Highlight top value universities
        top_value = df.nlargest(10, 'value_score')
        ax1.scatter(top_value['rank'], top_value['price_usd'], 
                   s=120, facecolors='none', edgecolors='red', linewidth=2,
                   label='Top 10 Value')
        
        ax1.set_xlabel('University Ranking (lower is better)')
        ax1.set_ylabel('Annual Tuition (USD)')
        ax1.set_title('Value Score Analysis\n(Color = Value Score, Red Circles = Top Value)')
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Value score distribution
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            ax2.hist(country_data['value_score'], alpha=0.6, bins=15, 
                    label=f'{country} (n={len(country_data)})')
        ax2.set_xlabel('Value Score')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Distribution of Value Scores')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Price vs Rank with quadrants
        median_rank = df['rank'].median()
        median_price = df['price_usd'].median()
        
        ax3.axhline(median_price, color='gray', linestyle='--', alpha=0.7)
        ax3.axvline(median_rank, color='gray', linestyle='--', alpha=0.7)
        
        # Add quadrant labels
        ax3.text(5, df['price_usd'].max() * 0.95, 'High Cost\nElite', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7),
                ha='left', va='top', fontsize=10)
        ax3.text(df['rank'].max() * 0.95, df['price_usd'].max() * 0.95, 'High Cost\nLower Rank', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7),
                ha='right', va='top', fontsize=10)
        ax3.text(5, df['price_usd'].min() * 1.05, 'SWEET SPOT\nElite & Affordable', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8),
                ha='left', va='bottom', fontsize=10, weight='bold')
        ax3.text(df['rank'].max() * 0.95, df['price_usd'].min() * 1.05, 'Budget\nOptions', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.7),
                ha='right', va='bottom', fontsize=10)
        
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            color = '#1f77b4' if country == 'US' else '#ff7f0e'
            ax3.scatter(country_data['rank'], country_data['price_usd'], 
                       c=color, alpha=0.6, s=60, label=country)
        
        ax3.set_xlabel('University Ranking (lower is better)')
        ax3.set_ylabel('Annual Tuition (USD)')
        ax3.set_title('Value Quadrants Analysis')
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Top value universities bar chart
        top_10_value = df.nlargest(10, 'value_score')
        bars = ax4.barh(range(len(top_10_value)), top_10_value['value_score'])
        
        # Color bars by country
        for i, country in enumerate(top_10_value['country']):
            color = '#1f77b4' if country == 'US' else '#ff7f0e'
            bars[i].set_color(color)
        
        ax4.set_yticks(range(len(top_10_value)))
        ax4.set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                            for name in top_10_value['name']])
        ax4.set_xlabel('Value Score')
        ax4.set_title('Top 10 Value Universities')
        ax4.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        return fig
        
    def print_sweet_spot_analysis(self, results: Dict):
        """Print comprehensive sweet spot analysis."""
        print("=" * 80)
        print("UNIVERSITY SWEET SPOT ANALYSIS")
        print("=" * 80)
        
        print("\n🏆 OVERALL TOP VALUE UNIVERSITIES (Global Ranking)")
        print("-" * 60)
        top_overall = results['overall'].head(10)
        for idx, row in top_overall.iterrows():
            print(f"{row['name']:<40} | {row['country']} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {row['value_score']:>5.1f}")
            
        if 'elite_bargains' in results and len(results['elite_bargains']) > 0:
            print(f"\n💎 ELITE BARGAINS (Top 25% Rankings, Reasonable Prices)")
            print("-" * 60)
            for idx, row in results['elite_bargains'].head(8).iterrows():
                print(f"{row['name']:<40} | {row['country']} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {row['value_score']:>5.1f}")
        
        if 'budget_champions' in results and len(results['budget_champions']) > 0:
            print(f"\n💰 BUDGET CHAMPIONS (Low Cost, Good Rankings)")
            print("-" * 60)
            for idx, row in results['budget_champions'].head(8).iterrows():
                print(f"{row['name']:<40} | {row['country']} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {row['value_score']:>5.1f}")
                
        # Country-specific recommendations
        print(f"\n🇺🇸 BEST VALUE US UNIVERSITIES")
        print("-" * 60)
        if 'US' in results:
            us_col = 'us_value_score'
            for idx, row in results['US'].head(8).iterrows():
                print(f"{row['name']:<40} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {row[us_col]:>5.1f}")
        
        print(f"\n🇬🇧 BEST VALUE UK UNIVERSITIES (International Students)")
        print("-" * 60)
        if 'UK' in results:
            uk_col = 'uk_value_score'
            for idx, row in results['UK'].head(8).iterrows():
                print(f"{row['name']:<40} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {row[uk_col]:>5.1f}")
        
        print(f"\n📊 VALUE INSIGHTS:")
        print(f"• Elite Bargains: {len(results.get('elite_bargains', []))} universities combine top rankings with reasonable prices")
        print(f"• Budget Champions: {len(results.get('budget_champions', []))} universities offer quality education at low cost")
        print(f"• UK universities often provide better value for international students than equivalent US institutions")
        print(f"• Scottish universities offer exceptional value due to lower tuition fees")

def main():
    """Main execution function."""
    analyzer = SweetSpotAnalyzer()
    
    if not analyzer.load_data():
        return
        
    # Calculate value scores
    df_with_scores = analyzer.calculate_value_scores()
    
    # Find sweet spot universities
    sweet_spot_results = analyzer.find_sweet_spot_universities(df_with_scores)
    
    # Print analysis
    analyzer.print_sweet_spot_analysis(sweet_spot_results)
    
    # Create visualization
    fig = analyzer.create_sweet_spot_visualization(df_with_scores)
    fig.savefig('university_sweet_spot_analysis.png', dpi=300, bbox_inches='tight')
    logger.info("Saved: university_sweet_spot_analysis.png")
    
    # Save detailed results
    df_with_scores.to_csv('university_value_analysis.csv', index=False)
    logger.info("Saved: university_value_analysis.csv")
    
    plt.show()
    
    return sweet_spot_results, df_with_scores

if __name__ == "__main__":
    main()