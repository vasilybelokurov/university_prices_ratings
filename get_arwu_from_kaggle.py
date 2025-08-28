#!/usr/bin/env python3
"""
Get complete ARWU 2023 rankings from Kaggle dataset.
Alternative approach when direct API fails.
"""

import pandas as pd
import os
import logging
from pathlib import Path
import zipfile
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_arwu_from_kaggle():
    """Download ARWU data from Kaggle dataset using direct HTTP method."""
    
    print("Attempting to get ARWU 2023 data from Kaggle...")
    print("Note: This requires Kaggle API setup for full access")
    
    # Method 1: Try programmatic download if Kaggle is configured
    try:
        import kaggle
        
        logger.info("Attempting Kaggle API download...")
        
        # Create arwu directory
        os.makedirs('arwu_data', exist_ok=True)
        
        # Download the complete ARWU dataset
        kaggle.api.dataset_download_files(
            'abinashdh/academic-ranking-of-world-universities',  
            path='arwu_data', 
            unzip=True
        )
        
        logger.info("✅ Successfully downloaded ARWU dataset from Kaggle")
        return load_arwu_data('arwu_data')
        
    except Exception as e:
        logger.warning(f"Kaggle API method failed: {e}")
        
    # Method 2: Manual fallback with instructions
    print("\n" + "="*60)
    print("MANUAL DOWNLOAD REQUIRED")
    print("="*60)
    print("The automated Kaggle download failed. Please:")
    print("1. Go to: https://www.kaggle.com/datasets/abinashdh/academic-ranking-of-world-universities")
    print("2. Click 'Download' (may require Kaggle account)")
    print("3. Extract the zip file to './arwu_data/' folder")
    print("4. Re-run this script")
    print("="*60)
    
    # Check if manual download exists
    arwu_dir = Path('arwu_data')
    if arwu_dir.exists():
        return load_arwu_data('arwu_data')
    else:
        return None

def load_arwu_data(data_dir):
    """Load ARWU data from downloaded files."""
    data_path = Path(data_dir)
    
    if not data_path.exists():
        logger.error(f"Data directory {data_dir} not found")
        return None
    
    # Find ARWU CSV files
    csv_files = list(data_path.glob('*.csv'))
    
    if not csv_files:
        logger.error(f"No CSV files found in {data_dir}")
        return None
    
    logger.info(f"Found {len(csv_files)} CSV files:")
    for f in csv_files:
        logger.info(f"  - {f.name}")
    
    # Try to load the data
    all_data = []
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded {csv_file.name}: {len(df)} rows, columns: {list(df.columns)}")
            
            # Add year information if not present
            if 'year' not in df.columns and 'Year' not in df.columns:
                # Try to extract year from filename
                year_from_filename = None
                for year in range(2020, 2025):
                    if str(year) in csv_file.name:
                        year_from_filename = year
                        break
                
                if year_from_filename:
                    df['year'] = year_from_filename
                    logger.info(f"  Added year {year_from_filename} from filename")
            
            all_data.append(df)
            
        except Exception as e:
            logger.error(f"Error loading {csv_file}: {e}")
    
    if all_data:
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True, sort=False)
        logger.info(f"Combined dataset: {len(combined_df)} rows")
        
        # Analyze the data
        analyze_combined_data(combined_df)
        
        return combined_df
    else:
        logger.error("No data successfully loaded")
        return None

def analyze_combined_data(df):
    """Analyze the combined ARWU dataset."""
    logger.info("ARWU DATASET ANALYSIS:")
    logger.info("-" * 40)
    
    # Basic info
    logger.info(f"Total rows: {len(df)}")
    logger.info(f"Columns: {list(df.columns)}")
    
    # Year analysis
    year_cols = [col for col in df.columns if 'year' in col.lower()]
    if year_cols:
        year_col = year_cols[0]
        year_counts = df[year_col].value_counts().sort_index()
        logger.info(f"\nData by year ({year_col}):")
        for year, count in year_counts.items():
            logger.info(f"  {year}: {count} universities")
        
        # Focus on 2023
        if 2023 in year_counts:
            df_2023 = df[df[year_col] == 2023]
            logger.info(f"\n2023 DATA ANALYSIS:")
            logger.info(f"  Universities in 2023: {len(df_2023)}")
            
            # Country analysis for 2023
            country_cols = [col for col in df_2023.columns if 'country' in col.lower()]
            if country_cols:
                country_col = country_cols[0]
                country_counts = df_2023[country_col].value_counts()
                
                us_count = country_counts.get('United States', 0)
                uk_count = country_counts.get('United Kingdom', 0)
                
                logger.info(f"  US universities: {us_count}")
                logger.info(f"  UK universities: {uk_count}")
                logger.info(f"  US + UK total: {us_count + uk_count}")
                
                logger.info(f"\nTop 10 countries in 2023:")
                for country, count in country_counts.head(10).items():
                    logger.info(f"    {country}: {count}")

def extract_2023_data(df):
    """Extract and process 2023 ARWU data."""
    if df is None:
        return None
    
    # Find year column
    year_col = None
    for col in ['year', 'Year', 'YEAR']:
        if col in df.columns:
            year_col = col
            break
    
    if year_col is None:
        logger.warning("No year column found, assuming all data is from recent years")
        df_2023 = df.copy()
    else:
        df_2023 = df[df[year_col] == 2023].copy()
    
    if len(df_2023) == 0:
        logger.error("No 2023 data found")
        return None
    
    # Standardize column names
    column_mapping = {
        'World Rank': 'rank',
        'Institution': 'institution', 
        'Country': 'country',
        'Total Score': 'score'
    }
    
    # Apply mapping
    for old_col, new_col in column_mapping.items():
        if old_col in df_2023.columns:
            df_2023 = df_2023.rename(columns={old_col: new_col})
    
    # Filter for US and UK
    if 'country' in df_2023.columns:
        us_uk_data = df_2023[df_2023['country'].isin(['United States', 'United Kingdom'])].copy()
        logger.info(f"Extracted {len(us_uk_data)} US+UK universities from 2023 data")
        
        # Show sample
        if len(us_uk_data) > 0:
            logger.info("Sample 2023 data:")
            for i, row in us_uk_data.head(10).iterrows():
                rank = row.get('rank', 'N/A')
                institution = row.get('institution', 'N/A')
                country = row.get('country', 'N/A')
                logger.info(f"  {rank}. {institution} ({country})")
        
        return us_uk_data
    else:
        logger.warning("No country column found")
        return df_2023

def main():
    print("=" * 80)
    print("GETTING COMPLETE ARWU 2023 DATA FROM KAGGLE")
    print("=" * 80)
    
    # Download data
    df = download_arwu_from_kaggle()
    
    if df is not None:
        # Extract 2023 data
        arwu_2023 = extract_2023_data(df)
        
        if arwu_2023 is not None and len(arwu_2023) > 0:
            # Save the 2023 data
            output_file = "arwu_2023_complete.csv"
            arwu_2023.to_csv(output_file, index=False)
            
            print("\n" + "=" * 80)
            print("SUCCESS: ARWU 2023 DATA COLLECTED")
            print("=" * 80)
            print(f"Total US+UK universities: {len(arwu_2023)}")
            print(f"Data saved to: {output_file}")
            
            # Country breakdown
            if 'country' in arwu_2023.columns:
                us_count = len(arwu_2023[arwu_2023['country'] == 'United States'])
                uk_count = len(arwu_2023[arwu_2023['country'] == 'United Kingdom'])
                print(f"US universities: {us_count}")
                print(f"UK universities: {uk_count}")
            
            return True
        else:
            print("ERROR: No 2023 data extracted")
            return False
    else:
        print("ERROR: Failed to download ARWU data")
        return False

if __name__ == "__main__":
    success = main()