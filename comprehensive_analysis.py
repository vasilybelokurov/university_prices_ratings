#!/usr/bin/env python3
"""
Comprehensive analysis of university price vs ranking data.
Analyzes 457 universities (387 US, 70 UK) with real tuition and ranking data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveUniversityAnalysis:
    def __init__(self, data_file: str = "massive_university_data.csv"):
        """Initialize with comprehensive dataset."""
        self.data_file = data_file
        self.df = None
        self.us_df = None
        self.uk_df = None
        
    def load_and_process_data(self):
        """Load and process the comprehensive dataset."""
        logger.info(f"Loading data from {self.data_file}")
        self.df = pd.read_csv(self.data_file)
        
        # Basic data cleaning
        self.df = self.df.dropna(subset=['price_usd', 'arwu_rank'])
        
        # Calculate percentiles for value analysis
        self._calculate_percentiles()
        
        # Split by country AFTER calculating percentiles
        self.us_df = self.df[self.df['country'] == 'United States'].copy()
        self.uk_df = self.df[self.df['country'] == 'United Kingdom'].copy()
        
        logger.info(f"Loaded {len(self.df)} universities total")
        logger.info(f"US universities: {len(self.us_df)}")
        logger.info(f"UK universities: {len(self.uk_df)}")
        
    def _calculate_percentiles(self):
        """Calculate rank and price percentiles for value scoring."""
        # Overall percentiles - better ranking = higher rank percentile
        self.df['rank_percentile'] = ((len(self.df) + 1 - self.df['arwu_rank'].rank(method='min')) / len(self.df)) * 100
        self.df['price_percentile'] = (self.df['price_usd'].rank(method='average') / len(self.df)) * 100
        
        # Country-specific percentiles
        for country in ['United States', 'United Kingdom']:
            mask = self.df['country'] == country
            country_data = self.df[mask]
            
            rank_percentiles = ((len(country_data) + 1 - country_data['arwu_rank'].rank(method='min')) / len(country_data)) * 100
            price_percentiles = (country_data['price_usd'].rank(method='average') / len(country_data)) * 100
            
            country_clean = country.lower().replace(' ', '_')
            self.df.loc[mask, f'{country_clean}_rank_percentile'] = rank_percentiles
            self.df.loc[mask, f'{country_clean}_price_percentile'] = price_percentiles
        
        # Calculate value scores (60% ranking weight, 40% price weight)
        # Higher rank percentile (better ranking) and lower price percentile (cheaper) = higher value
        self.df['value_score'] = (0.6 * self.df['rank_percentile']) + (0.4 * (100 - self.df['price_percentile']))
        
        # Country-specific value scores
        for country in ['United States', 'United Kingdom']:
            country_clean = country.lower().replace(' ', '_')
            rank_col = f'{country_clean}_rank_percentile'
            price_col = f'{country_clean}_price_percentile'
            value_col = f'{country_clean}_value_score'
            
            mask = self.df['country'] == country
            if rank_col in self.df.columns and price_col in self.df.columns:
                self.df.loc[mask, value_col] = (
                    0.6 * self.df.loc[mask, rank_col] + 
                    0.4 * (100 - self.df.loc[mask, price_col])
                )
    
    def generate_summary_statistics(self):
        """Generate comprehensive summary statistics."""
        print("=" * 80)
        print("COMPREHENSIVE UNIVERSITY ANALYSIS - SUMMARY STATISTICS")
        print("=" * 80)
        
        # Overall statistics
        print(f"\nDATASET OVERVIEW:")
        print(f"Total universities analyzed: {len(self.df)}")
        print(f"US universities: {len(self.us_df)}")
        print(f"UK universities: {len(self.uk_df)}")
        
        # Price statistics
        print(f"\nPRICE STATISTICS (USD):")
        print(f"Overall price range: ${self.df['price_usd'].min():,.0f} - ${self.df['price_usd'].max():,.0f}")
        print(f"Overall median price: ${self.df['price_usd'].median():,.0f}")
        print(f"US median price: ${self.us_df['price_usd'].median():,.0f}")
        print(f"UK median price: ${self.uk_df['price_usd'].median():,.0f}")
        
        # Ranking statistics
        print(f"\nRANKING STATISTICS (ARWU):")
        print(f"Overall ranking range: {self.df['arwu_rank'].min()} - {self.df['arwu_rank'].max()}")
        print(f"US best ranking: {self.us_df['arwu_rank'].min()}")
        print(f"UK best ranking: {self.uk_df['arwu_rank'].min()}")
        
        # Correlation analysis
        self._correlation_analysis()
        
        # Top value universities
        self._top_value_universities()
        
    def _correlation_analysis(self):
        """Perform correlation analysis between price and ranking."""
        print(f"\nCORRELATION ANALYSIS:")
        
        # Overall correlations
        overall_pearson, p_val_p = pearsonr(self.df['price_usd'], self.df['arwu_rank'])
        overall_spearman, p_val_s = spearmanr(self.df['price_usd'], self.df['arwu_rank'])
        
        print(f"Overall Pearson correlation (price vs rank): r = {overall_pearson:.3f} (p = {p_val_p:.3e})")
        print(f"Overall Spearman correlation (price vs rank): ρ = {overall_spearman:.3f} (p = {p_val_s:.3e})")
        
        # US correlations
        us_pearson, us_p_val_p = pearsonr(self.us_df['price_usd'], self.us_df['arwu_rank'])
        us_spearman, us_p_val_s = spearmanr(self.us_df['price_usd'], self.us_df['arwu_rank'])
        
        print(f"US Pearson correlation: r = {us_pearson:.3f} (p = {us_p_val_p:.3e})")
        print(f"US Spearman correlation: ρ = {us_spearman:.3f} (p = {us_p_val_s:.3e})")
        
        # UK correlations
        uk_pearson, uk_p_val_p = pearsonr(self.uk_df['price_usd'], self.uk_df['arwu_rank'])
        uk_spearman, uk_p_val_s = spearmanr(self.uk_df['price_usd'], self.uk_df['arwu_rank'])
        
        print(f"UK Pearson correlation: r = {uk_pearson:.3f} (p = {uk_p_val_p:.3e})")
        print(f"UK Spearman correlation: ρ = {uk_spearman:.3f} (p = {uk_p_val_s:.3e})")
        
    def _top_value_universities(self):
        """Identify top value universities."""
        print(f"\nTOP 20 VALUE UNIVERSITIES (Overall):")
        top_overall = self.df.nlargest(20, 'value_score')[
            ['institution', 'country', 'arwu_rank', 'price_usd', 'value_score']
        ]
        for i, (_, row) in enumerate(top_overall.iterrows(), 1):
            print(f"{i:2d}. {row['institution'][:50]:<50} | "
                  f"Rank: {row['arwu_rank']:3d} | "
                  f"Price: ${row['price_usd']:6,.0f} | "
                  f"Score: {row['value_score']:5.1f}")
        
        print(f"\nTOP 10 VALUE US UNIVERSITIES:")
        us_value_col = 'united_states_value_score'
        if us_value_col in self.us_df.columns:
            top_us = self.us_df.nlargest(10, us_value_col)[
                ['institution', 'arwu_rank', 'price_usd', us_value_col]
            ]
            for i, (_, row) in enumerate(top_us.iterrows(), 1):
                print(f"{i:2d}. {row['institution'][:45]:<45} | "
                      f"Rank: {row['arwu_rank']:3d} | "
                      f"Price: ${row['price_usd']:6,.0f} | "
                      f"Score: {row[us_value_col]:5.1f}")
        
        print(f"\nTOP 10 VALUE UK UNIVERSITIES:")
        uk_value_col = 'united_kingdom_value_score'
        if uk_value_col in self.uk_df.columns:
            top_uk = self.uk_df.nlargest(10, uk_value_col)[
                ['institution', 'arwu_rank', 'price_usd', uk_value_col]
            ]
            for i, (_, row) in enumerate(top_uk.iterrows(), 1):
                print(f"{i:2d}. {row['institution'][:45]:<45} | "
                      f"Rank: {row['arwu_rank']:3d} | "
                      f"Price: ${row['price_usd']:6,.0f} | "
                      f"Score: {row[uk_value_col]:5.1f}")
    
    def create_comprehensive_plots(self):
        """Create comprehensive visualization plots."""
        logger.info("Creating comprehensive plots...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Main scatter plot: Price vs Ranking
        ax1 = plt.subplot(2, 3, 1)
        
        # Plot US universities
        us_scatter = ax1.scatter(self.us_df['arwu_rank'], self.us_df['price_usd'], 
                                alpha=0.6, s=50, label=f'US (n={len(self.us_df)})', color='blue')
        
        # Plot UK universities
        uk_scatter = ax1.scatter(self.uk_df['arwu_rank'], self.uk_df['price_usd'], 
                                alpha=0.6, s=50, label=f'UK (n={len(self.uk_df)})', color='red')
        
        ax1.set_xlabel('ARWU Ranking (Lower is Better)')
        ax1.set_ylabel('Annual Tuition (USD)')
        ax1.set_title('University Ranking vs Tuition Cost\n457 Universities Total')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add trend lines
        z_us = np.polyfit(self.us_df['arwu_rank'], self.us_df['price_usd'], 1)
        p_us = np.poly1d(z_us)
        ax1.plot(self.us_df['arwu_rank'], p_us(self.us_df['arwu_rank']), "b--", alpha=0.8, linewidth=2)
        
        z_uk = np.polyfit(self.uk_df['arwu_rank'], self.uk_df['price_usd'], 1)
        p_uk = np.poly1d(z_uk)
        ax1.plot(self.uk_df['arwu_rank'], p_uk(self.uk_df['arwu_rank']), "r--", alpha=0.8, linewidth=2)
        
        # 2. Price distribution
        ax2 = plt.subplot(2, 3, 2)
        bins = np.linspace(0, 80000, 30)
        ax2.hist(self.us_df['price_usd'], bins=bins, alpha=0.6, label='US', color='blue', density=True)
        ax2.hist(self.uk_df['price_usd'], bins=bins, alpha=0.6, label='UK', color='red', density=True)
        ax2.set_xlabel('Annual Tuition (USD)')
        ax2.set_ylabel('Density')
        ax2.set_title('Distribution of Tuition Costs')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Ranking distribution
        ax3 = plt.subplot(2, 3, 3)
        rank_bins = np.linspace(1, 500, 25)
        ax3.hist(self.us_df['arwu_rank'], bins=rank_bins, alpha=0.6, label='US', color='blue', density=True)
        ax3.hist(self.uk_df['arwu_rank'], bins=rank_bins, alpha=0.6, label='UK', color='red', density=True)
        ax3.set_xlabel('ARWU Ranking')
        ax3.set_ylabel('Density')
        ax3.set_title('Distribution of University Rankings')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Value score scatter
        ax4 = plt.subplot(2, 3, 4)
        ax4.scatter(self.us_df['arwu_rank'], self.us_df['value_score'], 
                   alpha=0.6, s=50, label='US', color='blue')
        ax4.scatter(self.uk_df['arwu_rank'], self.uk_df['value_score'], 
                   alpha=0.6, s=50, label='UK', color='red')
        ax4.set_xlabel('ARWU Ranking')
        ax4.set_ylabel('Value Score')
        ax4.set_title('University Rankings vs Value Score')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Top value universities bar chart
        ax5 = plt.subplot(2, 3, 5)
        top_10_overall = self.df.nlargest(10, 'value_score')
        colors = ['blue' if country == 'United States' else 'red' 
                 for country in top_10_overall['country']]
        
        bars = ax5.barh(range(len(top_10_overall)), top_10_overall['value_score'], color=colors, alpha=0.7)
        ax5.set_yticks(range(len(top_10_overall)))
        ax5.set_yticklabels([name[:20] + ('...' if len(name) > 20 else '') 
                            for name in top_10_overall['institution']], fontsize=8)
        ax5.set_xlabel('Value Score')
        ax5.set_title('Top 10 Value Universities')
        ax5.grid(True, alpha=0.3)
        
        # Add value scores as text on bars
        for i, (bar, score) in enumerate(zip(bars, top_10_overall['value_score'])):
            ax5.text(score + 1, i, f'{score:.1f}', va='center', fontsize=8)
        
        # 6. Price vs Value Score
        ax6 = plt.subplot(2, 3, 6)
        ax6.scatter(self.us_df['price_usd'], self.us_df['value_score'], 
                   alpha=0.6, s=50, label='US', color='blue')
        ax6.scatter(self.uk_df['price_usd'], self.uk_df['value_score'], 
                   alpha=0.6, s=50, label='UK', color='red')
        ax6.set_xlabel('Annual Tuition (USD)')
        ax6.set_ylabel('Value Score')
        ax6.set_title('Tuition Cost vs Value Score')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('comprehensive_university_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info("Comprehensive plots saved as comprehensive_university_analysis.png")
    
    def save_processed_data(self):
        """Save the processed data with value scores."""
        output_file = "comprehensive_university_analysis.csv"
        self.df.to_csv(output_file, index=False)
        logger.info(f"Processed data saved to {output_file}")
        return output_file


def main():
    analyzer = ComprehensiveUniversityAnalysis()
    
    try:
        # Load and process data
        analyzer.load_and_process_data()
        
        # Generate summary statistics
        analyzer.generate_summary_statistics()
        
        # Create comprehensive plots
        analyzer.create_comprehensive_plots()
        
        # Save processed data
        analyzer.save_processed_data()
        
        print("\n" + "=" * 80)
        print("COMPREHENSIVE ANALYSIS COMPLETE")
        print("=" * 80)
        print("Files generated:")
        print("- comprehensive_university_analysis.png (plots)")
        print("- comprehensive_university_analysis.csv (processed data)")
        
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        raise


if __name__ == "__main__":
    main()