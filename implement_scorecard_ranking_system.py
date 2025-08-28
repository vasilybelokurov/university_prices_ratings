#!/usr/bin/env python3
"""
Implement comprehensive university quality ranking system using College Scorecard metrics.
Apply to all 1,213 US universities with real tuition data.
"""

import requests
import pandas as pd
import numpy as np
import time
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScorecardQualityRanker:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
        self.session = requests.Session()
        
        # Quality metrics with their weights and directions
        self.quality_components = {
            'academic_selectivity': {
                'weight': 0.30,
                'metrics': {
                    'latest.admissions.sat_scores.average.overall': {'weight': 0.4, 'higher_better': True},
                    'latest.admissions.act_scores.midpoint.cumulative': {'weight': 0.4, 'higher_better': True},
                    'latest.admissions.admission_rate.overall': {'weight': 0.2, 'higher_better': False}  # Lower admission rate = more selective
                }
            },
            'student_outcomes': {
                'weight': 0.40,
                'metrics': {
                    'latest.completion.completion_rate_4yr_100nt': {'weight': 0.4, 'higher_better': True},
                    'latest.earnings.10_yrs_after_entry.median': {'weight': 0.4, 'higher_better': True},
                    'latest.student.retention_rate.four_year.full_time': {'weight': 0.2, 'higher_better': True}
                }
            },
            'student_quality': {
                'weight': 0.20,
                'metrics': {
                    'latest.student.part_time_share': {'weight': 0.5, 'higher_better': False},  # Lower part-time = higher quality
                    'latest.aid.pell_grant_rate': {'weight': 0.5, 'higher_better': False}  # Lower Pell rate = higher income students
                }
            },
            'financial_health': {
                'weight': 0.10,
                'metrics': {
                    'latest.repayment.1_yr_repayment.overall': {'weight': 1.0, 'higher_better': True}
                }
            }
        }
        
    def get_all_quality_fields(self) -> List[str]:
        """Get all quality metric field names."""
        fields = []
        for component in self.quality_components.values():
            fields.extend(component['metrics'].keys())
        return fields
    
    def collect_universities_with_quality_metrics(self, per_page: int = 100, max_pages: int = 20) -> pd.DataFrame:
        """Collect universities with comprehensive quality metrics."""
        
        logger.info("Collecting universities with quality metrics...")
        
        # All fields we need
        quality_fields = self.get_all_quality_fields()
        
        base_fields = [
            'id', 'school.name', 'school.state', 'school.city',
            'school.school_url', 'latest.cost.tuition.in_state', 
            'latest.cost.tuition.out_of_state', 'latest.cost.attendance.academic_year',
            'latest.student.size'
        ]
        
        all_fields = base_fields + quality_fields
        
        all_universities = []
        page = 0
        
        base_params = {
            'api_key': self.api_key,
            'per_page': per_page,
            'fields': ','.join(all_fields),
            'school.degrees_awarded.predominant': '3,4',  # Bachelor's + Graduate
            'school.operating': '1',
            'latest.student.size__range': '1000..'  # Minimum size filter
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
                    logger.info(f"No more results on page {page + 1}")
                    break
                
                # Filter for universities with sufficient quality data
                valid_universities = []
                for school in results:
                    # Must have basic data
                    if not (school.get('school.name') and 
                           (school.get('latest.cost.tuition.out_of_state') or school.get('latest.cost.tuition.in_state'))):
                        continue
                    
                    # Count available quality metrics
                    available_metrics = sum(1 for field in quality_fields if school.get(field) is not None)
                    
                    # Require at least 5 out of 9 quality metrics
                    if available_metrics >= 5:
                        # Prefer out-of-state tuition for consistency
                        tuition = (school.get('latest.cost.tuition.out_of_state') or 
                                 school.get('latest.cost.tuition.in_state'))
                        
                        uni_data = {
                            'scorecard_id': school.get('id'),
                            'institution': school.get('school.name'),
                            'state': school.get('school.state'),
                            'city': school.get('school.city'),
                            'url': school.get('school.school_url'),
                            'tuition_in_state_usd': school.get('latest.cost.tuition.in_state'),
                            'tuition_out_state_usd': school.get('latest.cost.tuition.out_of_state'),
                            'total_cost_usd': school.get('latest.cost.attendance.academic_year'),
                            'student_size': school.get('latest.student.size'),
                            'price_usd': tuition,
                            'available_quality_metrics': available_metrics
                        }
                        
                        # Add all quality metrics
                        for field in quality_fields:
                            uni_data[field] = school.get(field)
                        
                        valid_universities.append(uni_data)
                
                all_universities.extend(valid_universities)
                logger.info(f"  ✅ Got {len(valid_universities)} universities with quality data from page {page + 1}")
                logger.info(f"  📊 Total collected: {len(all_universities)}")
                
                time.sleep(0.5)  # Rate limiting
                page += 1
                
            except Exception as e:
                logger.error(f"❌ Error on page {page + 1}: {e}")
                break
        
        if all_universities:
            df = pd.DataFrame(all_universities)
            df['country'] = 'United States'
            logger.info(f"🎉 Collected {len(df)} US universities with quality metrics")
            return df
        else:
            return pd.DataFrame()
    
    def calculate_quality_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive quality scores for each university."""
        
        logger.info("Calculating quality scores...")
        df = df.copy()
        
        # Initialize score columns
        for component_name in self.quality_components.keys():
            df[f'{component_name}_score'] = 0.0
        
        df['overall_quality_score'] = 0.0
        df['quality_ranking'] = 0
        
        for component_name, component_info in self.quality_components.items():
            logger.info(f"Calculating {component_name} scores...")
            
            component_scores = []
            
            for _, row in df.iterrows():
                metric_scores = []
                total_weight = 0
                
                for metric_name, metric_info in component_info['metrics'].items():
                    value = row.get(metric_name)
                    
                    if pd.notna(value):
                        # Normalize metric to 0-100 scale
                        series_values = df[metric_name].dropna()
                        
                        if len(series_values) > 1:
                            if metric_info['higher_better']:
                                # Higher values are better (SAT, completion rate, etc.)
                                normalized = 100 * (value - series_values.min()) / (series_values.max() - series_values.min())
                            else:
                                # Lower values are better (admission rate, Pell grant rate)
                                normalized = 100 * (series_values.max() - value) / (series_values.max() - series_values.min())
                            
                            metric_scores.append(normalized * metric_info['weight'])
                            total_weight += metric_info['weight']
                
                # Calculate component score
                if total_weight > 0:
                    component_score = sum(metric_scores) / total_weight
                else:
                    component_score = 50.0  # Neutral score for missing data
                
                component_scores.append(component_score)
            
            # Store component scores
            df[f'{component_name}_score'] = component_scores
        
        # Calculate overall quality score
        overall_scores = []
        for _, row in df.iterrows():
            weighted_sum = 0
            total_weight = 0
            
            for component_name, component_info in self.quality_components.items():
                component_score = row[f'{component_name}_score']
                if pd.notna(component_score):
                    weighted_sum += component_score * component_info['weight']
                    total_weight += component_info['weight']
            
            if total_weight > 0:
                overall_score = weighted_sum / total_weight
            else:
                overall_score = 50.0
            
            overall_scores.append(overall_score)
        
        df['overall_quality_score'] = overall_scores
        
        # Create quality rankings (1 = best)
        df = df.sort_values('overall_quality_score', ascending=False).reset_index(drop=True)
        df['quality_ranking'] = range(1, len(df) + 1)
        
        logger.info(f"✅ Quality scores calculated for {len(df)} universities")
        
        return df
    
    def analyze_quality_rankings(self, df: pd.DataFrame):
        """Analyze the calculated quality rankings."""
        
        logger.info("\nQUALITY RANKING ANALYSIS:")
        logger.info("=" * 50)
        
        # Top 10 universities by quality
        top_10 = df.head(10)
        logger.info("TOP 10 UNIVERSITIES BY QUALITY:")
        logger.info("-" * 40)
        
        for _, row in top_10.iterrows():
            name = row['institution'][:40]
            state = row['state']
            score = row['overall_quality_score']
            price = row['price_usd']
            
            logger.info(f"{row['quality_ranking']:2}. {name:<40} ({state}) | Score: {score:5.1f} | ${price:6,.0f}")
        
        # Score distribution
        score_stats = df['overall_quality_score'].describe()
        logger.info(f"\nQuality Score Statistics:")
        logger.info(f"  Mean: {score_stats['mean']:.1f}")
        logger.info(f"  Median: {score_stats['50%']:.1f}")
        logger.info(f"  Std Dev: {score_stats['std']:.1f}")
        logger.info(f"  Range: {score_stats['min']:.1f} - {score_stats['max']:.1f}")
        
        # Component score analysis
        logger.info(f"\nCOMPONENT SCORE ANALYSIS:")
        for component in self.quality_components.keys():
            col = f'{component}_score'
            if col in df.columns:
                mean_score = df[col].mean()
                logger.info(f"  {component}: {mean_score:.1f} average")
        
        return df

def main():
    print("=" * 80)
    print("IMPLEMENTING SCORECARD QUALITY RANKING SYSTEM")
    print("=" * 80)
    
    api_key = "jHFyoMT1IT4cT79aVDEUGmRdbnX6gxa5CCrLO4k9"
    ranker = ScorecardQualityRanker(api_key)
    
    # Collect universities with quality metrics
    df = ranker.collect_universities_with_quality_metrics(per_page=100, max_pages=15)
    
    if not df.empty:
        # Calculate quality scores
        df_ranked = ranker.calculate_quality_scores(df)
        
        # Analyze results
        ranker.analyze_quality_rankings(df_ranked)
        
        # Save the ranked data
        filename = "scorecard_universities_with_quality_rankings.csv"
        df_ranked.to_csv(filename, index=False)
        
        print("\n" + "=" * 80)
        print("SUCCESS: QUALITY RANKING SYSTEM IMPLEMENTED")
        print("=" * 80)
        print(f"Universities with quality rankings: {len(df_ranked)}")
        print(f"Quality metrics used: {len(ranker.get_all_quality_fields())}")
        print(f"Data saved to: {filename}")
        print("Ready for final analysis: price vs quality ranking!")
        
        return df_ranked
    else:
        print("❌ ERROR: No data collected")
        return None

if __name__ == "__main__":
    data = main()