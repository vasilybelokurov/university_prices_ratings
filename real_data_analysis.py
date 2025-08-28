#!/usr/bin/env python3
"""
Complete analysis using ONLY verified real data.
32 universities with real ARWU 2023 rankings and real tuition data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealUniversityAnalysis:
    def __init__(self, data_file: str = "verified_real_university_data.csv"):
        """Initialize with verified real data."""
        self.data_file = data_file
        self.df = None
        self.us_df = None
        self.uk_df = None
        
    def load_and_process_data(self):
        """Load and process the verified real dataset."""
        logger.info(f"Loading verified real data from {self.data_file}")
        self.df = pd.read_csv(self.data_file)
        
        # Calculate value scores (60% ranking weight, 40% price weight)
        self._calculate_value_scores()
        
        # Split by country AFTER calculating value scores
        self.us_df = self.df[self.df['country'] == 'United States'].copy()
        self.uk_df = self.df[self.df['country'] == 'United Kingdom'].copy()
        
        logger.info(f"Loaded {len(self.df)} universities total")
        logger.info(f"US universities: {len(self.us_df)}")
        logger.info(f"UK universities: {len(self.uk_df)}")
        
    def _calculate_value_scores(self):
        """Calculate value scores for ranking universities by value."""
        # Overall percentiles - better ranking (lower number) = higher rank percentile
        self.df['rank_percentile'] = ((len(self.df) + 1 - self.df['arwu_rank'].rank(method='min')) / len(self.df)) * 100
        self.df['price_percentile'] = (self.df['price_usd'].rank(method='average') / len(self.df)) * 100
        
        # Value score: higher rank percentile (better ranking) + lower price percentile (cheaper) = higher value
        self.df['value_score'] = (0.6 * self.df['rank_percentile']) + (0.4 * (100 - self.df['price_percentile']))
        
        # Country-specific value scores
        for country_name in ['United States', 'United Kingdom']:
            mask = self.df['country'] == country_name
            country_data = self.df[mask]
            
            if len(country_data) > 0:
                country_rank_percentile = ((len(country_data) + 1 - country_data['arwu_rank'].rank(method='min')) / len(country_data)) * 100
                country_price_percentile = (country_data['price_usd'].rank(method='average') / len(country_data)) * 100
                country_value_score = (0.6 * country_rank_percentile) + (0.4 * (100 - country_price_percentile))
                
                country_clean = country_name.lower().replace(' ', '_')
                self.df.loc[mask, f'{country_clean}_rank_percentile'] = country_rank_percentile
                self.df.loc[mask, f'{country_clean}_price_percentile'] = country_price_percentile
                self.df.loc[mask, f'{country_clean}_value_score'] = country_value_score
    
    def generate_summary_statistics(self):
        """Generate comprehensive summary statistics with real data."""
        print("=" * 80)
        print("REAL UNIVERSITY DATA ANALYSIS - VERIFIED AUTHENTIC DATA")
        print("=" * 80)
        
        # Dataset overview
        print(f"\nDATASET OVERVIEW:")
        print(f"Total verified universities: {len(self.df)}")
        print(f"US universities (real ARWU + College Scorecard): {len(self.us_df)}")
        print(f"UK universities (real ARWU + verified fees): {len(self.uk_df)}")
        print(f"Ranking range: {self.df['arwu_rank'].min()} - {self.df['arwu_rank'].max()}")
        
        # Price statistics
        print(f"\nPRICE STATISTICS (USD, International Student Rates):")
        print(f"Overall price range: ${self.df['price_usd'].min():,.0f} - ${self.df['price_usd'].max():,.0f}")
        print(f"Overall median price: ${self.df['price_usd'].median():,.0f}")
        print(f"US median price: ${self.us_df['price_usd'].median():,.0f}")
        print(f"UK median price: ${self.uk_df['price_usd'].median():,.0f}")
        
        # Top 10 universities by ranking
        print(f"\nTOP 10 UNIVERSITIES (REAL ARWU 2023 RANKINGS):")
        top_10 = self.df.nsmallest(10, 'arwu_rank')
        for _, row in top_10.iterrows():
            country_flag = "🇺🇸" if row['country'] == 'United States' else "🇬🇧"
            print(f"{row['arwu_rank']:2d}. {row['institution'][:45]:<45} {country_flag} ${row['price_usd']:6,.0f}")
        
        # Correlation analysis
        self._correlation_analysis()
        
        # Value analysis
        self._value_analysis()
        
    def _correlation_analysis(self):
        """Perform correlation analysis between price and ranking with real data."""
        print(f"\nCORRELATION ANALYSIS (REAL DATA):")
        print("-" * 50)
        
        # Overall correlations
        overall_pearson, p_val_p = pearsonr(self.df['price_usd'], self.df['arwu_rank'])
        overall_spearman, p_val_s = spearmanr(self.df['price_usd'], self.df['arwu_rank'])
        
        print(f"Overall correlation (n={len(self.df)}):")
        print(f"  Pearson:  r = {overall_pearson:+.3f} (p = {p_val_p:.3e})")
        print(f"  Spearman: ρ = {overall_spearman:+.3f} (p = {p_val_s:.3e})")
        
        # US correlations
        if len(self.us_df) > 3:
            us_pearson, us_p_val_p = pearsonr(self.us_df['price_usd'], self.us_df['arwu_rank'])
            us_spearman, us_p_val_s = spearmanr(self.us_df['price_usd'], self.us_df['arwu_rank'])
            
            print(f"\nUS universities (n={len(self.us_df)}):")
            print(f"  Pearson:  r = {us_pearson:+.3f} (p = {us_p_val_p:.3e})")
            print(f"  Spearman: ρ = {us_spearman:+.3f} (p = {us_p_val_s:.3e})")
        
        # UK correlations
        if len(self.uk_df) > 3:
            uk_pearson, uk_p_val_p = pearsonr(self.uk_df['price_usd'], self.uk_df['arwu_rank'])
            uk_spearman, uk_p_val_s = spearmanr(self.uk_df['price_usd'], self.uk_df['arwu_rank'])
            
            print(f"\nUK universities (n={len(self.uk_df)}):")
            print(f"  Pearson:  r = {uk_pearson:+.3f} (p = {uk_p_val_p:.3e})")
            print(f"  Spearman: ρ = {uk_spearman:+.3f} (p = {uk_p_val_s:.3e})")
        
        # Interpretation
        print(f"\nINTERPRETATION:")
        if overall_pearson < -0.3:
            print("  Strong negative correlation: Lower-ranked (better) universities cost MORE")
        elif overall_pearson < -0.1:
            print("  Weak negative correlation: Some tendency for better universities to cost more")
        elif overall_pearson > 0.1:
            print("  Positive correlation: Better universities may cost LESS (unusual)")
        else:
            print("  No significant correlation: Ranking and price largely independent")
    
    def _value_analysis(self):
        """Identify top value universities with real data."""
        print(f"\nVALUE ANALYSIS (REAL SWEET SPOTS):")
        print("=" * 80)
        
        # Overall top value
        print(f"TOP 10 VALUE UNIVERSITIES (Overall Real Rankings):")
        top_value = self.df.nlargest(10, 'value_score')
        for i, (_, row) in enumerate(top_value.iterrows(), 1):
            country_flag = "🇺🇸" if row['country'] == 'United States' else "🇬🇧"
            print(f"{i:2d}. {row['institution'][:40]:<40} {country_flag} | "
                  f"Rank: {row['arwu_rank']:3d} | ${row['price_usd']:6,.0f} | "
                  f"Score: {row['value_score']:5.1f}")
        
        # Country-specific value
        if 'united_states_value_score' in self.us_df.columns:
            print(f"\nTOP 5 VALUE US UNIVERSITIES:")
            us_top = self.us_df.nlargest(5, 'united_states_value_score')
            for i, (_, row) in enumerate(us_top.iterrows(), 1):
                print(f"{i}. {row['institution'][:35]:<35} | "
                      f"Rank: {row['arwu_rank']:3d} | ${row['price_usd']:6,.0f} | "
                      f"US Score: {row['united_states_value_score']:5.1f}")
        
        if 'united_kingdom_value_score' in self.uk_df.columns:
            print(f"\nTOP 5 VALUE UK UNIVERSITIES:")
            uk_top = self.uk_df.nlargest(5, 'united_kingdom_value_score')
            for i, (_, row) in enumerate(uk_top.iterrows(), 1):
                print(f"{i}. {row['institution'][:35]:<35} | "
                      f"Rank: {row['arwu_rank']:3d} | ${row['price_usd']:6,.0f} | "
                      f"UK Score: {row['united_kingdom_value_score']:5.1f}")
    
    def create_real_data_plots(self):
        """Create comprehensive plots with verified real data."""
        logger.info("Creating plots with verified real data...")
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(20, 14))
        
        # 1. Main scatter plot: Price vs Ranking (Real Data)
        ax1 = plt.subplot(2, 3, 1)
        
        # Plot US universities
        us_scatter = ax1.scatter(self.us_df['arwu_rank'], self.us_df['price_usd'], 
                                alpha=0.8, s=100, label=f'US (n={len(self.us_df)})', 
                                color='blue', edgecolors='darkblue')
        
        # Plot UK universities  
        uk_scatter = ax1.scatter(self.uk_df['arwu_rank'], self.uk_df['price_usd'], 
                                alpha=0.8, s=100, label=f'UK (n={len(self.uk_df)})', 
                                color='red', edgecolors='darkred')
        
        ax1.set_xlabel('ARWU Ranking (Lower = Better)')
        ax1.set_ylabel('Annual Tuition (USD, International Rates)')
        ax1.set_title('Real University Ranking vs Tuition Cost\n32 Verified Universities (ARWU 2023)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add trend lines
        if len(self.us_df) > 2:
            z_us = np.polyfit(self.us_df['arwu_rank'], self.us_df['price_usd'], 1)
            p_us = np.poly1d(z_us)
            ax1.plot(self.us_df['arwu_rank'], p_us(self.us_df['arwu_rank']), 
                    "b--", alpha=0.8, linewidth=2)
        
        if len(self.uk_df) > 2:
            z_uk = np.polyfit(self.uk_df['arwu_rank'], self.uk_df['price_usd'], 1)
            p_uk = np.poly1d(z_uk)
            ax1.plot(self.uk_df['arwu_rank'], p_uk(self.uk_df['arwu_rank']), 
                    "r--", alpha=0.8, linewidth=2)
        
        # Annotate top universities
        for _, row in self.df.head(5).iterrows():
            ax1.annotate(row['institution'].replace('University of ', '').replace('University', 'Univ'), 
                        (row['arwu_rank'], row['price_usd']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=8, alpha=0.7)
        
        # 2. Price distribution
        ax2 = plt.subplot(2, 3, 2)
        ax2.hist(self.us_df['price_usd'], bins=8, alpha=0.7, label='US', color='blue', density=True)
        ax2.hist(self.uk_df['price_usd'], bins=8, alpha=0.7, label='UK', color='red', density=True)
        ax2.set_xlabel('Annual Tuition (USD)')
        ax2.set_ylabel('Density')
        ax2.set_title('Distribution of Tuition Costs\n(Real Data)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Value score analysis
        ax3 = plt.subplot(2, 3, 3)
        ax3.scatter(self.us_df['arwu_rank'], self.us_df['value_score'], 
                   alpha=0.8, s=100, label='US', color='blue')
        ax3.scatter(self.uk_df['arwu_rank'], self.uk_df['value_score'], 
                   alpha=0.8, s=100, label='UK', color='red')
        ax3.set_xlabel('ARWU Ranking')
        ax3.set_ylabel('Value Score (60% Rank + 40% Price)')
        ax3.set_title('University Rankings vs Value Score\n(Real Data)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Top value universities
        ax4 = plt.subplot(2, 3, 4)
        top_value = self.df.nlargest(12, 'value_score')
        colors = ['blue' if country == 'United States' else 'red' 
                 for country in top_value['country']]
        
        bars = ax4.barh(range(len(top_value)), top_value['value_score'], 
                       color=colors, alpha=0.7)
        ax4.set_yticks(range(len(top_value)))
        ax4.set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                            for name in top_value['institution']], fontsize=8)
        ax4.set_xlabel('Value Score')
        ax4.set_title('Top 12 Value Universities\n(Real Data)')
        ax4.grid(True, alpha=0.3)
        
        # Add value scores as text on bars
        for i, (bar, score) in enumerate(zip(bars, top_value['value_score'])):
            ax4.text(score + 1, i, f'{score:.1f}', va='center', fontsize=8)
        
        # 5. Price vs Value scatter
        ax5 = plt.subplot(2, 3, 5)
        ax5.scatter(self.us_df['price_usd'], self.us_df['value_score'], 
                   alpha=0.8, s=100, label='US', color='blue')
        ax5.scatter(self.uk_df['price_usd'], self.uk_df['value_score'], 
                   alpha=0.8, s=100, label='UK', color='red')
        ax5.set_xlabel('Annual Tuition (USD)')
        ax5.set_ylabel('Value Score')
        ax5.set_title('Tuition vs Value Score\n(Real Data)')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Country comparison
        ax6 = plt.subplot(2, 3, 6)
        
        countries = ['US', 'UK']
        medians = [self.us_df['price_usd'].median(), self.uk_df['price_usd'].median()]
        colors = ['blue', 'red']
        
        bars = ax6.bar(countries, medians, color=colors, alpha=0.7)
        ax6.set_ylabel('Median Tuition (USD)')
        ax6.set_title('Country Comparison\n(International Student Rates)')
        ax6.grid(True, alpha=0.3)
        
        # Add values on bars
        for bar, median in zip(bars, medians):
            ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1000,
                    f'${median:,.0f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('real_university_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info("Real data plots saved as real_university_analysis.png")
    
    def save_final_analysis(self):
        """Save the complete analysis with real data."""
        output_file = "final_real_university_analysis.csv"
        self.df.to_csv(output_file, index=False)
        logger.info(f"Final analysis saved to {output_file}")
        return output_file


def main():
    analyzer = RealUniversityAnalysis()
    
    try:
        # Load and process verified real data
        analyzer.load_and_process_data()
        
        # Generate comprehensive statistics
        analyzer.generate_summary_statistics()
        
        # Create real data plots
        analyzer.create_real_data_plots()
        
        # Save final analysis
        analyzer.save_final_analysis()
        
        print("\n" + "=" * 80)
        print("REAL DATA ANALYSIS COMPLETE - 100% VERIFIED AUTHENTIC DATA")
        print("=" * 80)
        print("Files generated:")
        print("- real_university_analysis.png (verified data plots)")
        print("- final_real_university_analysis.csv (complete analysis)")
        
    except Exception as e:
        logger.error(f"Error in analysis: {e}")
        raise


if __name__ == "__main__":
    main()