#!/usr/bin/env python3
"""
Investigate College Scorecard API for built-in quality/ranking metrics.
Check what quality indicators are available that could serve as university rankings.
"""

import requests
import pandas as pd
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scorecard_quality_metrics():
    """Test comprehensive quality metrics available in College Scorecard API."""
    
    api_key = "jHFyoMT1IT4cT79aVDEUGmRdbnX6gxa5CCrLO4k9"
    base_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
    
    # Comprehensive quality metrics to test
    quality_fields = [
        # Academic Quality
        'latest.admissions.sat_scores.average.overall',
        'latest.admissions.act_scores.midpoint.cumulative',
        'latest.admissions.admission_rate.overall',
        'latest.completion.completion_rate_4yr_100nt',
        'latest.completion.completion_rate_less_than_4yr_100nt',
        
        # Student Outcomes
        'latest.earnings.10_yrs_after_entry.median',
        'latest.repayment.1_yr_repayment.overall',
        'latest.student.retention_rate.four_year.full_time',
        
        # Academic Programs
        'latest.academics.program_percentage.bachelors',
        'latest.academics.program_percentage.graduate',
        
        # Student Demographics (as quality proxy)
        'latest.student.demographics.race_ethnicity.white',
        'latest.student.part_time_share',
        
        # Financial Health
        'latest.cost.net_price.public.by_income_level.0-30000',
        'latest.aid.pell_grant_rate',
        
        # Basic Info
        'school.name',
        'school.state',
        'latest.student.size'
    ]
    
    logger.info("Testing College Scorecard quality metrics...")
    logger.info(f"Testing {len(quality_fields)} potential quality indicators")
    
    params = {
        'api_key': api_key,
        'per_page': 10,
        'fields': ','.join(quality_fields),
        'school.operating': '1',
        'latest.student.size__range': '5000..',  # Large universities only
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        logger.info(f"✅ Got {len(results)} universities for testing")
        
        if results:
            # Analyze which metrics are available
            df = pd.json_normalize(results)
            logger.info(f"Available columns: {len(df.columns)}")
            
            # Check data availability for each metric
            logger.info("\nQUALITY METRICS AVAILABILITY:")
            logger.info("-" * 50)
            
            quality_metrics = {}
            
            for col in df.columns:
                if col not in ['school.name', 'school.state']:
                    non_null_count = df[col].notna().sum()
                    availability = non_null_count / len(df) * 100
                    
                    if availability > 50:  # Focus on metrics with >50% availability
                        quality_metrics[col] = {
                            'availability_pct': availability,
                            'sample_values': df[col].dropna().head(3).tolist(),
                            'data_type': str(df[col].dtype)
                        }
                        
                        logger.info(f"  ✅ {col}: {availability:.1f}% available")
                        logger.info(f"     Sample values: {quality_metrics[col]['sample_values']}")
                    else:
                        logger.info(f"  ❌ {col}: {availability:.1f}% available (low)")
            
            # Show sample universities with their quality metrics
            logger.info(f"\nSAMPLE UNIVERSITIES WITH QUALITY METRICS:")
            logger.info("-" * 60)
            
            for _, row in df.head(5).iterrows():
                name = row.get('school.name', 'Unknown')
                state = row.get('school.state', 'Unknown')
                sat = row.get('latest.admissions.sat_scores.average.overall', 'N/A')
                completion = row.get('latest.completion.completion_rate_4yr_100nt', 'N/A')
                earnings = row.get('latest.earnings.10_yrs_after_entry.median', 'N/A')
                
                logger.info(f"{name} ({state})")
                logger.info(f"  SAT: {sat}, 4yr Completion: {completion}, Earnings: ${earnings}")
            
            return quality_metrics
        else:
            logger.error("No results returned from API")
            return {}
            
    except Exception as e:
        logger.error(f"Error testing quality metrics: {e}")
        return {}

def create_quality_ranking_system(quality_metrics):
    """Propose a quality ranking system based on available metrics."""
    
    logger.info("\nPROPOSED QUALITY RANKING SYSTEM:")
    logger.info("=" * 50)
    
    # Define quality components with weights
    ranking_components = {
        'Academic Selectivity (30%)': [
            'latest.admissions.sat_scores.average.overall',  # Higher is better
            'latest.admissions.act_scores.midpoint.cumulative',  # Higher is better
            'latest.admissions.admission_rate.overall'  # Lower is better (more selective)
        ],
        'Student Outcomes (40%)': [
            'latest.completion.completion_rate_4yr_100nt',  # Higher is better
            'latest.earnings.10_yrs_after_entry.median',  # Higher is better
            'latest.student.retention_rate.four_year.full_time'  # Higher is better
        ],
        'Student Quality (20%)': [
            'latest.student.part_time_share',  # Lower is better (more full-time)
            'latest.aid.pell_grant_rate'  # Lower could indicate higher income students
        ],
        'Financial Health (10%)': [
            'latest.repayment.1_yr_repayment.overall'  # Higher is better
        ]
    }
    
    for category, metrics in ranking_components.items():
        logger.info(f"\n{category}:")
        for metric in metrics:
            if metric in quality_metrics:
                availability = quality_metrics[metric]['availability_pct']
                logger.info(f"  ✅ {metric} ({availability:.1f}% available)")
            else:
                logger.info(f"  ❌ {metric} (not available)")
    
    # Calculate how many universities we could rank
    available_metrics = [m for category in ranking_components.values() 
                        for m in category if m in quality_metrics]
    
    logger.info(f"\nSUMMARY:")
    logger.info(f"Available quality metrics: {len(available_metrics)}")
    logger.info(f"This would create a comprehensive quality ranking system!")
    
    return ranking_components, available_metrics

def main():
    print("=" * 80)
    print("INVESTIGATING COLLEGE SCORECARD QUALITY METRICS")
    print("=" * 80)
    
    # Test available quality metrics
    quality_metrics = test_scorecard_quality_metrics()
    
    if quality_metrics:
        # Propose ranking system
        ranking_components, available_metrics = create_quality_ranking_system(quality_metrics)
        
        print("\n" + "=" * 80)
        print("CONCLUSION: COLLEGE SCORECARD HAS QUALITY METRICS!")
        print("=" * 80)
        print(f"✅ Found {len(available_metrics)} usable quality indicators")
        print("✅ Can create comprehensive university quality rankings")
        print("✅ No external ranking APIs needed!")
        print("\nNext step: Implement quality ranking system for 1,213 universities")
        
        return quality_metrics
    else:
        print("❌ Could not access quality metrics")
        return None

if __name__ == "__main__":
    metrics = main()