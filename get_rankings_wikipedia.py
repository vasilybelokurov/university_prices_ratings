#!/usr/bin/env python3
"""
Get university rankings from Wikipedia tables - o3's verified working method.
This approach requires no authentication and scrapes live data.
"""

import pandas as pd
import requests
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wikipedia_access():
    """Test if Wikipedia is accessible."""
    try:
        response = requests.get("https://en.wikipedia.org/wiki/QS_World_University_Rankings", timeout=10)
        logger.info(f"Wikipedia access test: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Wikipedia access failed: {e}")
        return False

def get_qs_rankings_from_wikipedia() -> pd.DataFrame:
    """Get QS World University Rankings from Wikipedia."""
    logger.info("Fetching QS rankings from Wikipedia...")
    
    try:
        url = "https://en.wikipedia.org/wiki/QS_World_University_Rankings"
        
        # Read all tables and find the one with 2025 rankings
        tables = pd.read_html(url)
        logger.info(f"Found {len(tables)} tables on QS Wikipedia page")
        
        # Look for the main rankings table (usually the largest one)
        ranking_table = None
        for i, table in enumerate(tables):
            logger.info(f"Table {i}: {table.shape}, columns: {list(table.columns)[:3]}...")
            
            # Look for tables with university names and rankings
            if len(table.columns) >= 3 and len(table) > 50:
                # Check if it looks like a ranking table
                first_col_name = str(table.columns[0]).lower()
                second_col_name = str(table.columns[1]).lower()
                
                if ('rank' in first_col_name or 'position' in first_col_name) and \
                   ('university' in second_col_name or 'institution' in second_col_name):
                    ranking_table = table
                    logger.info(f"Using table {i} as QS ranking table")
                    break
        
        if ranking_table is not None:
            # Clean up the table
            df = ranking_table.copy()
            
            # Standardize column names
            cols = list(df.columns)
            if len(cols) >= 2:
                df = df.rename(columns={
                    cols[0]: 'qs_rank',
                    cols[1]: 'institution'
                })
                
                # Keep only rank and institution columns
                df = df[['qs_rank', 'institution']].copy()
                
                # Clean rank column (remove ranges, keep first number)
                df['qs_rank'] = df['qs_rank'].astype(str).str.extract('(\d+)')[0]
                df['qs_rank'] = pd.to_numeric(df['qs_rank'], errors='coerce')
                
                # Remove rows with missing data
                df = df.dropna().copy()
                
                # Add source info
                df['ranking_source'] = 'QS'
                df['country'] = 'Unknown'  # Will be filled later if needed
                
                logger.info(f"Successfully parsed {len(df)} QS rankings")
                
                # Show sample
                logger.info("Sample QS rankings:")
                for _, row in df.head(10).iterrows():
                    logger.info(f"  {row['qs_rank']:3.0f}. {row['institution']}")
                
                return df
        
        logger.error("Could not find suitable ranking table in QS Wikipedia page")
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Error fetching QS rankings from Wikipedia: {e}")
        return pd.DataFrame()

def get_arwu_rankings_from_wikipedia() -> pd.DataFrame:
    """Get ARWU rankings from Wikipedia."""
    logger.info("Fetching ARWU rankings from Wikipedia...")
    
    try:
        url = "https://en.wikipedia.org/wiki/Academic_Ranking_of_World_Universities"
        
        tables = pd.read_html(url)
        logger.info(f"Found {len(tables)} tables on ARWU Wikipedia page")
        
        # Look for the main ARWU rankings table
        ranking_table = None
        for i, table in enumerate(tables):
            logger.info(f"Table {i}: {table.shape}")
            
            if len(table.columns) >= 3 and len(table) > 20:
                # Check if this looks like the ARWU ranking table
                if any('rank' in str(col).lower() for col in table.columns):
                    ranking_table = table
                    logger.info(f"Using table {i} as ARWU ranking table")
                    break
        
        if ranking_table is not None:
            df = ranking_table.copy()
            
            # Standardize column names
            cols = list(df.columns)
            if len(cols) >= 2:
                df = df.rename(columns={
                    cols[0]: 'arwu_rank',
                    cols[1]: 'institution'
                })
                
                df = df[['arwu_rank', 'institution']].copy()
                
                # Clean rank column
                df['arwu_rank'] = df['arwu_rank'].astype(str).str.extract('(\d+)')[0]
                df['arwu_rank'] = pd.to_numeric(df['arwu_rank'], errors='coerce')
                
                df = df.dropna().copy()
                df['ranking_source'] = 'ARWU'
                
                logger.info(f"Successfully parsed {len(df)} ARWU rankings")
                
                # Show sample
                logger.info("Sample ARWU rankings:")
                for _, row in df.head(10).iterrows():
                    logger.info(f"  {row['arwu_rank']:3.0f}. {row['institution']}")
                
                return df
        
        logger.error("Could not find suitable ranking table in ARWU Wikipedia page")
        return pd.DataFrame()
        
    except Exception as e:
        logger.error(f"Error fetching ARWU rankings from Wikipedia: {e}")
        return pd.DataFrame()

def combine_rankings(qs_df: pd.DataFrame, arwu_df: pd.DataFrame) -> pd.DataFrame:
    """Combine multiple ranking datasets."""
    all_rankings = []
    
    if not qs_df.empty:
        qs_subset = qs_df[['institution', 'qs_rank']].copy()
        qs_subset = qs_subset.rename(columns={'qs_rank': 'rank'})
        qs_subset['ranking_system'] = 'QS'
        all_rankings.append(qs_subset)
    
    if not arwu_df.empty:
        arwu_subset = arwu_df[['institution', 'arwu_rank']].copy()
        arwu_subset = arwu_subset.rename(columns={'arwu_rank': 'rank'})
        arwu_subset['ranking_system'] = 'ARWU'
        all_rankings.append(arwu_subset)
    
    if all_rankings:
        combined = pd.concat(all_rankings, ignore_index=True)
        logger.info(f"Combined rankings: {len(combined)} total entries")
        
        # Count by ranking system
        system_counts = combined['ranking_system'].value_counts()
        for system, count in system_counts.items():
            logger.info(f"  {system}: {count} universities")
        
        return combined
    else:
        return pd.DataFrame()

def main():
    print("=" * 80)
    print("GETTING UNIVERSITY RANKINGS FROM WIKIPEDIA - VERIFIED METHOD")
    print("=" * 80)
    
    # Test Wikipedia access
    if not test_wikipedia_access():
        print("❌ ERROR: Cannot access Wikipedia")
        return None
    
    print("✅ Wikipedia accessible")
    
    # Get QS rankings
    qs_df = get_qs_rankings_from_wikipedia()
    
    # Get ARWU rankings
    arwu_df = get_arwu_rankings_from_wikipedia()
    
    # Combine rankings
    combined_df = combine_rankings(qs_df, arwu_df)
    
    if not combined_df.empty:
        # Save the rankings
        filename = "wikipedia_university_rankings.csv"
        combined_df.to_csv(filename, index=False)
        
        print("\n" + "=" * 80)
        print("SUCCESS: RANKINGS COLLECTED FROM WIKIPEDIA")
        print("=" * 80)
        print(f"Total ranking entries: {len(combined_df)}")
        
        if 'ranking_system' in combined_df.columns:
            system_counts = combined_df['ranking_system'].value_counts()
            for system, count in system_counts.items():
                print(f"{system} rankings: {count} universities")
        
        print(f"Data saved to: {filename}")
        print("Ready for matching with College Scorecard data!")
        
        return combined_df
    else:
        print("❌ ERROR: No rankings collected")
        return None

if __name__ == "__main__":
    rankings = main()