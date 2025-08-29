#!/usr/bin/env python3
"""
Analyze why sweet spot universities are outliers from the main trend.
Investigate the specific characteristics that allow them to offer high quality at low prices.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_outlier_reasons():
    """Analyze why sweet spot universities break the normal price-quality trend."""
    
    print("ANALYZING SWEET SPOT OUTLIERS: Why High Quality at Low Price?")
    print("=" * 70)
    
    # Load data
    df = pd.read_csv("scorecard_universities_with_quality_rankings.csv")
    
    # Identify sweet spot universities
    median_price = df['price_usd'].median()
    top_25_quality_threshold = df['quality_ranking'].quantile(0.25)
    
    sweet_spot_mask = (df['quality_ranking'] <= top_25_quality_threshold) & (df['price_usd'] <= median_price)
    sweet_spot_unis = df[sweet_spot_mask].sort_values('quality_ranking').head(10)
    regular_unis = df[~sweet_spot_mask]
    
    print(f"Sweet Spot Universities (n={len(sweet_spot_unis)}):")
    for i, (_, row) in enumerate(sweet_spot_unis.iterrows(), 1):
        print(f"  {i}. {row['institution'][:35]} ({row['state']})")
    
    print("\nANALYZING KEY DIFFERENTIATORS:")
    print("=" * 50)
    
    # 1. Public vs Private Analysis
    print("\n1. FUNDING MODEL ANALYSIS")
    print("-" * 30)
    
    # Identify public universities (common patterns)
    public_keywords = ['University of', 'State University', 'SUNY', 'CUNY', 'Florida State', 'San Diego State']
    
    def is_likely_public(name):
        return any(keyword in name for keyword in public_keywords) or \
               name.startswith('University of ') or \
               'State' in name
    
    sweet_spot_unis['likely_public'] = sweet_spot_unis['institution'].apply(is_likely_public)
    
    public_count = sweet_spot_unis['likely_public'].sum()
    private_count = len(sweet_spot_unis) - public_count
    
    print(f"Public universities in sweet spot: {public_count}/10 ({public_count/10*100:.0f}%)")
    print(f"Private universities in sweet spot: {private_count}/10 ({private_count/10*100:.0f}%)")
    
    print("\nPublic universities (state subsidized):")
    for _, row in sweet_spot_unis[sweet_spot_unis['likely_public']].iterrows():
        print(f"  • {row['institution']} ({row['state']}) - ${row['price_usd']:,}")
    
    print("\nPrivate universities (must be efficient):")
    for _, row in sweet_spot_unis[~sweet_spot_unis['likely_public']].iterrows():
        print(f"  • {row['institution']} ({row['state']}) - ${row['price_usd']:,}")
    
    # 2. Geographic Analysis
    print("\n2. GEOGRAPHIC PATTERNS")
    print("-" * 25)
    
    state_counts = sweet_spot_unis['state'].value_counts()
    print("States with multiple sweet spot universities:")
    for state, count in state_counts[state_counts > 1].items():
        unis_in_state = sweet_spot_unis[sweet_spot_unis['state'] == state]['institution'].tolist()
        print(f"  {state}: {count} universities")
        for uni in unis_in_state:
            price = sweet_spot_unis[sweet_spot_unis['institution'] == uni]['price_usd'].iloc[0]
            print(f"    • {uni[:40]} (${price:,})")
    
    # 3. Quality Component Analysis
    print("\n3. QUALITY STRATEGY ANALYSIS")
    print("-" * 30)
    
    # Compare sweet spot vs all universities on quality components
    components = ['academic_selectivity_score', 'student_outcomes_score', 'student_quality_score']
    
    print("Average quality component scores:")
    print(f"{'Component':<25} {'Sweet Spot':<12} {'All Unis':<12} {'Difference'}")
    print("-" * 55)
    
    for component in components:
        if component in df.columns:
            sweet_avg = sweet_spot_unis[component].mean()
            all_avg = df[component].mean()
            diff = sweet_avg - all_avg
            print(f"{component.replace('_score', ''):<25} {sweet_avg:<12.1f} {all_avg:<12.1f} {diff:+.1f}")
    
    # 4. Specific Metrics Analysis
    print("\n4. SPECIFIC PERFORMANCE METRICS")
    print("-" * 35)
    
    metrics_to_analyze = [
        ('latest.admissions.sat_scores.average.overall', 'SAT Scores', 'higher_better'),
        ('latest.completion.completion_rate_4yr_100nt', '4-Year Graduation Rate', 'higher_better'),
        ('latest.earnings.10_yrs_after_entry.median', '10-Year Earnings ($)', 'higher_better'),
        ('latest.admissions.admission_rate.overall', 'Admission Rate', 'lower_better'),
        ('latest.aid.pell_grant_rate', 'Pell Grant Rate (%)', 'context'),
        ('student_size', 'Student Size', 'context')
    ]
    
    print(f"{'Metric':<25} {'Sweet Spot Avg':<15} {'All Unis Avg':<15} {'Interpretation'}")
    print("-" * 80)
    
    for metric, name, direction in metrics_to_analyze:
        if metric in df.columns:
            sweet_avg = sweet_spot_unis[metric].mean()
            all_avg = df[metric].mean()
            
            if metric == 'latest.admissions.admission_rate.overall':
                sweet_avg *= 100  # Convert to percentage
                all_avg *= 100
                interpretation = "More selective" if sweet_avg < all_avg else "Less selective"
                print(f"{name:<25} {sweet_avg:<15.1f} {all_avg:<15.1f} {interpretation}")
            elif metric == 'latest.aid.pell_grant_rate':
                sweet_avg *= 100
                all_avg *= 100
                interpretation = "More low-income" if sweet_avg > all_avg else "Less low-income"
                print(f"{name:<25} {sweet_avg:<15.1f} {all_avg:<15.1f} {interpretation}")
            elif metric == 'latest.completion.completion_rate_4yr_100nt':
                sweet_avg *= 100
                all_avg *= 100
                interpretation = "Better retention" if sweet_avg > all_avg else "Lower retention"
                print(f"{name:<25} {sweet_avg:<15.1f} {all_avg:<15.1f} {interpretation}")
            elif metric == 'student_size':
                interpretation = "Larger" if sweet_avg > all_avg else "Smaller"
                print(f"{name:<25} {sweet_avg:<15,.0f} {all_avg:<15,.0f} {interpretation}")
            else:
                interpretation = "Higher" if sweet_avg > all_avg else "Lower"
                print(f"{name:<25} {sweet_avg:<15,.0f} {all_avg:<15,.0f} {interpretation}")
    
    # 5. Individual University Deep Dive
    print("\n5. TOP 3 SWEET SPOT UNIVERSITIES - DEEP DIVE")
    print("-" * 50)
    
    top_3 = sweet_spot_unis.head(3)
    
    for i, (_, row) in enumerate(top_3.iterrows(), 1):
        print(f"\n{i}. {row['institution']} ({row['state']})")
        print(f"   Quality Rank: #{row['quality_ranking']:.0f} | Price: ${row['price_usd']:,}")
        print(f"   Student Size: {row['student_size']:,.0f}")
        
        if pd.notna(row['latest.admissions.sat_scores.average.overall']):
            print(f"   SAT Score: {row['latest.admissions.sat_scores.average.overall']:.0f}")
        
        if pd.notna(row['latest.completion.completion_rate_4yr_100nt']):
            print(f"   4-Year Graduation Rate: {row['latest.completion.completion_rate_4yr_100nt']*100:.1f}%")
        
        if pd.notna(row['latest.earnings.10_yrs_after_entry.median']):
            print(f"   10-Year Median Earnings: ${row['latest.earnings.10_yrs_after_entry.median']:,.0f}")
        
        # Determine key success factors
        reasons = []
        if is_likely_public(row['institution']):
            reasons.append("State subsidized (public university)")
        if row['student_size'] > df['student_size'].median():
            reasons.append("Large scale operations (economies of scale)")
        if pd.notna(row['latest.admissions.admission_rate.overall']) and row['latest.admissions.admission_rate.overall'] < 0.5:
            reasons.append("Highly selective admissions")
        
        print(f"   Key Success Factors: {', '.join(reasons) if reasons else 'Efficient operations'}")
    
    return sweet_spot_unis

def create_outlier_explanation_plot(sweet_spot_unis):
    """Create visualization showing why these are outliers."""
    
    df = pd.read_csv("scorecard_universities_with_quality_rankings.csv")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Why Sweet Spot Universities Are Outliers: Key Differentiators', fontsize=16, fontweight='bold')
    
    # 1. Public vs Private comparison
    public_mask = df['institution'].str.contains('University of|State|SUNY|CUNY', na=False)
    
    ax1.scatter(df[public_mask]['price_usd'], df[public_mask]['overall_quality_score'], 
                alpha=0.5, c='blue', s=20, label='Public Universities')
    ax1.scatter(df[~public_mask]['price_usd'], df[~public_mask]['overall_quality_score'], 
                alpha=0.5, c='red', s=20, label='Private Universities')
    ax1.scatter(sweet_spot_unis['price_usd'], sweet_spot_unis['overall_quality_score'], 
                c='gold', s=100, edgecolor='black', linewidth=2, label='Sweet Spot', zorder=5)
    
    ax1.set_xlabel('Price (USD)')
    ax1.set_ylabel('Quality Score')
    ax1.set_title('Public vs Private Universities')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Student size analysis
    ax2.scatter(df['student_size'], df['overall_quality_score'], alpha=0.5, c='gray', s=20)
    ax2.scatter(sweet_spot_unis['student_size'], sweet_spot_unis['overall_quality_score'], 
                c='gold', s=100, edgecolor='black', linewidth=2, zorder=5)
    
    ax2.set_xlabel('Student Size')
    ax2.set_ylabel('Quality Score')
    ax2.set_title('Student Size vs Quality (Sweet Spot = Gold)')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    
    # 3. Graduation rate vs price
    ax3.scatter(df['price_usd'], df['latest.completion.completion_rate_4yr_100nt']*100, 
                alpha=0.5, c='gray', s=20)
    ax3.scatter(sweet_spot_unis['price_usd'], sweet_spot_unis['latest.completion.completion_rate_4yr_100nt']*100, 
                c='gold', s=100, edgecolor='black', linewidth=2, zorder=5)
    
    ax3.set_xlabel('Price (USD)')
    ax3.set_ylabel('4-Year Graduation Rate (%)')
    ax3.set_title('Graduation Rate vs Price')
    ax3.grid(True, alpha=0.3)
    
    # 4. SAT scores vs price
    sat_data = df[df['latest.admissions.sat_scores.average.overall'].notna()]
    sweet_sat = sweet_spot_unis[sweet_spot_unis['latest.admissions.sat_scores.average.overall'].notna()]
    
    ax4.scatter(sat_data['price_usd'], sat_data['latest.admissions.sat_scores.average.overall'], 
                alpha=0.5, c='gray', s=20)
    ax4.scatter(sweet_sat['price_usd'], sweet_sat['latest.admissions.sat_scores.average.overall'], 
                c='gold', s=100, edgecolor='black', linewidth=2, zorder=5)
    
    ax4.set_xlabel('Price (USD)')
    ax4.set_ylabel('Average SAT Score')
    ax4.set_title('SAT Scores vs Price')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('sweet_spot_outlier_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ Outlier analysis visualization saved: sweet_spot_outlier_analysis.png")

if __name__ == "__main__":
    sweet_spot_unis = analyze_outlier_reasons()
    create_outlier_explanation_plot(sweet_spot_unis)