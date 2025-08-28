#!/usr/bin/env python3
"""
Collect US university tuition and ranking data.
Uses College Scorecard API for tuition and scrapes Washington Monthly rankings.
"""

import requests
import pandas as pd
import numpy as np
import time
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class USUniversityDataCollector:
    def __init__(self):
        self.scorecard_base_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
        self.data = {}
        
    def fetch_scorecard_data(self) -> pd.DataFrame:
        """Fetch university data from College Scorecard API."""
        logger.info("Fetching data from College Scorecard API...")
        
        # Parameters for undergraduate 4-year degree-granting institutions
        params = {
            'school.degrees_awarded.predominant': '3',  # Bachelor's degree
            'school.operating': '1',  # Currently operating
            'school.main_campus': '1',  # Main campus only
            'fields': 'id,school.name,school.state,school.city,latest.cost.tuition.in_state,latest.cost.tuition.out_of_state,latest.cost.attendance.academic_year,latest.admissions.sat_scores.average.overall,latest.completion.completion_rate_4yr_150nt,latest.student.size',
            '_per_page': '5000'
        }
        
        try:
            response = requests.get(self.scorecard_base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            universities = []
            for school in data.get('results', []):
                if school.get('latest.cost.tuition.in_state') is not None:
                    universities.append({
                        'name': school.get('school.name'),
                        'state': school.get('school.state'),
                        'city': school.get('school.city'),
                        'tuition_in_state': school.get('latest.cost.tuition.in_state'),
                        'tuition_out_state': school.get('latest.cost.tuition.out_of_state'),
                        'total_cost': school.get('latest.cost.attendance.academic_year'),
                        'sat_average': school.get('latest.admissions.sat_scores.average.overall'),
                        'completion_rate': school.get('latest.completion.completion_rate_4yr_150nt'),
                        'student_size': school.get('latest.student.size'),
                        'scorecard_id': school.get('id')
                    })
            
            df = pd.DataFrame(universities)
            logger.info(f"Collected {len(df)} universities from College Scorecard")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching College Scorecard data: {e}")
            return pd.DataFrame()

    def fetch_forbes_rankings(self) -> pd.DataFrame:
        """Scrape Forbes America's Top Colleges rankings."""
        logger.info("Attempting to fetch Forbes rankings...")
        
        # Note: This is a placeholder - Forbes may have anti-scraping measures
        # In practice, you might need to manually download their rankings CSV
        forbes_data = []
        
        # Mock data for demonstration - replace with actual scraping or manual data
        mock_forbes = [
            {'name': 'Harvard University', 'forbes_rank': 1},
            {'name': 'Stanford University', 'forbes_rank': 2},
            {'name': 'Yale University', 'forbes_rank': 3},
            {'name': 'Princeton University', 'forbes_rank': 4},
            {'name': 'Massachusetts Institute of Technology', 'forbes_rank': 5},
        ]
        
        logger.info(f"Using mock Forbes rankings data ({len(mock_forbes)} entries)")
        return pd.DataFrame(mock_forbes)

    def fetch_money_rankings(self) -> pd.DataFrame:
        """Fetch Money Magazine Best Colleges rankings."""
        logger.info("Using mock Money Magazine rankings...")
        
        # Mock data - in practice, scrape or download from Money's website
        mock_money = [
            {'name': 'Princeton University', 'money_rank': 1},
            {'name': 'Massachusetts Institute of Technology', 'money_rank': 2},
            {'name': 'Yale University', 'money_rank': 3},
            {'name': 'Harvard University', 'money_rank': 4},
            {'name': 'Stanford University', 'money_rank': 5},
        ]
        
        return pd.DataFrame(mock_money)

    def normalize_university_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize university names for matching."""
        df['name_normalized'] = df['name'].str.strip().str.lower()
        df['name_normalized'] = df['name_normalized'].str.replace(r'\s+', ' ', regex=True)
        return df

    def merge_rankings(self, scorecard_df: pd.DataFrame, 
                      forbes_df: pd.DataFrame, 
                      money_df: pd.DataFrame) -> pd.DataFrame:
        """Merge scorecard data with ranking data."""
        logger.info("Merging ranking data with scorecard data...")
        
        # Normalize names in all dataframes
        scorecard_df = self.normalize_university_names(scorecard_df)
        forbes_df = self.normalize_university_names(forbes_df)
        money_df = self.normalize_university_names(money_df)
        
        # Merge on normalized names
        merged = scorecard_df.merge(
            forbes_df[['name_normalized', 'forbes_rank']], 
            on='name_normalized', 
            how='left'
        )
        
        merged = merged.merge(
            money_df[['name_normalized', 'money_rank']], 
            on='name_normalized', 
            how='left'
        )
        
        # Create composite ranking (average of available rankings)
        ranking_cols = ['forbes_rank', 'money_rank']
        merged['composite_rank'] = merged[ranking_cols].mean(axis=1, skipna=True)
        
        # Drop normalized name column
        merged = merged.drop('name_normalized', axis=1)
        
        logger.info(f"Final dataset has {len(merged)} universities with rankings for {merged['composite_rank'].notna().sum()}")
        return merged

    def collect_all_data(self) -> pd.DataFrame:
        """Main method to collect all US university data."""
        logger.info("Starting US university data collection...")
        
        # Fetch all data sources
        scorecard_df = self.fetch_scorecard_data()
        if scorecard_df.empty:
            logger.error("Failed to fetch scorecard data")
            return pd.DataFrame()
            
        forbes_df = self.fetch_forbes_rankings()
        money_df = self.fetch_money_rankings()
        
        # Merge all data
        final_df = self.merge_rankings(scorecard_df, forbes_df, money_df)
        
        # Filter for universities with both cost and ranking data
        final_df = final_df.dropna(subset=['tuition_in_state', 'composite_rank'])
        
        logger.info(f"Final US dataset: {len(final_df)} universities")
        return final_df

def main():
    """Test the data collection."""
    collector = USUniversityDataCollector()
    df = collector.collect_all_data()
    
    if not df.empty:
        # Save to CSV
        output_file = "us_universities_data.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Data saved to {output_file}")
        
        # Show summary statistics
        print("\n=== US Universities Data Summary ===")
        print(f"Total universities: {len(df)}")
        print(f"In-state tuition range: ${df['tuition_in_state'].min():,.0f} - ${df['tuition_in_state'].max():,.0f}")
        print(f"Out-of-state tuition range: ${df['tuition_out_state'].min():,.0f} - ${df['tuition_out_state'].max():,.0f}")
        print(f"Universities with rankings: {df['composite_rank'].notna().sum()}")
        
        # Show first few rows
        print("\nFirst 5 universities:")
        print(df[['name', 'state', 'tuition_in_state', 'composite_rank']].head())
    
    return df

if __name__ == "__main__":
    main()