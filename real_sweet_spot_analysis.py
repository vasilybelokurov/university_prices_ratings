#!/usr/bin/env python3
"""
Sweet Spot Analysis with Real University Data
Identifies best value universities using actual ARWU rankings and College Scorecard data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class RealSweetSpotAnalyzer:
    def __init__(self):
        self.data = None
        
    def load_data(self) -> bool:
        """Load real university data."""
        try:
            self.data = pd.read_csv('real_university_data.csv')
            # Keep only universities with both price and ranking data
            self.data = self.data.dropna(subset=['price_usd', 'rank']).copy()
            logger.info(f"Loaded {len(self.data)} universities with complete data")
            return True
        except FileNotFoundError:
            logger.error("Real data file not found")
            return False
            
    def calculate_value_scores(self) -> pd.DataFrame:
        """Calculate value scores for real data."""
        df = self.data.copy()
        
        # Create percentiles (lower rank = better = higher percentile)
        df['rank_percentile'] = 100 - ((df['rank'] - df['rank'].min()) / 
                                      (df['rank'].max() - df['rank'].min()) * 100)
        
        # Lower price = better = higher percentile
        df['price_percentile'] = 100 - ((df['price_usd'] - df['price_usd'].min()) / 
                                       (df['price_usd'].max() - df['price_usd'].min()) * 100)
        
        # Value score (60% ranking, 40% price)
        df['value_score'] = (0.6 * df['rank_percentile']) + (0.4 * df['price_percentile'])
        
        # Country-specific value scores
        for country in df['country'].unique():
            country_mask = df['country'] == country
            country_data = df[country_mask]
            
            if len(country_data) > 1:
                df.loc[country_mask, f'{country.lower()}_rank_percentile'] = (
                    100 - ((country_data['rank'] - country_data['rank'].min()) / 
                          (country_data['rank'].max() - country_data['rank'].min()) * 100)
                )
                
                df.loc[country_mask, f'{country.lower()}_price_percentile'] = (
                    100 - ((country_data['price_usd'] - country_data['price_usd'].min()) / 
                          (country_data['price_usd'].max() - country_data['price_usd'].min()) * 100)
                )
                
                df.loc[country_mask, f'{country.lower()}_value_score'] = (
                    0.6 * df.loc[country_mask, f'{country.lower()}_rank_percentile'] + 
                    0.4 * df.loc[country_mask, f'{country.lower()}_price_percentile']
                )
        
        return df
        
    def find_sweet_spots(self, df: pd.DataFrame) -> Dict:
        """Find sweet spot universities in real data."""
        results = {}
        
        # Overall best value
        top_10 = df.nlargest(10, 'value_score')[
            ['institution', 'country', 'rank', 'price_usd', 'value_score']
        ].copy()
        top_10['price_formatted'] = top_10['price_usd'].apply(lambda x: f"${x:,.0f}")
        results['overall_top'] = top_10
        
        # Elite bargains (top 25% ranks, below median price)
        rank_threshold = df['rank'].quantile(0.25)
        price_threshold = df['price_usd'].median()
        
        elite_bargains = df[
            (df['rank'] <= rank_threshold) & 
            (df['price_usd'] <= price_threshold)
        ].sort_values('rank')
        
        if not elite_bargains.empty:
            elite_bargains = elite_bargains[
                ['institution', 'country', 'rank', 'price_usd', 'value_score']
            ].copy()
            elite_bargains['price_formatted'] = elite_bargains['price_usd'].apply(lambda x: f"${x:,.0f}")
            results['elite_bargains'] = elite_bargains
        
        # Budget champions (bottom 25% prices)
        budget_threshold = df['price_usd'].quantile(0.25)
        budget_champions = df[df['price_usd'] <= budget_threshold].sort_values('value_score', ascending=False)
        
        if not budget_champions.empty:
            budget_champions = budget_champions[
                ['institution', 'country', 'rank', 'price_usd', 'value_score']
            ].copy()
            budget_champions['price_formatted'] = budget_champions['price_usd'].apply(lambda x: f"${x:,.0f}")
            results['budget_champions'] = budget_champions
        
        # Country-specific top performers
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            country_col = f'{country.lower()}_value_score'
            
            if country_col in country_data.columns:
                country_top = country_data.nlargest(8, country_col)[
                    ['institution', 'rank', 'price_usd', country_col]
                ].copy()
                country_top['price_formatted'] = country_top['price_usd'].apply(lambda x: f"${x:,.0f}")
                results[f'{country.lower()}_top'] = country_top
        
        return results
        
    def create_sweet_spot_visualization(self, df: pd.DataFrame) -> plt.Figure:
        """Create sweet spot visualization for real data."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Value score scatter
        colors = {'United States': '#1f77b4', 'United Kingdom': '#ff7f0e'}
        
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            scatter = ax1.scatter(country_data['rank'], country_data['price_usd'],
                                c=country_data['value_score'], cmap='RdYlGn',
                                s=100, alpha=0.7, edgecolors=colors[country],
                                linewidth=2, label=country)
        
        # Highlight top 5 value universities
        top_5 = df.nlargest(5, 'value_score')
        ax1.scatter(top_5['rank'], top_5['price_usd'],
                   s=200, facecolors='none', edgecolors='red',
                   linewidth=3, label='Top 5 Value')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax1)
        cbar.set_label('Value Score', rotation=270, labelpad=20)
        
        ax1.set_xlabel('ARWU Ranking (lower = better)')
        ax1.set_ylabel('Annual Tuition (USD)')
        ax1.set_title('Value Score Analysis - Real Data\n(Color = Value Score)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # 2. Value quadrants
        median_rank = df['rank'].median()
        median_price = df['price_usd'].median()
        
        ax2.axhline(median_price, color='gray', linestyle='--', alpha=0.7)
        ax2.axvline(median_rank, color='gray', linestyle='--', alpha=0.7)
        
        # Quadrant labels
        ax2.text(df['rank'].min(), df['price_usd'].max()*0.95,
                'SWEET SPOT\nGood Rank\nLow Price', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8),
                ha='left', va='top', fontweight='bold')
        
        ax2.text(df['rank'].max()*0.95, df['price_usd'].max()*0.95,
                'High Price\nPoor Rank', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7),
                ha='right', va='top')
        
        ax2.text(df['rank'].min(), df['price_usd'].min()*1.1,
                'Elite\nExpensive', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.7),
                ha='left', va='bottom')
        
        ax2.text(df['rank'].max()*0.95, df['price_usd'].min()*1.1,
                'Budget\nOptions', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7),
                ha='right', va='bottom')
        
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            ax2.scatter(country_data['rank'], country_data['price_usd'],
                       c=colors[country], alpha=0.7, s=80, label=country)
        
        ax2.set_xlabel('ARWU Ranking (lower = better)')
        ax2.set_ylabel('Annual Tuition (USD)')
        ax2.set_title('Value Quadrants - Real Data')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # 3. Top value universities bar chart
        top_8 = df.nlargest(8, 'value_score')
        bars = ax3.barh(range(len(top_8)), top_8['value_score'])
        
        # Color bars by country
        for i, (_, row) in enumerate(top_8.iterrows()):
            bars[i].set_color(colors[row['country']])
        
        ax3.set_yticks(range(len(top_8)))
        ax3.set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                            for name in top_8['institution']])
        ax3.set_xlabel('Value Score')
        ax3.set_title('Top 8 Value Universities - Real Data')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # 4. Price efficiency plot
        # Calculate price per ranking point (lower is better)
        df_temp = df.copy()
        df_temp['price_per_rank'] = df_temp['price_usd'] / (201 - df_temp['rank'])  # Invert rank
        
        most_efficient = df_temp.nsmallest(8, 'price_per_rank')
        bars2 = ax4.barh(range(len(most_efficient)), most_efficient['price_per_rank'])
        
        for i, (_, row) in enumerate(most_efficient.iterrows()):
            bars2[i].set_color(colors[row['country']])
        
        ax4.set_yticks(range(len(most_efficient)))
        ax4.set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                            for name in most_efficient['institution']])
        ax4.set_xlabel('Price per Ranking Point (USD)')
        ax4.set_title('Most Price-Efficient Universities')
        ax4.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        return fig
        
    def print_sweet_spot_analysis(self, results: Dict):
        """Print comprehensive sweet spot analysis with real data."""
        print("=" * 80)
        print("SWEET SPOT ANALYSIS - REAL DATA")
        print("=" * 80)
        
        print("Data Sources:")
        print("• Rankings: ARWU 2023 (Academic Ranking of World Universities)")
        print("• US Tuition: College Scorecard API (US Department of Education)")
        print("• UK Fees: Official rates + international student fees")
        
        print(f"\n🏆 TOP VALUE UNIVERSITIES (Real Data)")
        print("-" * 60)
        if 'overall_top' in results:
            for idx, row in results['overall_top'].head(10).iterrows():
                uni_name = row['institution'][:35] + '...' if len(row['institution']) > 35 else row['institution']
                print(f"{uni_name:<38} | {row['country'][:2]} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {row['value_score']:>5.1f}")
        
        if 'elite_bargains' in results and len(results['elite_bargains']) > 0:
            print(f"\n💎 ELITE BARGAINS (Top Quarter Rankings + Below Median Price)")
            print("-" * 60)
            for idx, row in results['elite_bargains'].iterrows():
                uni_name = row['institution'][:35] + '...' if len(row['institution']) > 35 else row['institution']
                print(f"{uni_name:<38} | {row['country'][:2]} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {row['value_score']:>5.1f}")
        
        if 'budget_champions' in results and len(results['budget_champions']) > 0:
            print(f"\n💰 BUDGET CHAMPIONS (Lowest 25% Prices)")
            print("-" * 60)
            for idx, row in results['budget_champions'].iterrows():
                uni_name = row['institution'][:35] + '...' if len(row['institution']) > 35 else row['institution']
                print(f"{uni_name:<38} | {row['country'][:2]} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {row['value_score']:>5.1f}")
        
        # Country-specific results
        if 'united states_top' in results:
            print(f"\n🇺🇸 BEST VALUE US UNIVERSITIES (Real College Scorecard Data)")
            print("-" * 60)
            us_col = 'united states_value_score'
            for idx, row in results['united states_top'].iterrows():
                uni_name = row['institution'][:35] + '...' if len(row['institution']) > 35 else row['institution']
                score = row.get(us_col, row.get('value_score', 0))
                print(f"{uni_name:<38} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {score:>5.1f}")
        
        if 'united kingdom_top' in results:
            print(f"\n🇬🇧 BEST VALUE UK UNIVERSITIES (International Students)")
            print("-" * 60)
            uk_col = 'united kingdom_value_score'
            for idx, row in results['united kingdom_top'].iterrows():
                uni_name = row['institution'][:35] + '...' if len(row['institution']) > 35 else row['institution']
                score = row.get(uk_col, row.get('value_score', 0))
                print(f"{uni_name:<38} | Rank: {row['rank']:>3.0f} | {row['price_formatted']:>8} | Score: {score:>5.1f}")
        
        # Key insights
        print(f"\n📊 KEY INSIGHTS FROM REAL DATA:")
        elite_count = len(results.get('elite_bargains', []))
        budget_count = len(results.get('budget_champions', []))
        print(f"• Elite Bargains Found: {elite_count} universities combine top rankings with reasonable prices")
        print(f"• Budget Champions: {budget_count} universities offer lowest-cost education")
        print(f"• Real College Scorecard data reveals actual published tuition rates")
        print(f"• ARWU rankings focus on research excellence and academic output")
        print(f"• Price-ranking correlation varies significantly by country")
        
        if self.data is not None:
            cheapest = self.data.loc[self.data['price_usd'].idxmin()]
            print(f"• Cheapest option: {cheapest['institution']} (${cheapest['price_usd']:,.0f})")
            
            if 'overall_top' in results and not results['overall_top'].empty:
                best_value = results['overall_top'].iloc[0]
                print(f"• Best overall value: {best_value['institution']} (Score: {best_value['value_score']:.1f})")

def main():
    """Main execution."""
    analyzer = RealSweetSpotAnalyzer()
    
    if not analyzer.load_data():
        return
        
    # Calculate value scores
    df_with_scores = analyzer.calculate_value_scores()
    
    # Find sweet spots
    sweet_spot_results = analyzer.find_sweet_spots(df_with_scores)
    
    # Print analysis
    analyzer.print_sweet_spot_analysis(sweet_spot_results)
    
    # Create visualization
    fig = analyzer.create_sweet_spot_visualization(df_with_scores)
    fig.savefig('real_sweet_spot_analysis.png', dpi=300, bbox_inches='tight')
    logger.info("Saved: real_sweet_spot_analysis.png")
    
    # Save value analysis
    df_with_scores.to_csv('real_value_analysis.csv', index=False)
    logger.info("Saved: real_value_analysis.csv")
    
    plt.show()
    
    return sweet_spot_results

if __name__ == "__main__":
    main()