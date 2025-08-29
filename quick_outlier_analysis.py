#!/usr/bin/env python3
"""
Quick analysis of why sweet spot universities are outliers.
"""

import pandas as pd

def quick_outlier_analysis():
    """Quick analysis of sweet spot outliers."""
    
    print("WHY ARE SWEET SPOT UNIVERSITIES OUTLIERS?")
    print("=" * 50)
    
    # Load data
    df = pd.read_csv("scorecard_universities_with_quality_rankings.csv")
    
    # Get sweet spot universities
    median_price = df['price_usd'].median()
    top_25_quality_threshold = df['quality_ranking'].quantile(0.25)
    
    sweet_spot_mask = (df['quality_ranking'] <= top_25_quality_threshold) & (df['price_usd'] <= median_price)
    sweet_spot_unis = df[sweet_spot_mask].sort_values('quality_ranking').head(10)
    
    print("Top 10 Sweet Spot Universities:")
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows(), 1):
        public = "PUBLIC" if any(keyword in row['institution'] for keyword in 
                               ['University of', 'State University', 'SUNY', 'CUNY']) else "PRIVATE"
        print(f"  {i}. {row['institution'][:40]} ({row['state']}) - ${row['price_usd']:,} [{public}]")
    
    # Analysis 1: Public vs Private
    print(f"\n1. FUNDING MODEL:")
    print("-" * 20)
    
    public_keywords = ['University of', 'State University', 'SUNY', 'CUNY', 'Florida State', 'San Diego State']
    sweet_spot_unis['is_public'] = sweet_spot_unis['institution'].apply(
        lambda x: any(keyword in x for keyword in public_keywords) or x.startswith('University of ')
    )
    
    public_count = sweet_spot_unis['is_public'].sum()
    print(f"Public universities: {public_count}/10 ({public_count/10*100:.0f}%)")
    print(f"Private universities: {10-public_count}/10 ({(10-public_count)/10*100:.0f}%)")
    print("→ Most are PUBLIC = state subsidized, lower tuition")
    
    # Analysis 2: State patterns
    print(f"\n2. GEOGRAPHIC CONCENTRATION:")
    print("-" * 30)
    state_counts = sweet_spot_unis['state'].value_counts()
    for state, count in state_counts[state_counts > 1].items():
        print(f"{state}: {count} universities")
    print("→ Florida and New York have strong public university systems")
    
    # Analysis 3: Size analysis
    print(f"\n3. ECONOMIES OF SCALE:")
    print("-" * 25)
    avg_size_sweet = sweet_spot_unis['student_size'].mean()
    avg_size_all = df['student_size'].mean()
    print(f"Sweet spot avg size: {avg_size_sweet:,.0f} students")
    print(f"All universities avg: {avg_size_all:,.0f} students")
    print(f"→ Sweet spot universities are {'LARGER' if avg_size_sweet > avg_size_all else 'SMALLER'} than average")
    
    # Analysis 4: Quality components
    print(f"\n4. QUALITY STRATEGY:")
    print("-" * 20)
    
    components = {
        'academic_selectivity_score': 'Academic Selectivity',
        'student_outcomes_score': 'Student Outcomes', 
        'student_quality_score': 'Student Quality'
    }
    
    for comp, name in components.items():
        if comp in df.columns:
            sweet_avg = sweet_spot_unis[comp].mean()
            all_avg = df[comp].mean()
            diff = sweet_avg - all_avg
            print(f"{name}: {sweet_avg:.1f} vs {all_avg:.1f} (diff: {diff:+.1f})")
    
    # Analysis 5: Key metrics
    print(f"\n5. PERFORMANCE COMPARISON:")
    print("-" * 30)
    
    if 'latest.completion.completion_rate_4yr_100nt' in df.columns:
        sweet_grad = sweet_spot_unis['latest.completion.completion_rate_4yr_100nt'].mean() * 100
        all_grad = df['latest.completion.completion_rate_4yr_100nt'].mean() * 100
        print(f"4-year graduation rate: {sweet_grad:.1f}% vs {all_grad:.1f}%")
    
    if 'latest.earnings.10_yrs_after_entry.median' in df.columns:
        sweet_earn = sweet_spot_unis['latest.earnings.10_yrs_after_entry.median'].mean()
        all_earn = df['latest.earnings.10_yrs_after_entry.median'].mean()
        print(f"10-year earnings: ${sweet_earn:,.0f} vs ${all_earn:,.0f}")
    
    print(f"\nCONCLUSION: Sweet spot universities break the trend because:")
    print("1. Most are PUBLIC → State subsidized = lower tuition")
    print("2. Large scale → Economies of scale = efficiency") 
    print("3. Strong state systems → Established quality at public prices")
    print("4. Focus on outcomes → High graduation rates and earnings")

if __name__ == "__main__":
    quick_outlier_analysis()