#!/usr/bin/env python3
"""
Verify the authenticity of our collected data by testing against real sources.
"""

import requests
import json
import pandas as pd

def test_college_scorecard_api():
    """Test College Scorecard API to verify tuition data is real."""
    api_key = 'jHFyoMT1IT4cT79aVDEUGmRdbnX6gxa5CCrLO4k9'
    base_url = 'https://api.data.gov/ed/collegescorecard/v1/schools'
    
    # Test famous universities
    test_universities = ['Harvard University', 'Stanford University', 'MIT', 'Yale University']
    
    print("VERIFYING COLLEGE SCORECARD API DATA:")
    print("=" * 60)
    
    for uni_name in test_universities:
        params = {
            'school.name': uni_name,
            'fields': 'school.name,latest.cost.tuition.in_state,latest.cost.tuition.out_of_state,latest.cost.attendance.academic_year',
            'api_key': api_key
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            print(f"\n{uni_name}:")
            print(f"  API Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    result = data['results'][0]
                    print(f"  Name: {result.get('school.name', 'N/A')}")
                    in_state = result.get('latest.cost.tuition.in_state')
                    out_state = result.get('latest.cost.tuition.out_of_state') 
                    total_cost = result.get('latest.cost.attendance.academic_year')
                    
                    print(f"  In-state: ${in_state:,}" if in_state else "  In-state: N/A")
                    print(f"  Out-state: ${out_state:,}" if out_state else "  Out-state: N/A")
                    print(f"  Total cost: ${total_cost:,}" if total_cost else "  Total cost: N/A")
                else:
                    print("  No data found in API response")
            else:
                print(f"  API Error: {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")


def verify_our_collected_data():
    """Check our collected data against what we know should be correct."""
    
    print("\n\nVERIFYING OUR COLLECTED DATA:")
    print("=" * 60)
    
    # Real ARWU 2023 Top 10 (from official source)
    real_arwu_top10 = {
        "Harvard University": 1,
        "Stanford University": 2, 
        "Massachusetts Institute of Technology": 3,
        "University of Cambridge": 4,
        "University of California, Berkeley": 5,
        "Princeton University": 6,
        "University of Oxford": 7,
        "Columbia University": 8,
        "California Institute of Technology": 9,
        "University of Chicago": 10
    }
    
    # Check our datasets
    datasets = [
        'massive_university_data.csv',
        'real_university_data.csv', 
        'comprehensive_university_analysis.csv'
    ]
    
    for dataset in datasets:
        try:
            print(f"\nChecking {dataset}:")
            df = pd.read_csv(dataset)
            
            # Check if we have the real top universities with correct rankings
            correct_count = 0
            total_found = 0
            
            for uni_name, real_rank in real_arwu_top10.items():
                matches = df[df['institution'].str.contains(uni_name.replace('Massachusetts Institute of Technology', 'MIT'), case=False, na=False)]
                
                if not matches.empty:
                    total_found += 1
                    our_rank = matches.iloc[0]['arwu_rank'] if 'arwu_rank' in matches.columns else matches.iloc[0].get('rank', 'N/A')
                    
                    if our_rank == real_rank:
                        correct_count += 1
                        print(f"  ✅ {uni_name}: Rank {our_rank} (CORRECT)")
                    else:
                        print(f"  ❌ {uni_name}: Our rank {our_rank}, Real rank {real_rank} (WRONG)")
                else:
                    print(f"  ⚠️  {uni_name}: Not found in dataset")
            
            print(f"  Summary: {correct_count}/{total_found} correct rankings found")
            
            # Check for obviously fake data
            if 'arwu_rank' in df.columns:
                rank_1_unis = df[df['arwu_rank'] == 1]['institution'].tolist()
                if rank_1_unis:
                    print(f"  Universities with rank 1: {rank_1_unis}")
                    if 'Harvard University' not in rank_1_unis:
                        print(f"  ❌ FAKE DATA: Rank 1 should be Harvard, found: {rank_1_unis}")
            
        except FileNotFoundError:
            print(f"  File not found: {dataset}")
        except Exception as e:
            print(f"  Error reading {dataset}: {e}")


def main():
    print("DATA AUTHENTICITY VERIFICATION")
    print("=" * 60)
    
    # Test API
    test_college_scorecard_api()
    
    # Verify our data
    verify_our_collected_data()
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()