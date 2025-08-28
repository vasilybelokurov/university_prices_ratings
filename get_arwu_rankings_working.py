#!/usr/bin/env python3
"""
Get ARWU 2023 rankings using the working JSON API that o3 confirmed works.
This is the undocumented but public API that powers the ARWU website.
"""

import requests
import pandas as pd
import json
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_arwu_us_rankings_2023() -> pd.DataFrame:
    """Get ARWU 2023 rankings for US universities using working JSON API."""
    
    # o3's confirmed working endpoint
    url = ("https://www.shanghairanking.com/api/pub/v1/rank?"
           "rankingType=arwu&year=2023&page=1&pageSize=1000&country=United%20States")
    
    logger.info("Fetching ARWU 2023 US rankings from working JSON API...")
    logger.info(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Content type: {response.headers.get('Content-Type', 'Unknown')}")
        
        # Parse JSON
        data = response.json()
        logger.info(f"JSON keys: {list(data.keys())}")
        
        if 'data' in data:
            rankings_data = data['data']
            logger.info(f"Found {len(rankings_data)} US universities in ARWU 2023")
            
            # Convert to DataFrame
            df = pd.json_normalize(rankings_data)
            logger.info(f"DataFrame columns: {list(df.columns)}")
            
            # Standardize column names
            column_mapping = {
                'univName': 'university',
                'rankingDisplayNumber': 'arwu_rank_2023',
                'country': 'country',
                'totalScore': 'arwu_score'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Clean and validate
            if 'university' in df.columns and 'arwu_rank_2023' in df.columns:
                df = df[['university', 'arwu_rank_2023', 'arwu_score']].copy()
                df['country'] = 'United States'
                
                # Show sample
                logger.info("Sample ARWU 2023 US universities:")
                for _, row in df.head(10).iterrows():
                    rank = row['arwu_rank_2023']
                    uni = row['university']
                    score = row.get('arwu_score', 'N/A')
                    logger.info(f"  {rank}. {uni} (Score: {score})")
                
                return df
            else:
                logger.error("Required columns not found after renaming")
                return pd.DataFrame()
        else:
            logger.error("'data' key not found in JSON response")
            return pd.DataFrame()
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode failed: {e}")
        logger.info(f"Response content: {response.text[:500]}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return pd.DataFrame()

def get_arwu_global_rankings_2023(max_results: int = 1000) -> pd.DataFrame:
    """Get ARWU 2023 global rankings (all countries)."""
    
    url = ("https://www.shanghairanking.com/api/pub/v1/rank?"
           f"rankingType=arwu&year=2023&page=1&pageSize={max_results}")
    
    logger.info(f"Fetching ARWU 2023 global rankings (max {max_results})...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if 'data' in data:
            rankings_data = data['data']
            logger.info(f"Found {len(rankings_data)} universities globally in ARWU 2023")
            
            df = pd.json_normalize(rankings_data)
            
            # Standardize column names
            column_mapping = {
                'univName': 'university',
                'rankingDisplayNumber': 'arwu_rank_2023',
                'country': 'country',
                'totalScore': 'arwu_score'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Filter for US and UK
            if 'country' in df.columns:
                us_uk_df = df[df['country'].isin(['United States', 'United Kingdom'])].copy()
                logger.info(f"US+UK universities: {len(us_uk_df)}")
                
                us_count = len(us_uk_df[us_uk_df['country'] == 'United States'])
                uk_count = len(us_uk_df[us_uk_df['country'] == 'United Kingdom'])
                logger.info(f"  US: {us_count}, UK: {uk_count}")
                
                return us_uk_df
            else:
                return df
        else:
            logger.error("'data' key not found in global rankings")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"Error getting global rankings: {e}")
        return pd.DataFrame()

def test_arwu_api():
    """Test the ARWU API to verify it works."""
    print("="*60)
    print("TESTING ARWU JSON API")
    print("="*60)
    
    # Test US rankings
    us_df = get_arwu_us_rankings_2023()
    
    if not us_df.empty:
        print(f"✅ SUCCESS: Got {len(us_df)} US universities")
        
        # Test global rankings
        global_df = get_arwu_global_rankings_2023()
        
        if not global_df.empty:
            print(f"✅ SUCCESS: Got {len(global_df)} US+UK universities from global data")
            return global_df
        else:
            print("⚠️ Global rankings failed, using US-only data")
            return us_df
    else:
        print("❌ FAILED: Could not get ARWU rankings")
        return pd.DataFrame()

def save_arwu_data(df: pd.DataFrame, filename: str = "arwu_2023_working.csv"):
    """Save the ARWU ranking data."""
    if df.empty:
        logger.error("Cannot save empty DataFrame")
        return None
    
    df.to_csv(filename, index=False)
    logger.info(f"ARWU data saved to: {filename}")
    return filename

def main():
    print("="*80)
    print("GETTING ARWU 2023 RANKINGS - WORKING METHOD")
    print("="*80)
    
    # Test and get rankings
    df = test_arwu_api()
    
    if not df.empty:
        # Save the data
        filename = save_arwu_data(df)
        
        print("\n" + "="*80)
        print("SUCCESS: ARWU RANKINGS COLLECTED")
        print("="*80)
        print(f"Universities with rankings: {len(df)}")
        if 'country' in df.columns:
            us_count = len(df[df['country'] == 'United States'])
            uk_count = len(df[df['country'] == 'United Kingdom'])
            print(f"US universities: {us_count}")
            print(f"UK universities: {uk_count}")
        print(f"Data saved to: {filename}")
        print("Ready for matching with College Scorecard data!")
        
        return df
    else:
        print("ERROR: Failed to get ARWU rankings")
        return None

if __name__ == "__main__":
    rankings_data = main()