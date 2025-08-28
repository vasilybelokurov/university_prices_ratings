#!/usr/bin/env python3
"""
Get complete ARWU 2023 rankings using the JSON API method suggested by o3.
Downloads all 1000 universities from official ShanghaiRanking API.
"""

import requests
import pandas as pd
import time
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_complete_arwu_2023():
    """Fetch complete ARWU 2023 rankings using JSON API."""
    BASE_URL = "https://www.shanghairanking.com/rankings/arwu/2023"
    
    all_rows = []
    total_pages = 10  # 10 pages * 100 per page = 1000 universities
    
    logger.info("Fetching complete ARWU 2023 rankings from JSON API...")
    
    for page in range(total_pages):
        logger.info(f"Fetching page {page + 1}/{total_pages} (universities {page * 100 + 1}-{(page + 1) * 100})")
        
        url = f"{BASE_URL}?page={page}&per-page=100"
        
        try:
            # Make request with proper headers
            headers = {
                'User-Agent': 'University Research Tool 1.0 (Academic Use)',
                'Accept': 'application/json',
                'Referer': 'https://www.shanghairanking.com/rankings/arwu/2023'
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            if 'data' in data and isinstance(data['data'], list):
                page_rows = data['data']
                all_rows.extend(page_rows)
                logger.info(f"  ✅ Got {len(page_rows)} universities from page {page + 1}")
            else:
                logger.warning(f"  ⚠️ Unexpected JSON structure on page {page + 1}")
                logger.info(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Be polite to the server
            time.sleep(0.6)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"  ❌ Error fetching page {page + 1}: {e}")
            # Continue with other pages
            continue
        except json.JSONDecodeError as e:
            logger.error(f"  ❌ JSON decode error on page {page + 1}: {e}")
            continue
    
    # Convert to DataFrame
    if all_rows:
        df = pd.json_normalize(all_rows)
        logger.info(f"Successfully collected {len(df)} universities")
        logger.info(f"Columns available: {list(df.columns)}")
        
        # Show sample
        if len(df) > 0:
            logger.info("Sample universities:")
            for i, row in df.head(5).iterrows():
                institution = row.get('Institution', row.get('institution', 'Unknown'))
                rank = row.get('Rank', row.get('rank', 'Unknown'))
                country = row.get('CountryRegion', row.get('country', 'Unknown'))
                logger.info(f"  {rank}. {institution} ({country})")
        
        return df
    else:
        logger.error("No data collected - all pages failed")
        return pd.DataFrame()

def save_arwu_data(df, filename="complete_arwu_2023.csv"):
    """Save ARWU data with proper documentation."""
    if df.empty:
        logger.error("Cannot save empty DataFrame")
        return None
    
    # Save main data
    df.to_csv(filename, index=False)
    logger.info(f"ARWU 2023 data saved to: {filename}")
    
    # Save Excel version for compatibility
    excel_filename = filename.replace('.csv', '.xlsx')
    df.to_excel(excel_filename, index=False)
    logger.info(f"ARWU 2023 data saved to: {excel_filename}")
    
    # Create metadata file
    metadata = {
        'source': 'ShanghaiRanking ARWU 2023',
        'url': 'https://www.shanghairanking.com/rankings/arwu/2023',
        'collection_method': 'JSON API pagination',
        'total_universities': len(df),
        'collection_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'columns': list(df.columns),
        'notes': 'Complete ARWU 2023 rankings collected via undocumented JSON API'
    }
    
    metadata_file = filename.replace('.csv', '_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Metadata saved to: {metadata_file}")
    return filename

def analyze_arwu_data(df):
    """Quick analysis of the collected ARWU data."""
    if df.empty:
        logger.error("No data to analyze")
        return
    
    logger.info("ARWU 2023 DATA ANALYSIS:")
    logger.info("-" * 40)
    
    # Basic stats
    logger.info(f"Total universities: {len(df)}")
    
    # Country breakdown
    country_col = None
    for col in ['CountryRegion', 'country', 'Country']:
        if col in df.columns:
            country_col = col
            break
    
    if country_col:
        country_counts = df[country_col].value_counts()
        logger.info(f"\nTop 10 countries by university count:")
        for country, count in country_counts.head(10).items():
            logger.info(f"  {country}: {count} universities")
        
        # US and UK counts
        us_count = country_counts.get('United States', 0)
        uk_count = country_counts.get('United Kingdom', 0)
        logger.info(f"\nTarget countries:")
        logger.info(f"  United States: {us_count} universities")
        logger.info(f"  United Kingdom: {uk_count} universities")
        logger.info(f"  Combined US+UK: {us_count + uk_count} universities")
    
    # Ranking range
    rank_col = None
    for col in ['Rank', 'rank', 'ranking']:
        if col in df.columns:
            rank_col = col
            break
    
    if rank_col:
        logger.info(f"\nRanking range: {df[rank_col].min()} - {df[rank_col].max()}")

def main():
    print("=" * 80)
    print("COLLECTING COMPLETE ARWU 2023 RANKINGS")  
    print("=" * 80)
    
    # Fetch data
    df = fetch_complete_arwu_2023()
    
    if not df.empty:
        # Analyze data
        analyze_arwu_data(df)
        
        # Save data
        filename = save_arwu_data(df)
        
        if filename:
            print("\n" + "=" * 80)
            print("SUCCESS: COMPLETE ARWU 2023 DATA COLLECTED")
            print("=" * 80)
            print(f"Universities collected: {len(df)}")
            print(f"Main file: {filename}")
            print("Ready for next step: College Scorecard bulk data")
        else:
            print("ERROR: Failed to save data")
    else:
        print("ERROR: No data collected")
        return False
    
    return True

if __name__ == "__main__":
    success = main()