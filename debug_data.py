#!/usr/bin/env python3
"""Debug the data structure to understand the column issue."""

import pandas as pd

# Load data and check columns
df = pd.read_csv("massive_university_data.csv")
print("Original columns:", df.columns.tolist())
print("Sample data:")
print(df.head())

# Calculate percentiles
df['rank_percentile'] = ((len(df) + 1 - df['arwu_rank'].rank(method='min')) / len(df)) * 100
df['price_percentile'] = (df['price_usd'].rank(method='average') / len(df)) * 100
df['value_score'] = (0.6 * df['rank_percentile']) + (0.4 * (100 - df['price_percentile']))

print("\nAfter adding columns:", df.columns.tolist())
print("Value score sample:")
print(df[['institution', 'country', 'arwu_rank', 'price_usd', 'value_score']].head())

# Split by country
us_df = df[df['country'] == 'United States'].copy()
uk_df = df[df['country'] == 'United Kingdom'].copy()

print(f"\nUS columns: {us_df.columns.tolist()}")
print(f"UK columns: {uk_df.columns.tolist()}")
print(f"Value score in us_df: {'value_score' in us_df.columns}")
print(f"Value score in uk_df: {'value_score' in uk_df.columns}")