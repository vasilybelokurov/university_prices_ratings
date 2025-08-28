#!/usr/bin/env python3
"""
Collect UK university tuition and ranking data.
Uses sample data based on Complete University Guide and official fee information.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_uk_data() -> pd.DataFrame:
    """Create sample UK university data for demonstration."""
    logger.info("Creating sample UK university dataset...")
    
    # Sample data based on real UK universities (2024 data)
    # Tuition fees: Home = £9,250, International varies significantly
    sample_data = [
        # Russell Group and top universities
        {'name': 'University of Cambridge', 'city': 'Cambridge', 'home_tuition': 9250, 'intl_tuition': 27048, 'cug_rank': 1, 'guardian_rank': 1},
        {'name': 'University of Oxford', 'city': 'Oxford', 'home_tuition': 9250, 'intl_tuition': 28950, 'cug_rank': 2, 'guardian_rank': 2},
        {'name': 'London School of Economics', 'city': 'London', 'home_tuition': 9250, 'intl_tuition': 25608, 'cug_rank': 3, 'guardian_rank': 4},
        {'name': 'Imperial College London', 'city': 'London', 'home_tuition': 9250, 'intl_tuition': 37900, 'cug_rank': 4, 'guardian_rank': 5},
        {'name': 'University College London', 'city': 'London', 'home_tuition': 9250, 'intl_tuition': 31200, 'cug_rank': 5, 'guardian_rank': 8},
        {'name': 'University of Edinburgh', 'city': 'Edinburgh', 'home_tuition': 1820, 'intl_tuition': 26500, 'cug_rank': 6, 'guardian_rank': 13},
        {'name': 'Kings College London', 'city': 'London', 'home_tuition': 9250, 'intl_tuition': 31350, 'cug_rank': 7, 'guardian_rank': 35},
        {'name': 'University of Manchester', 'city': 'Manchester', 'home_tuition': 9250, 'intl_tuition': 26000, 'cug_rank': 8, 'guardian_rank': 25},
        {'name': 'University of Warwick', 'city': 'Coventry', 'home_tuition': 9250, 'intl_tuition': 27060, 'cug_rank': 9, 'guardian_rank': 9},
        {'name': 'University of Bristol', 'city': 'Bristol', 'home_tuition': 9250, 'intl_tuition': 27200, 'cug_rank': 10, 'guardian_rank': 15},
        
        # More Russell Group
        {'name': 'University of Glasgow', 'city': 'Glasgow', 'home_tuition': 1820, 'intl_tuition': 24540, 'cug_rank': 11, 'guardian_rank': 18},
        {'name': 'Durham University', 'city': 'Durham', 'home_tuition': 9250, 'intl_tuition': 28500, 'cug_rank': 12, 'guardian_rank': 6},
        {'name': 'University of Sheffield', 'city': 'Sheffield', 'home_tuition': 9250, 'intl_tuition': 23650, 'cug_rank': 13, 'guardian_rank': 26},
        {'name': 'University of Birmingham', 'city': 'Birmingham', 'home_tuition': 9250, 'intl_tuition': 25860, 'cug_rank': 14, 'guardian_rank': 14},
        {'name': 'University of Leeds', 'city': 'Leeds', 'home_tuition': 9250, 'intl_tuition': 24500, 'cug_rank': 15, 'guardian_rank': 19},
        {'name': 'University of Nottingham', 'city': 'Nottingham', 'home_tuition': 9250, 'intl_tuition': 26000, 'cug_rank': 16, 'guardian_rank': 30},
        {'name': 'University of Southampton', 'city': 'Southampton', 'home_tuition': 9250, 'intl_tuition': 24400, 'cug_rank': 17, 'guardian_rank': 20},
        {'name': 'University of York', 'city': 'York', 'home_tuition': 9250, 'intl_tuition': 24450, 'cug_rank': 18, 'guardian_rank': 16},
        {'name': 'Newcastle University', 'city': 'Newcastle', 'home_tuition': 9250, 'intl_tuition': 24000, 'cug_rank': 19, 'guardian_rank': 33},
        {'name': 'University of Liverpool', 'city': 'Liverpool', 'home_tuition': 9250, 'intl_tuition': 23400, 'cug_rank': 20, 'guardian_rank': 42},
        
        # Additional universities
        {'name': 'Lancaster University', 'city': 'Lancaster', 'home_tuition': 9250, 'intl_tuition': 25040, 'cug_rank': 21, 'guardian_rank': 7},
        {'name': 'University of Bath', 'city': 'Bath', 'home_tuition': 9250, 'intl_tuition': 25900, 'cug_rank': 22, 'guardian_rank': 11},
        {'name': 'University of East Anglia', 'city': 'Norwich', 'home_tuition': 9250, 'intl_tuition': 22800, 'cug_rank': 23, 'guardian_rank': 23},
        {'name': 'University of Exeter', 'city': 'Exeter', 'home_tuition': 9250, 'intl_tuition': 27000, 'cug_rank': 24, 'guardian_rank': 12},
        {'name': 'Cardiff University', 'city': 'Cardiff', 'home_tuition': 9000, 'intl_tuition': 24450, 'cug_rank': 25, 'guardian_rank': 34},
        
        # Lower-ranked but well-known
        {'name': 'University of Leicester', 'city': 'Leicester', 'home_tuition': 9250, 'intl_tuition': 21750, 'cug_rank': 26, 'guardian_rank': 41},
        {'name': 'University of Surrey', 'city': 'Guildford', 'home_tuition': 9250, 'intl_tuition': 23800, 'cug_rank': 27, 'guardian_rank': 38},
        {'name': 'University of Strathclyde', 'city': 'Glasgow', 'home_tuition': 1820, 'intl_tuition': 22400, 'cug_rank': 28, 'guardian_rank': 22},
        {'name': 'Queen Mary University', 'city': 'London', 'home_tuition': 9250, 'intl_tuition': 26250, 'cug_rank': 29, 'guardian_rank': 47},
        {'name': 'University of Reading', 'city': 'Reading', 'home_tuition': 9250, 'intl_tuition': 22350, 'cug_rank': 30, 'guardian_rank': 29},
        
        # More affordable or specialized institutions  
        {'name': 'Coventry University', 'city': 'Coventry', 'home_tuition': 9250, 'intl_tuition': 16800, 'cug_rank': 50, 'guardian_rank': 52},
        {'name': 'University of Chester', 'city': 'Chester', 'home_tuition': 9250, 'intl_tuition': 13450, 'cug_rank': 68, 'guardian_rank': 75},
        {'name': 'University of Cumbria', 'city': 'Carlisle', 'home_tuition': 9250, 'intl_tuition': 13575, 'cug_rank': 89, 'guardian_rank': 95},
        {'name': 'Teesside University', 'city': 'Middlesbrough', 'home_tuition': 9250, 'intl_tuition': 15000, 'cug_rank': 95, 'guardian_rank': 89},
        {'name': 'University of Bolton', 'city': 'Bolton', 'home_tuition': 9250, 'intl_tuition': 12950, 'cug_rank': 120, 'guardian_rank': 110},
        
        # Scottish universities (lower home fees)
        {'name': 'University of St Andrews', 'city': 'St Andrews', 'home_tuition': 1820, 'intl_tuition': 30160, 'cug_rank': 3, 'guardian_rank': 3},
        {'name': 'University of Aberdeen', 'city': 'Aberdeen', 'home_tuition': 1820, 'intl_tuition': 24800, 'cug_rank': 31, 'guardian_rank': 48},
        {'name': 'University of Stirling', 'city': 'Stirling', 'home_tuition': 1820, 'intl_tuition': 16400, 'cug_rank': 45, 'guardian_rank': 45},
        {'name': 'Glasgow Caledonian University', 'city': 'Glasgow', 'home_tuition': 1820, 'intl_tuition': 15500, 'cug_rank': 78, 'guardian_rank': 82},
        {'name': 'Robert Gordon University', 'city': 'Aberdeen', 'home_tuition': 1820, 'intl_tuition': 17000, 'cug_rank': 55, 'guardian_rank': 71},
    ]
    
    df = pd.DataFrame(sample_data)
    
    # Create composite ranking (average of CUG and Guardian)
    df['composite_rank'] = df[['cug_rank', 'guardian_rank']].mean(axis=1)
    
    logger.info(f"Created sample dataset with {len(df)} UK universities")
    
    return df

def analyze_uk_data(df: pd.DataFrame) -> Dict:
    """Analyze the UK university data.""" 
    logger.info("Analyzing UK university data...")
    
    # Separate Scottish universities (different fee structure)
    scottish_unis = df[df['home_tuition'] == 1820]
    english_unis = df[df['home_tuition'] >= 9000]
    
    stats = {
        'total_universities': len(df),
        'scottish_count': len(scottish_unis),
        'english_welsh_count': len(english_unis),
        'home_tuition_stats': {
            'min': df['home_tuition'].min(),
            'max': df['home_tuition'].max(), 
            'mean': df['home_tuition'].mean(),
            'median': df['home_tuition'].median()
        },
        'intl_tuition_stats': {
            'min': df['intl_tuition'].min(),
            'max': df['intl_tuition'].max(),
            'mean': df['intl_tuition'].mean(),
            'median': df['intl_tuition'].median()
        },
        'ranking_stats': {
            'best_rank': df['composite_rank'].min(),
            'worst_rank': df['composite_rank'].max(),
            'mean_rank': df['composite_rank'].mean()
        }
    }
    
    # Correlation analysis (using international fees as they vary more)
    correlation = df['intl_tuition'].corr(df['composite_rank'])
    stats['price_rank_correlation'] = correlation
    
    return stats

def main():
    """Main execution function."""
    logger.info("Starting UK university data collection and analysis...")
    
    # Create sample data
    df = create_sample_uk_data()
    
    # Save to CSV
    output_file = "uk_universities_sample.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"Data saved to {output_file}")
    
    # Analyze data
    stats = analyze_uk_data(df)
    
    # Display results
    print("\n=== UK Universities Sample Data Analysis ===")
    print(f"Total universities: {stats['total_universities']}")
    print(f"Scottish universities: {stats['scottish_count']} (£1,820 home fees)")
    print(f"English/Welsh universities: {stats['english_welsh_count']} (£9,000-9,250 home fees)")
    print(f"\nHome Student Tuition:")
    print(f"  Range: £{stats['home_tuition_stats']['min']:,.0f} - £{stats['home_tuition_stats']['max']:,.0f}")
    print(f"  Mean: £{stats['home_tuition_stats']['mean']:,.0f}")
    print(f"  Median: £{stats['home_tuition_stats']['median']:,.0f}")
    print(f"\nInternational Student Tuition:")
    print(f"  Range: £{stats['intl_tuition_stats']['min']:,.0f} - £{stats['intl_tuition_stats']['max']:,.0f}")
    print(f"  Mean: £{stats['intl_tuition_stats']['mean']:,.0f}")
    print(f"  Median: £{stats['intl_tuition_stats']['median']:,.0f}")
    print(f"\nRanking Statistics:")
    print(f"  Best composite rank: {stats['ranking_stats']['best_rank']:.1f}")
    print(f"  Worst composite rank: {stats['ranking_stats']['worst_rank']:.1f}")
    print(f"  Mean composite rank: {stats['ranking_stats']['mean_rank']:.1f}")
    print(f"\nInternational Price-Ranking Correlation: {stats['price_rank_correlation']:.3f}")
    
    # Show sample data
    print(f"\nSample of data:")
    print(df[['name', 'city', 'home_tuition', 'intl_tuition', 'composite_rank']].head(10).to_string(index=False))
    
    return df

if __name__ == "__main__":
    main()