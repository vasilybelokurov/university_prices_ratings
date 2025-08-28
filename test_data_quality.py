#!/usr/bin/env python3
"""
Data quality validation and testing for university analysis.
Tests data completeness, validity, and analysis results.
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataQualityTester:
    def __init__(self):
        self.test_results = {}
        
    def test_file_existence(self) -> bool:
        """Test that all expected output files exist."""
        logger.info("Testing file existence...")
        
        expected_files = [
            'us_universities_sample.csv',
            'uk_universities_sample.csv', 
            'combined_university_data.csv',
            'university_price_vs_ranking_scatter.png',
            'university_distributions_boxplot.png',
            'university_density_plots.png'
        ]
        
        missing_files = []
        for file in expected_files:
            if not os.path.exists(file):
                missing_files.append(file)
                
        self.test_results['file_existence'] = {
            'passed': len(missing_files) == 0,
            'missing_files': missing_files,
            'total_expected': len(expected_files)
        }
        
        logger.info(f"File existence test: {'PASSED' if len(missing_files) == 0 else 'FAILED'}")
        return len(missing_files) == 0
        
    def test_data_completeness(self) -> bool:
        """Test data completeness and validity."""
        logger.info("Testing data completeness...")
        
        try:
            us_data = pd.read_csv('us_universities_sample.csv')
            uk_data = pd.read_csv('uk_universities_sample.csv')
            combined_data = pd.read_csv('combined_university_data.csv')
        except FileNotFoundError as e:
            logger.error(f"Cannot load data files: {e}")
            return False
            
        tests = {}
        
        # Test US data
        tests['us_data'] = {
            'row_count': len(us_data) >= 30,  # Should have at least 30 universities
            'required_columns': all(col in us_data.columns for col in ['name', 'tuition', 'ranking']),
            'no_null_prices': us_data['tuition'].notna().sum() >= 30,
            'no_null_rankings': us_data['ranking'].notna().sum() >= 30,
            'positive_tuition': (us_data['tuition'] >= 0).all(),
            'reasonable_rankings': (us_data['ranking'] >= 1).all() and (us_data['ranking'] <= 200).all()
        }
        
        # Test UK data  
        tests['uk_data'] = {
            'row_count': len(uk_data) >= 30,
            'required_columns': all(col in uk_data.columns for col in ['name', 'intl_tuition', 'composite_rank']),
            'no_null_prices': uk_data['intl_tuition'].notna().sum() >= 30,
            'no_null_rankings': uk_data['composite_rank'].notna().sum() >= 30,
            'positive_tuition': (uk_data['intl_tuition'] >= 0).all(),
            'reasonable_rankings': (uk_data['composite_rank'] >= 1).all() and (uk_data['composite_rank'] <= 200).all()
        }
        
        # Test combined data
        tests['combined_data'] = {
            'total_count': len(combined_data) >= 60,
            'has_both_countries': set(combined_data['country'].unique()) == {'US', 'UK'},
            'required_columns': all(col in combined_data.columns for col in ['name', 'country', 'price_usd', 'rank']),
            'no_null_values': combined_data[['price_usd', 'rank']].notna().all().all(),
            'positive_prices': (combined_data['price_usd'] >= 0).all(),
            'reasonable_rankings': (combined_data['rank'] >= 1).all() and (combined_data['rank'] <= 200).all()
        }
        
        self.test_results['data_completeness'] = tests
        
        # Overall pass/fail
        all_passed = all([all(dataset_tests.values()) for dataset_tests in tests.values()])
        logger.info(f"Data completeness test: {'PASSED' if all_passed else 'FAILED'}")
        
        return all_passed
        
    def test_statistical_validity(self) -> bool:
        """Test statistical properties of the analysis."""
        logger.info("Testing statistical validity...")
        
        try:
            combined_data = pd.read_csv('combined_university_data.csv')
        except FileNotFoundError:
            logger.error("Combined data file not found")
            return False
            
        tests = {}
        
        # Test price distributions
        us_data = combined_data[combined_data['country'] == 'US']
        uk_data = combined_data[combined_data['country'] == 'UK']
        
        tests['price_distributions'] = {
            'us_price_range': us_data['price_usd'].min() >= 0 and us_data['price_usd'].max() <= 100000,
            'uk_price_range': uk_data['price_usd'].min() >= 10000 and uk_data['price_usd'].max() <= 60000,  # Converted to USD
            'us_price_variance': us_data['price_usd'].std() > 5000,  # Should have significant variance
            'uk_price_variance': uk_data['price_usd'].std() > 2000,
        }
        
        # Test correlation strengths
        overall_corr = combined_data['price_usd'].corr(combined_data['rank'])
        us_corr = us_data['price_usd'].corr(us_data['rank'])
        uk_corr = uk_data['price_usd'].corr(uk_data['rank'])
        
        tests['correlations'] = {
            'overall_correlation_exists': abs(overall_corr) > 0.3,
            'us_correlation_reasonable': abs(us_corr) > 0.2,
            'uk_correlation_reasonable': abs(uk_corr) > 0.2,
            'correlations_negative': overall_corr < 0 and us_corr < 0 and uk_corr < 0  # Better rank = lower number = higher price
        }
        
        # Test sample sizes
        tests['sample_sizes'] = {
            'adequate_overall_n': len(combined_data) >= 60,
            'adequate_us_n': len(us_data) >= 30,
            'adequate_uk_n': len(uk_data) >= 30,
        }
        
        self.test_results['statistical_validity'] = tests
        
        all_passed = all([all(test_group.values()) for test_group in tests.values()])
        logger.info(f"Statistical validity test: {'PASSED' if all_passed else 'FAILED'}")
        
        return all_passed
        
    def test_plot_generation(self) -> bool:
        """Test that plots were generated and have reasonable file sizes."""
        logger.info("Testing plot generation...")
        
        plot_files = [
            'university_price_vs_ranking_scatter.png',
            'university_distributions_boxplot.png', 
            'university_density_plots.png'
        ]
        
        tests = {}
        
        for plot_file in plot_files:
            if os.path.exists(plot_file):
                file_size = os.path.getsize(plot_file)
                tests[plot_file] = {
                    'exists': True,
                    'reasonable_size': 10000 < file_size < 5000000  # Between 10KB and 5MB
                }
            else:
                tests[plot_file] = {
                    'exists': False,
                    'reasonable_size': False
                }
                
        self.test_results['plot_generation'] = tests
        
        all_passed = all([all(plot_tests.values()) for plot_tests in tests.values()])
        logger.info(f"Plot generation test: {'PASSED' if all_passed else 'FAILED'}")
        
        return all_passed
        
    def run_all_tests(self) -> Dict:
        """Run all data quality tests."""
        logger.info("Running comprehensive data quality tests...")
        
        test_results = {
            'file_existence': self.test_file_existence(),
            'data_completeness': self.test_data_completeness(),
            'statistical_validity': self.test_statistical_validity(),
            'plot_generation': self.test_plot_generation()
        }
        
        overall_pass = all(test_results.values())
        
        logger.info(f"Overall test result: {'PASSED' if overall_pass else 'FAILED'}")
        
        return {
            'overall_passed': overall_pass,
            'individual_tests': test_results,
            'detailed_results': self.test_results
        }
        
    def print_test_summary(self, results: Dict):
        """Print a detailed test summary."""
        print("\n" + "=" * 60)
        print("DATA QUALITY TEST SUMMARY")
        print("=" * 60)
        
        print(f"\nOverall Result: {'✓ PASSED' if results['overall_passed'] else '✗ FAILED'}")
        
        print(f"\nIndividual Test Results:")
        for test_name, passed in results['individual_tests'].items():
            status = '✓ PASSED' if passed else '✗ FAILED'
            print(f"  {test_name}: {status}")
            
        # Print detailed failures if any
        if not results['overall_passed']:
            print(f"\nDetailed Failure Information:")
            for test_category, test_data in results['detailed_results'].items():
                if isinstance(test_data, dict):
                    failed_tests = []
                    for key, value in test_data.items():
                        if isinstance(value, dict):
                            failed_subtests = [subkey for subkey, subvalue in value.items() if not subvalue]
                            if failed_subtests:
                                failed_tests.extend([f"{key}.{subtest}" for subtest in failed_subtests])
                        elif not value:
                            failed_tests.append(key)
                    
                    if failed_tests:
                        print(f"  {test_category}: {', '.join(failed_tests)}")
                        
        print(f"\nTest completed successfully!")

def main():
    """Run data quality tests."""
    tester = DataQualityTester()
    results = tester.run_all_tests()
    tester.print_test_summary(results)
    
    return results

if __name__ == "__main__":
    main()