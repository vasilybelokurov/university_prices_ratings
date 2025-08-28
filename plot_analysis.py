#!/usr/bin/env python3
"""
University Price vs Rating Analysis and Visualization
Combines US and UK university data to create comparative plots.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, Optional
import logging
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class UniversityAnalyzer:
    def __init__(self):
        self.us_data = None
        self.uk_data = None
        self.combined_data = None
        
    def load_data(self) -> bool:
        """Load US and UK university data."""
        try:
            logger.info("Loading university datasets...")
            self.us_data = pd.read_csv("us_universities_sample.csv")
            self.uk_data = pd.read_csv("uk_universities_sample.csv")
            logger.info(f"Loaded {len(self.us_data)} US universities and {len(self.uk_data)} UK universities")
            return True
        except FileNotFoundError as e:
            logger.error(f"Data files not found: {e}")
            return False
            
    def prepare_data(self) -> pd.DataFrame:
        """Prepare and combine US and UK data for analysis."""
        logger.info("Preparing combined dataset...")
        
        # Prepare US data
        us_prep = self.us_data.copy()
        us_prep['country'] = 'US'
        us_prep['price_usd'] = us_prep['tuition']  # Already in USD
        us_prep['rank'] = us_prep['ranking']
        
        # Prepare UK data - convert GBP to USD (approximate rate: 1 GBP = 1.27 USD)
        uk_prep = self.uk_data.copy()
        uk_prep['country'] = 'UK'
        # Use international tuition for UK as it varies more and is more comparable
        uk_prep['price_usd'] = uk_prep['intl_tuition'] * 1.27  # Convert to USD
        uk_prep['rank'] = uk_prep['composite_rank']
        
        # Combine datasets
        us_subset = us_prep[['name', 'country', 'price_usd', 'rank', 'type']].copy()
        uk_subset = uk_prep[['name', 'country', 'price_usd', 'rank']].copy()
        uk_subset['type'] = 'public'  # Most UK unis are publicly funded
        
        combined = pd.concat([us_subset, uk_subset], ignore_index=True)
        combined = combined.dropna(subset=['price_usd', 'rank'])
        
        self.combined_data = combined
        logger.info(f"Combined dataset: {len(combined)} universities")
        return combined
        
    def calculate_correlations(self, df: pd.DataFrame) -> Dict:
        """Calculate correlation coefficients."""
        correlations = {}
        
        # Overall correlation
        pearson_r, pearson_p = pearsonr(df['price_usd'], df['rank'])
        spearman_r, spearman_p = spearmanr(df['price_usd'], df['rank'])
        
        correlations['overall'] = {
            'pearson': {'r': pearson_r, 'p': pearson_p},
            'spearman': {'r': spearman_r, 'p': spearman_p}
        }
        
        # By country
        for country in ['US', 'UK']:
            country_data = df[df['country'] == country]
            if len(country_data) > 3:
                pr, pp = pearsonr(country_data['price_usd'], country_data['rank'])
                sr, sp = spearmanr(country_data['price_usd'], country_data['rank'])
                correlations[country] = {
                    'pearson': {'r': pr, 'p': pp},
                    'spearman': {'r': sr, 'p': sp}
                }
        
        return correlations
        
    def create_scatter_plot(self, df: pd.DataFrame) -> plt.Figure:
        """Create scatter plot of price vs ranking."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Separate by country
        countries = df['country'].unique()
        colors = ['#1f77b4', '#ff7f0e']  # Blue for US, Orange for UK
        
        for i, country in enumerate(countries):
            country_data = df[df['country'] == country]
            ax.scatter(country_data['rank'], country_data['price_usd'], 
                      c=colors[i], label=f'{country} ({len(country_data)} unis)',
                      alpha=0.7, s=60)
        
        # Add regression lines
        for i, country in enumerate(countries):
            country_data = df[df['country'] == country]
            if len(country_data) > 2:
                # Fit regression
                X = country_data['rank'].values.reshape(-1, 1)
                y = country_data['price_usd'].values
                reg = LinearRegression().fit(X, y)
                
                # Plot regression line
                x_range = np.linspace(country_data['rank'].min(), country_data['rank'].max(), 100)
                y_pred = reg.predict(x_range.reshape(-1, 1))
                ax.plot(x_range, y_pred, '--', color=colors[i], alpha=0.8, linewidth=2)
        
        ax.set_xlabel('University Ranking (lower is better)', fontsize=12)
        ax.set_ylabel('Annual Tuition (USD)', fontsize=12)
        ax.set_title('University Rankings vs Annual Tuition Costs\nUS vs UK Comparison', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        return fig
        
    def create_boxplot(self, df: pd.DataFrame) -> plt.Figure:
        """Create boxplot comparing price distributions by country."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Price distribution by country
        sns.boxplot(data=df, x='country', y='price_usd', ax=ax1)
        ax1.set_title('Tuition Distribution by Country', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Annual Tuition (USD)', fontsize=12)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Ranking distribution by country
        sns.boxplot(data=df, x='country', y='rank', ax=ax2)
        ax2.set_title('Ranking Distribution by Country', fontsize=14, fontweight='bold')
        ax2.set_ylabel('University Ranking', fontsize=12)
        ax2.invert_yaxis()  # Lower rankings are better
        
        plt.tight_layout()
        return fig
        
    def create_density_plot(self, df: pd.DataFrame) -> plt.Figure:
        """Create density plots of price and ranking distributions."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Price density
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            ax1.hist(country_data['price_usd'], alpha=0.6, density=True, 
                    bins=15, label=f'{country}')
        ax1.set_xlabel('Annual Tuition (USD)', fontsize=12)
        ax1.set_ylabel('Density', fontsize=12)
        ax1.set_title('Tuition Cost Distribution', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        # Ranking density  
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            ax2.hist(country_data['rank'], alpha=0.6, density=True,
                    bins=15, label=f'{country}')
        ax2.set_xlabel('University Ranking', fontsize=12)
        ax2.set_ylabel('Density', fontsize=12) 
        ax2.set_title('Ranking Distribution', fontsize=14, fontweight='bold')
        ax2.legend()
        
        plt.tight_layout()
        return fig
        
    def print_summary_statistics(self, df: pd.DataFrame, correlations: Dict):
        """Print comprehensive summary statistics."""
        print("=" * 60)
        print("UNIVERSITY PRICE vs RANKING ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Dataset overview
        print(f"\nDataset Overview:")
        print(f"  Total universities: {len(df)}")
        for country in df['country'].unique():
            count = len(df[df['country'] == country])
            print(f"  {country} universities: {count}")
            
        # Price statistics by country
        print(f"\nTuition Statistics (USD):")
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            print(f"  {country}:")
            print(f"    Range: ${country_data['price_usd'].min():,.0f} - ${country_data['price_usd'].max():,.0f}")
            print(f"    Mean: ${country_data['price_usd'].mean():,.0f}")
            print(f"    Median: ${country_data['price_usd'].median():,.0f}")
            print(f"    Std Dev: ${country_data['price_usd'].std():,.0f}")
            
        # Ranking statistics
        print(f"\nRanking Statistics:")
        for country in df['country'].unique():
            country_data = df[df['country'] == country]
            print(f"  {country}:")
            print(f"    Best rank: {country_data['rank'].min():.1f}")
            print(f"    Worst rank: {country_data['rank'].max():.1f}")
            print(f"    Mean rank: {country_data['rank'].mean():.1f}")
            
        # Correlation analysis
        print(f"\nCorrelation Analysis (Price vs Rank):")
        for key, corr_data in correlations.items():
            print(f"  {key.upper()}:")
            print(f"    Pearson r = {corr_data['pearson']['r']:.3f} (p = {corr_data['pearson']['p']:.3f})")
            print(f"    Spearman ρ = {corr_data['spearman']['r']:.3f} (p = {corr_data['spearman']['p']:.3f})")
            
        # Interpretation
        print(f"\nKey Findings:")
        overall_corr = correlations['overall']['pearson']['r']
        if overall_corr < -0.5:
            print(f"  • Strong negative correlation ({overall_corr:.3f}): Higher rankings (lower numbers) associated with higher prices")
        elif overall_corr < -0.3:
            print(f"  • Moderate negative correlation ({overall_corr:.3f}): Some association between ranking and price")
        else:
            print(f"  • Weak correlation ({overall_corr:.3f}): Limited association between ranking and price")
            
        # Compare countries
        if 'US' in correlations and 'UK' in correlations:
            us_corr = correlations['US']['pearson']['r']
            uk_corr = correlations['UK']['pearson']['r']
            print(f"  • US shows {'stronger' if abs(us_corr) > abs(uk_corr) else 'weaker'} price-ranking correlation than UK")

def main():
    """Main analysis execution."""
    logger.info("Starting university price vs ranking analysis...")
    
    analyzer = UniversityAnalyzer()
    
    # Load and prepare data
    if not analyzer.load_data():
        logger.error("Failed to load data files. Run data collection scripts first.")
        return
        
    df = analyzer.prepare_data()
    correlations = analyzer.calculate_correlations(df)
    
    # Print summary statistics
    analyzer.print_summary_statistics(df, correlations)
    
    # Create visualizations
    logger.info("Creating visualizations...")
    
    # Scatter plot
    fig1 = analyzer.create_scatter_plot(df)
    fig1.savefig('university_price_vs_ranking_scatter.png', dpi=300, bbox_inches='tight')
    logger.info("Saved: university_price_vs_ranking_scatter.png")
    
    # Box plots
    fig2 = analyzer.create_boxplot(df)
    fig2.savefig('university_distributions_boxplot.png', dpi=300, bbox_inches='tight')
    logger.info("Saved: university_distributions_boxplot.png")
    
    # Density plots
    fig3 = analyzer.create_density_plot(df)
    fig3.savefig('university_density_plots.png', dpi=300, bbox_inches='tight')
    logger.info("Saved: university_density_plots.png")
    
    # Save combined dataset
    df.to_csv('combined_university_data.csv', index=False)
    logger.info("Saved: combined_university_data.csv")
    
    plt.show()
    
    logger.info("Analysis complete!")
    return df, correlations

if __name__ == "__main__":
    main()