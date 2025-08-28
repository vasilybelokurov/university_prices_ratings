#!/usr/bin/env python3
"""
Fix US tuition rate consistency for international comparison.
Use out-of-state rates for public universities (comparable to UK international rates).
"""

import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_tuition_inconsistencies():
    """Analyze and fix tuition rate inconsistencies."""
    
    # Load the data
    df = pd.read_csv("massive_university_data.csv")
    us_df = df[df['country'] == 'United States'].copy()
    
    print("=" * 80)
    print("US TUITION RATE ANALYSIS")
    print("=" * 80)
    
    # Analyze the current pricing logic
    print(f"\nCURRENT DATA ANALYSIS:")
    print(f"Total US universities: {len(us_df)}")
    
    # Check for universities with different in-state vs out-of-state rates
    us_df['has_different_rates'] = (
        pd.notna(us_df['tuition_in_state_usd']) & 
        pd.notna(us_df['tuition_out_state_usd']) & 
        (us_df['tuition_in_state_usd'] != us_df['tuition_out_state_usd'])
    )
    
    different_rates = us_df[us_df['has_different_rates']]
    same_rates = us_df[~us_df['has_different_rates']]
    
    print(f"Universities with different in-state/out-of-state rates (PUBLIC): {len(different_rates)}")
    print(f"Universities with same rates (PRIVATE): {len(same_rates)}")
    
    # Show examples of the inconsistency
    print(f"\nEXAMPLES OF PUBLIC UNIVERSITIES (different rates):")
    for i, (_, row) in enumerate(different_rates.head(10).iterrows()):
        in_state = row['tuition_in_state_usd']
        out_state = row['tuition_out_state_usd']
        current_price = row['price_usd']
        
        if current_price == out_state:
            rate_used = "OUT-STATE ✓"
        elif current_price == in_state:
            rate_used = "IN-STATE ✗"
        else:
            rate_used = "UNKNOWN ?"
            
        print(f"{i+1:2d}. {row['institution'][:40]:<40} | "
              f"In: ${in_state:6,.0f} | Out: ${out_state:6,.0f} | "
              f"Used: ${current_price:6,.0f} ({rate_used})")
    
    # Check UK rates for comparison
    uk_df = df[df['country'] == 'United Kingdom'].copy()
    print(f"\nUK COMPARISON:")
    print(f"UK universities use INTERNATIONAL rates: ${uk_df['price_usd'].median():,.0f} median")
    print(f"US median with current logic: ${us_df['price_usd'].median():,.0f}")
    
    # Fix the pricing logic
    print(f"\n" + "=" * 80)
    print("APPLYING CONSISTENT PRICING LOGIC")
    print("=" * 80)
    
    # Create corrected pricing
    us_df_corrected = us_df.copy()
    
    # For universities with different rates (public), always use out-of-state
    public_mask = us_df_corrected['has_different_rates']
    private_mask = ~public_mask
    
    # Public universities: use out-of-state rate
    us_df_corrected.loc[public_mask, 'price_usd_corrected'] = us_df_corrected.loc[public_mask, 'tuition_out_state_usd']
    
    # Private universities: use the single rate (either in-state or out-of-state, they're the same)
    us_df_corrected.loc[private_mask, 'price_usd_corrected'] = us_df_corrected.loc[private_mask, 'tuition_out_state_usd'].fillna(
        us_df_corrected.loc[private_mask, 'tuition_in_state_usd']
    )
    
    # Compare before and after
    price_changes = us_df_corrected['price_usd_corrected'] - us_df_corrected['price_usd']
    
    print(f"\nPRICING CORRECTIONS:")
    print(f"Universities with price changes: {(price_changes != 0).sum()}")
    print(f"Average price change: ${price_changes.mean():+,.0f}")
    print(f"Median price change: ${price_changes.median():+,.0f}")
    
    # Show biggest corrections
    significant_changes = us_df_corrected[abs(price_changes) > 1000].copy()
    significant_changes['price_change'] = price_changes[abs(price_changes) > 1000]
    significant_changes = significant_changes.sort_values('price_change', key=abs, ascending=False)
    
    print(f"\nBIGGEST CORRECTIONS (>$1000 difference):")
    for i, (_, row) in enumerate(significant_changes.head(15).iterrows()):
        change = row['price_change']
        old_price = row['price_usd']
        new_price = row['price_usd_corrected']
        print(f"{i+1:2d}. {row['institution'][:35]:<35} | "
              f"Old: ${old_price:6,.0f} → New: ${new_price:6,.0f} | "
              f"Change: ${change:+6,.0f}")
    
    # Update the full dataset
    df_corrected = df.copy()
    us_indices = df_corrected['country'] == 'United States'
    df_corrected.loc[us_indices, 'price_usd'] = us_df_corrected['price_usd_corrected']
    
    print(f"\nFINAL COMPARISON:")
    print(f"Original US median: ${us_df['price_usd'].median():,.0f}")
    print(f"Corrected US median: ${df_corrected[df_corrected['country'] == 'United States']['price_usd'].median():,.0f}")
    print(f"UK international median: ${uk_df['price_usd'].median():,.0f}")
    
    # Save corrected data
    output_file = "corrected_university_data.csv"
    df_corrected.to_csv(output_file, index=False)
    print(f"\nCorrected data saved to: {output_file}")
    
    return df_corrected


if __name__ == "__main__":
    corrected_df = analyze_tuition_inconsistencies()