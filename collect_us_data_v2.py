#!/usr/bin/env python3
"""
Collect US university tuition and ranking data.
Uses downloadable datasets and manual ranking data for demonstration.
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_us_data() -> pd.DataFrame:
    """Create sample US university data for demonstration."""
    logger.info("Creating sample US university dataset...")
    
    # Sample data based on real universities and approximate costs (2024)
    sample_data = [
        # Ivy League and top private
        {'name': 'Harvard University', 'state': 'MA', 'tuition': 59076, 'ranking': 2, 'type': 'private'},
        {'name': 'Stanford University', 'state': 'CA', 'tuition': 61731, 'ranking': 3, 'type': 'private'},
        {'name': 'Massachusetts Institute of Technology', 'state': 'MA', 'tuition': 59750, 'ranking': 2, 'type': 'private'},
        {'name': 'Yale University', 'state': 'CT', 'tuition': 64700, 'ranking': 5, 'type': 'private'},
        {'name': 'Princeton University', 'state': 'NJ', 'tuition': 59710, 'ranking': 1, 'type': 'private'},
        {'name': 'University of Pennsylvania', 'state': 'PA', 'tuition': 63452, 'ranking': 6, 'type': 'private'},
        {'name': 'Columbia University', 'state': 'NY', 'tuition': 68400, 'ranking': 12, 'type': 'private'},
        {'name': 'Dartmouth College', 'state': 'NH', 'tuition': 64710, 'ranking': 12, 'type': 'private'},
        {'name': 'Brown University', 'state': 'RI', 'tuition': 65146, 'ranking': 9, 'type': 'private'},
        {'name': 'Cornell University', 'state': 'NY', 'tuition': 63200, 'ranking': 12, 'type': 'private'},
        
        # Top public universities (in-state tuition)
        {'name': 'University of California Berkeley', 'state': 'CA', 'tuition': 14312, 'ranking': 15, 'type': 'public'},
        {'name': 'University of Michigan Ann Arbor', 'state': 'MI', 'tuition': 17786, 'ranking': 21, 'type': 'public'},
        {'name': 'University of California Los Angeles', 'state': 'CA', 'tuition': 13804, 'ranking': 15, 'type': 'public'},
        {'name': 'University of Virginia', 'state': 'VA', 'tuition': 19698, 'ranking': 24, 'type': 'public'},
        {'name': 'Georgia Institute of Technology', 'state': 'GA', 'tuition': 12682, 'ranking': 33, 'type': 'public'},
        {'name': 'University of North Carolina Chapel Hill', 'state': 'NC', 'tuition': 7019, 'ranking': 22, 'type': 'public'},
        {'name': 'University of California San Diego', 'state': 'CA', 'tuition': 14648, 'ranking': 28, 'type': 'public'},
        {'name': 'University of Wisconsin Madison', 'state': 'WI', 'tuition': 10796, 'ranking': 35, 'type': 'public'},
        {'name': 'University of Illinois Urbana-Champaign', 'state': 'IL', 'tuition': 16866, 'ranking': 35, 'type': 'public'},
        {'name': 'University of Washington', 'state': 'WA', 'tuition': 12092, 'ranking': 40, 'type': 'public'},
        
        # Mid-tier private colleges
        {'name': 'New York University', 'state': 'NY', 'tuition': 58168, 'ranking': 28, 'type': 'private'},
        {'name': 'Boston University', 'state': 'MA', 'tuition': 62360, 'ranking': 41, 'type': 'private'},
        {'name': 'Northeastern University', 'state': 'MA', 'tuition': 59100, 'ranking': 44, 'type': 'private'},
        {'name': 'University of Southern California', 'state': 'CA', 'tuition': 64726, 'ranking': 28, 'type': 'private'},
        {'name': 'Georgetown University', 'state': 'DC', 'tuition': 62052, 'ranking': 22, 'type': 'private'},
        
        # Additional public universities
        {'name': 'Ohio State University', 'state': 'OH', 'tuition': 12485, 'ranking': 43, 'type': 'public'},
        {'name': 'University of Florida', 'state': 'FL', 'tuition': 6381, 'ranking': 28, 'type': 'public'},
        {'name': 'University of Texas Austin', 'state': 'TX', 'tuition': 11678, 'ranking': 32, 'type': 'public'},
        {'name': 'Pennsylvania State University', 'state': 'PA', 'tuition': 18898, 'ranking': 60, 'type': 'public'},
        {'name': 'University of California Davis', 'state': 'CA', 'tuition': 14495, 'ranking': 28, 'type': 'public'},
        
        # Lower-cost public options
        {'name': 'SUNY Stony Brook', 'state': 'NY', 'tuition': 7070, 'ranking': 58, 'type': 'public'},
        {'name': 'University of Georgia', 'state': 'GA', 'tuition': 11830, 'ranking': 47, 'type': 'public'},
        {'name': 'Rutgers University', 'state': 'NJ', 'tuition': 15804, 'ranking': 55, 'type': 'public'},
        {'name': 'University of Alabama', 'state': 'AL', 'tuition': 11100, 'ranking': 103, 'type': 'public'},
        {'name': 'Arizona State University', 'state': 'AZ', 'tuition': 11618, 'ranking': 105, 'type': 'public'},
        
        # More affordable private colleges
        {'name': 'Brigham Young University', 'state': 'UT', 'tuition': 6304, 'ranking': 89, 'type': 'private'},
        {'name': 'Berea College', 'state': 'KY', 'tuition': 0, 'ranking': 75, 'type': 'private'},
        {'name': 'Cooper Union', 'state': 'NY', 'tuition': 46700, 'ranking': 65, 'type': 'private'},
        {'name': 'Rice University', 'state': 'TX', 'tuition': 54960, 'ranking': 15, 'type': 'private'},
        {'name': 'Vanderbilt University', 'state': 'TN', 'tuition': 60348, 'ranking': 13, 'type': 'private'},
        {'name': 'Washington University in St. Louis', 'state': 'MO', 'tuition': 61750, 'ranking': 24, 'type': 'private'},
    ]
    
    df = pd.DataFrame(sample_data)
    logger.info(f"Created sample dataset with {len(df)} universities")
    
    return df

def analyze_us_data(df: pd.DataFrame) -> Dict:
    """Analyze the US university data."""
    logger.info("Analyzing US university data...")
    
    # Basic statistics
    stats = {
        'total_universities': len(df),
        'private_count': len(df[df['type'] == 'private']),
        'public_count': len(df[df['type'] == 'public']),
        'tuition_stats': {
            'min': df['tuition'].min(),
            'max': df['tuition'].max(),
            'mean': df['tuition'].mean(),
            'median': df['tuition'].median()
        },
        'ranking_stats': {
            'best_rank': df['ranking'].min(),
            'worst_rank': df['ranking'].max(),
            'mean_rank': df['ranking'].mean()
        }
    }
    
    # Correlation analysis
    correlation = df['tuition'].corr(df['ranking'])
    stats['price_rank_correlation'] = correlation
    
    return stats

def main():
    """Main execution function."""
    logger.info("Starting US university data collection and analysis...")
    
    # Create sample data
    df = create_sample_us_data()
    
    # Save to CSV
    output_file = "us_universities_sample.csv"
    df.to_csv(output_file, index=False)
    logger.info(f"Data saved to {output_file}")
    
    # Analyze data
    stats = analyze_us_data(df)
    
    # Display results
    print("\n=== US Universities Sample Data Analysis ===")
    print(f"Total universities: {stats['total_universities']}")
    print(f"Private universities: {stats['private_count']}")
    print(f"Public universities: {stats['public_count']}")
    print(f"\nTuition Statistics:")
    print(f"  Range: ${stats['tuition_stats']['min']:,.0f} - ${stats['tuition_stats']['max']:,.0f}")
    print(f"  Mean: ${stats['tuition_stats']['mean']:,.0f}")
    print(f"  Median: ${stats['tuition_stats']['median']:,.0f}")
    print(f"\nRanking Statistics:")
    print(f"  Best rank: {stats['ranking_stats']['best_rank']}")
    print(f"  Worst rank: {stats['ranking_stats']['worst_rank']}")
    print(f"  Mean rank: {stats['ranking_stats']['mean_rank']:.1f}")
    print(f"\nPrice-Ranking Correlation: {stats['price_rank_correlation']:.3f}")
    
    # Show sample data
    print(f"\nSample of data:")
    print(df[['name', 'state', 'tuition', 'ranking', 'type']].head(10).to_string(index=False))
    
    return df

if __name__ == "__main__":
    main()