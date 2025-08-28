#!/usr/bin/env python3
"""
Analysis of Real University Data
Uses actual ARWU rankings and College Scorecard API data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class RealDataAnalyzer:
    def __init__(self):
        self.data = None
        
    def load_real_data(self) -> pd.DataFrame:
        """Load the real university data."""
        try:
            df = pd.read_csv('real_university_data.csv')
            logger.info(f"Loaded real data: {len(df)} universities")
            
            # Clean data - remove rows without price or rank
            df_clean = df.dropna(subset=['price_usd', 'rank']).copy()
            logger.info(f"Clean data after removing NaN: {len(df_clean)} universities")
            
            self.data = df_clean
            return df_clean
            
        except FileNotFoundError:
            logger.error("Real data file not found. Run collect_real_data.py first.")
            return pd.DataFrame()
    
    def analyze_correlations(self) -> dict:
        """Analyze price-ranking correlations."""
        if self.data is None or self.data.empty:
            return {}
            
        df = self.data
        correlations = {}
        
        # Overall correlation
        if len(df) > 3:
            pearson_r, pearson_p = pearsonr(df['price_usd'], df['rank'])
            spearman_r, spearman_p = spearmanr(df['price_usd'], df['rank'])
            
            correlations['overall'] = {
                'pearson': {'r': pearson_r, 'p': pearson_p},
                'spearman': {'r': spearman_r, 'p': spearman_p},
                'n': len(df)
            }
        
        # By country
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            if len(country_data) > 3:
                pr, pp = pearsonr(country_data['price_usd'], country_data['rank'])
                sr, sp = spearmanr(country_data['price_usd'], country_data['rank'])
                correlations[country] = {
                    'pearson': {'r': pr, 'p': pp},
                    'spearman': {'r': sr, 'p': sp},
                    'n': len(country_data)
                }
        
        return correlations
    
    def create_real_data_plots(self) -> tuple:
        """Create comprehensive plots of real data."""
        if self.data is None or self.data.empty:
            logger.error("No data to plot")
            return None, None
            
        df = self.data
        
        # Main scatter plot
        fig1, ax1 = plt.subplots(figsize=(12, 8))
        
        countries = df['country'].unique()
        colors = ['#1f77b4', '#ff7f0e']  # Blue for US, Orange for UK
        
        for i, country in enumerate(countries):
            country_data = df[df['country'] == country]
            ax1.scatter(country_data['rank'], country_data['price_usd'], 
                       c=colors[i], label=f'{country} ({len(country_data)} unis)',
                       alpha=0.7, s=80)
            
            # Add regression line if enough data points
            if len(country_data) > 2:
                X = country_data['rank'].values.reshape(-1, 1)
                y = country_data['price_usd'].values
                reg = LinearRegression().fit(X, y)
                
                x_range = np.linspace(country_data['rank'].min(), 
                                     country_data['rank'].max(), 100)
                y_pred = reg.predict(x_range.reshape(-1, 1))
                ax1.plot(x_range, y_pred, '--', color=colors[i], 
                        alpha=0.8, linewidth=2)
        
        # Annotate notable universities
        notable_unis = [
            'Harvard University', 'Stanford University', 'Massachusetts Institute of Technology',
            'University of Cambridge', 'University of Oxford', 'University of Chicago'
        ]
        
        for _, row in df.iterrows():
            if any(uni in row['institution'] for uni in notable_unis):
                ax1.annotate(row['institution'].split(',')[0].replace('University of ', ''), 
                           (row['rank'], row['price_usd']),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.8)
        
        ax1.set_xlabel('ARWU Ranking (lower is better)', fontsize=12)
        ax1.set_ylabel('Annual Tuition (USD)', fontsize=12)
        ax1.set_title('University Rankings vs Tuition Costs\nReal Data from ARWU + College Scorecard API', 
                     fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Summary statistics subplot
        fig2, ((ax2, ax3), (ax4, ax5)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Price distribution by country
        for country in countries:
            country_data = df[df['country'] == country]
            ax2.hist(country_data['price_usd'], alpha=0.6, bins=10,
                    label=f'{country} (n={len(country_data)})', density=True)
        ax2.set_xlabel('Annual Tuition (USD)')
        ax2.set_ylabel('Density')
        ax2.set_title('Tuition Distribution by Country (Real Data)')
        ax2.legend()
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # Ranking distribution
        for country in countries:
            country_data = df[df['country'] == country]
            ax3.hist(country_data['rank'], alpha=0.6, bins=10,
                    label=f'{country}', density=True)
        ax3.set_xlabel('ARWU Ranking')
        ax3.set_ylabel('Density')
        ax3.set_title('Ranking Distribution by Country')
        ax3.legend()
        
        # Box plots
        sns.boxplot(data=df, x='country', y='price_usd', ax=ax4)
        ax4.set_title('Price Distribution by Country')
        ax4.set_ylabel('Annual Tuition (USD)')
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # Top universities table
        ax5.axis('tight')
        ax5.axis('off')
        
        top_unis = df.nsmallest(15, 'rank')[['institution', 'country', 'rank', 'price_usd']]
        top_unis['price_formatted'] = top_unis['price_usd'].apply(lambda x: f'${x:,.0f}')
        top_unis['institution_short'] = top_unis['institution'].apply(
            lambda x: x[:30] + '...' if len(x) > 30 else x
        )
        
        table_data = top_unis[['institution_short', 'country', 'rank', 'price_formatted']].values
        table = ax5.table(cellText=table_data, 
                         colLabels=['University', 'Country', 'Rank', 'Price (USD)'],
                         cellLoc='left', loc='center', fontsize=8)
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        ax5.set_title('Top 15 Universities by ARWU Ranking (Real Data)', 
                     fontsize=12, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        return fig1, fig2
    
    def print_real_data_analysis(self, correlations: dict):
        """Print comprehensive analysis of real data."""
        if self.data is None or self.data.empty:
            print("No data available for analysis")
            return
            
        df = self.data
        
        print("=" * 80)
        print("REAL UNIVERSITY DATA ANALYSIS")
        print("=" * 80)
        
        print(f"\nData Sources:")
        print(f"• Rankings: ARWU 2023 (Shanghai Rankings)")
        print(f"• US Tuition: College Scorecard API (US Dept of Education)")
        print(f"• UK Fees: Official university data + mock international rates")
        
        print(f"\nDataset Overview:")
        print(f"• Total universities: {len(df)}")
        us_count = len(df[df['country'] == 'United States'])
        uk_count = len(df[df['country'] == 'United Kingdom'])
        print(f"• US universities: {us_count}")
        print(f"• UK universities: {uk_count}")
        
        print(f"\nPrice Statistics (USD):")
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            print(f"  {country}:")
            print(f"    Range: ${country_data['price_usd'].min():,.0f} - ${country_data['price_usd'].max():,.0f}")
            print(f"    Mean: ${country_data['price_usd'].mean():,.0f}")
            print(f"    Median: ${country_data['price_usd'].median():,.0f}")
            print(f"    Std Dev: ${country_data['price_usd'].std():,.0f}")
        
        print(f"\nRanking Statistics:")
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            print(f"  {country}:")
            print(f"    Best rank: {country_data['rank'].min()}")
            print(f"    Worst rank: {country_data['rank'].max()}")
            print(f"    Mean rank: {country_data['rank'].mean():.1f}")
        
        print(f"\nCorrelation Analysis (Price vs Rank):")
        for key, corr_data in correlations.items():
            print(f"  {key.upper()} (n={corr_data['n']}):")
            print(f"    Pearson r = {corr_data['pearson']['r']:.3f} (p = {corr_data['pearson']['p']:.3f})")
            print(f"    Spearman ρ = {corr_data['spearman']['r']:.3f} (p = {corr_data['spearman']['p']:.3f})")
        
        # Data quality assessment
        print(f"\nData Quality Assessment:")
        total_possible = len(df)
        price_complete = df['price_usd'].notna().sum()
        print(f"• Price data completeness: {price_complete}/{total_possible} ({100*price_complete/total_possible:.1f}%)")
        
        us_data = df[df['country'] == 'United States']
        us_real = us_data['tuition_in_state_usd'].notna().sum()
        print(f"• US real tuition data: {us_real}/{len(us_data)} ({100*us_real/len(us_data):.1f}%)")
        
        # Key findings
        print(f"\nKey Findings from Real Data:")
        overall_corr = correlations.get('overall', {}).get('pearson', {}).get('r', 0)
        if overall_corr < -0.5:
            print(f"• Strong negative correlation ({overall_corr:.3f}): Better rankings = Higher prices")
        elif overall_corr < -0.3:
            print(f"• Moderate negative correlation ({overall_corr:.3f}): Some price-ranking relationship")
        else:
            print(f"• Weak correlation ({overall_corr:.3f}): Limited price-ranking relationship")
        
        # Compare US vs UK
        us_corr = correlations.get('United States', {}).get('pearson', {}).get('r', 0)
        uk_corr = correlations.get('United Kingdom', {}).get('pearson', {}).get('r', 0)
        if us_corr and uk_corr:
            stronger = 'US' if abs(us_corr) > abs(uk_corr) else 'UK'
            print(f"• {stronger} shows stronger price-ranking correlation")
        
        # Extreme values
        cheapest = df.loc[df['price_usd'].idxmin()]
        most_expensive = df.loc[df['price_usd'].idxmax()]
        best_rank = df.loc[df['rank'].idxmin()]
        
        print(f"\nExtreme Values:")
        print(f"• Cheapest: {cheapest['institution']} - ${cheapest['price_usd']:,.0f} (Rank {cheapest['rank']})")
        print(f"• Most expensive: {most_expensive['institution']} - ${most_expensive['price_usd']:,.0f} (Rank {most_expensive['rank']})")
        print(f"• Best ranked: {best_rank['institution']} - Rank {best_rank['rank']} (${best_rank['price_usd']:,.0f})")

def main():
    """Main analysis execution."""
    analyzer = RealDataAnalyzer()
    
    # Load real data
    df = analyzer.load_real_data()
    if df.empty:
        logger.error("No data to analyze")
        return
    
    # Analyze correlations
    correlations = analyzer.analyze_correlations()
    
    # Print analysis
    analyzer.print_real_data_analysis(correlations)
    
    # Create plots
    fig1, fig2 = analyzer.create_real_data_plots()
    
    if fig1 is not None:
        fig1.savefig('real_data_scatter_plot.png', dpi=300, bbox_inches='tight')
        logger.info("Saved: real_data_scatter_plot.png")
        
        fig2.savefig('real_data_analysis_summary.png', dpi=300, bbox_inches='tight')
        logger.info("Saved: real_data_analysis_summary.png")
        
        plt.show()
    
    return df, correlations

if __name__ == "__main__":
    main()