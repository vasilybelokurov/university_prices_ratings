#!/usr/bin/env python3
"""
Get bulk US university data using College Scorecard API.
Use the API key properly to get hundreds of US universities with real tuition data.
"""

import requests
import pandas as pd
import time
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollegeScorecardCollector:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
        self.session = requests.Session()
        
    def get_bulk_university_data(self, per_page: int = 100, max_pages: int = 50) -> pd.DataFrame:
        """Get bulk university data from College Scorecard API."""
        
        logger.info("Collecting bulk US university data from College Scorecard...")
        
        all_universities = []
        page = 0
        
        # Parameters for getting quality universities
        base_params = {
            'api_key': self.api_key,
            'per_page': per_page,
            'fields': ','.join([
                'id', 'school.name', 'school.state', 'school.city',
                'school.school_url', 'school.carnegie_size_setting',
                'latest.cost.tuition.in_state', 'latest.cost.tuition.out_of_state',
                'latest.cost.attendance.academic_year',
                'latest.student.size', 'latest.academics.program_available.assoc',
                'latest.academics.program_available.bachelors',
                'latest.academics.program_available.graduate',
                'school.degrees_awarded.predominant',
                'school.operating'
            ]),
            # Filter for quality institutions
            'school.degrees_awarded.predominant': '3,4',  # Bachelor's (3) and Graduate (4)
            'school.operating': '1',  # Currently operating
            'latest.student.size__range': '1000..',  # At least 1000 students
        }
        
        while page < max_pages:
            logger.info(f"Fetching page {page + 1}/{max_pages}...")
            
            params = base_params.copy()
            params['page'] = page
            
            try:
                response = self.session.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    logger.info(f"No more results on page {page + 1}, stopping")
                    break
                
                # Process and filter results
                valid_universities = []
                for school in results:
                    # Must have tuition data
                    if (school.get('latest.cost.tuition.out_of_state') or 
                        school.get('latest.cost.tuition.in_state')) and school.get('school.name'):
                        
                        # Prefer out-of-state tuition for international comparison
                        tuition = (school.get('latest.cost.tuition.out_of_state') or 
                                 school.get('latest.cost.tuition.in_state'))
                        
                        valid_universities.append({
                            'scorecard_id': school.get('id'),
                            'institution': school.get('school.name'),
                            'state': school.get('school.state'),
                            'city': school.get('school.city'),
                            'url': school.get('school.school_url'),
                            'carnegie_setting': school.get('school.carnegie_size_setting'),
                            'tuition_in_state_usd': school.get('latest.cost.tuition.in_state'),
                            'tuition_out_state_usd': school.get('latest.cost.tuition.out_of_state'),
                            'total_cost_usd': school.get('latest.cost.attendance.academic_year'),
                            'student_size': school.get('latest.student.size'),
                            'price_usd': tuition,
                            'degrees_predominant': school.get('school.degrees_awarded.predominant'),
                            'has_bachelors': school.get('latest.academics.program_available.bachelors'),
                            'has_graduate': school.get('latest.academics.program_available.graduate')
                        })
                
                all_universities.extend(valid_universities)
                logger.info(f"  ✅ Got {len(valid_universities)} valid universities from page {page + 1}")
                logger.info(f"  📊 Total collected so far: {len(all_universities)}")
                
                # Rate limiting
                time.sleep(0.5)
                page += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Error fetching page {page + 1}: {e}")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error on page {page + 1}: {e}")
                break
        
        # Convert to DataFrame
        if all_universities:
            df = pd.DataFrame(all_universities)
            df['country'] = 'United States'
            
            logger.info(f"🎉 Successfully collected {len(df)} US universities")
            return df
        else:
            logger.error("❌ No universities collected")
            return pd.DataFrame()
    
    def analyze_collected_data(self, df: pd.DataFrame):
        """Analyze the collected university data."""
        if df.empty:
            logger.error("No data to analyze")
            return
        
        logger.info("\n" + "="*60)
        logger.info("COLLEGE SCORECARD DATA ANALYSIS")
        logger.info("="*60)
        
        # Basic stats
        logger.info(f"Total universities collected: {len(df)}")
        
        # State distribution
        state_counts = df['state'].value_counts()
        logger.info(f"\nTop 10 states by university count:")
        for state, count in state_counts.head(10).items():
            logger.info(f"  {state}: {count} universities")
        
        # Price statistics
        price_stats = df['price_usd'].describe()
        logger.info(f"\nTuition price statistics (USD):")
        logger.info(f"  Min: ${price_stats['min']:,.0f}")
        logger.info(f"  Median: ${price_stats['50%']:,.0f}")
        logger.info(f"  Max: ${price_stats['max']:,.0f}")
        logger.info(f"  Mean: ${price_stats['mean']:,.0f}")
        
        # Size statistics  
        size_stats = df['student_size'].describe()
        logger.info(f"\nStudent size statistics:")
        logger.info(f"  Min: {size_stats['min']:,.0f} students")
        logger.info(f"  Median: {size_stats['50%']:,.0f} students") 
        logger.info(f"  Max: {size_stats['max']:,.0f} students")
        
        # Show sample universities
        logger.info(f"\nSample universities (sorted by price):")
        sample = df.nsmallest(10, 'price_usd')[['institution', 'state', 'price_usd', 'student_size']]
        for _, row in sample.iterrows():
            logger.info(f"  {row['institution'][:40]:<40} | {row['state']} | ${row['price_usd']:6,.0f} | {row['student_size']:5,.0f} students")
    
    def save_data(self, df: pd.DataFrame, filename: str = "bulk_scorecard_data.csv"):
        """Save the collected data."""
        if df.empty:
            logger.error("Cannot save empty DataFrame")
            return None
        
        df.to_csv(filename, index=False)
        logger.info(f"✅ Data saved to: {filename}")
        return filename


def main():
    # Use your provided API key
    api_key = "jHFyoMT1IT4cT79aVDEUGmRdbnX6gxa5CCrLO4k9"
    
    print("="*80)
    print("COLLECTING BULK US UNIVERSITY DATA FROM COLLEGE SCORECARD")
    print("="*80)
    
    collector = CollegeScorecardCollector(api_key)
    
    # Collect data (aim for 200-500 universities)
    df = collector.get_bulk_university_data(per_page=100, max_pages=20)
    
    if not df.empty:
        # Analyze the data
        collector.analyze_collected_data(df)
        
        # Save the data
        filename = collector.save_data(df)
        
        print("\n" + "="*80)
        print("SUCCESS: BULK US DATA COLLECTED")
        print("="*80)
        print(f"Universities collected: {len(df)}")
        print(f"Data saved to: {filename}")
        print("Ready for next step: UK data collection and ranking matching")
        
        return df
    else:
        print("❌ ERROR: No data collected")
        return None


if __name__ == "__main__":
    data = main()