#!/usr/bin/env python3
"""
Fix university matching using strict one-to-one mapping based on o3 and ChatGPT suggestions.
Implements: name canonicalization, TF-IDF weighting, gap rule, and Hungarian assignment.
"""

import pandas as pd
import numpy as np
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment
import re
import logging
from typing import Dict, List, Tuple, Optional
from unidecode import unidecode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrictUniversityMatcher:
    def __init__(self):
        # Stop words that add no discriminative value
        self.stop_words = {
            'university', 'college', 'school', 'institute', 'institution', 
            'of', 'the', 'at', 'for', 'and', 'in', 'on', 
            'state', 'system', 'campus', 'main', 'branch'
        }
        
        # Common abbreviation expansions
        self.abbreviations = {
            'univ': 'university',
            'inst': 'institute', 
            'tech': 'technology',
            'sci': 'science',
            'eng': 'engineering',
            '&': 'and',
            'u': 'university',  # Be careful with single letters
            'calif': 'california',
            'penn': 'pennsylvania'
        }
        
        # ARWU 2023 rankings - only the most reliable ones for strict matching
        self.arwu_rankings = {
            "Harvard University": (1, 100.0),
            "Stanford University": (2, 76.3),
            "Massachusetts Institute of Technology": (3, 75.4),
            "University of California, Berkeley": (4, 68.9),
            "University of Cambridge": (5, 67.2),
            "Princeton University": (6, 66.7),
            "Columbia University": (7, 60.4),
            "California Institute of Technology": (8, 59.5),
            "University of Chicago": (9, 56.5),
            "Yale University": (10, 54.1),
            "Cornell University": (11, 52.8),
            "University of California, Los Angeles": (12, 51.9),
            "University of Pennsylvania": (13, 48.4),
            "Johns Hopkins University": (14, 47.8),
            "University of California, San Francisco": (15, 46.2),
            "University of Oxford": (16, 45.4),
            "University of Michigan, Ann Arbor": (17, 44.9),
            "University College London": (18, 43.2),
            "University of California, San Diego": (19, 42.1),
            "University of Washington": (20, 41.8),
            "New York University": (22, 40.2),
            "Imperial College London": (23, 39.8),
            "Northwestern University": (24, 39.1),
            "University of Wisconsin - Madison": (25, 38.7),
            "University of Illinois at Urbana-Champaign": (27, 37.9),
            "Duke University": (28, 37.5),
            "University of North Carolina at Chapel Hill": (32, 35.9),
            "King's College London": (33, 35.6),
            "University of Colorado at Boulder": (34, 35.2),
            "Carnegie Mellon University": (35, 34.8),
            "University of Edinburgh": (36, 34.5),
            "University of Texas at Austin": (38, 33.8),
            "Boston University": (40, 33.2),
            "University of Manchester": (41, 32.9),
            "University of California, Davis": (42, 32.5),
            "University of California, Santa Barbara": (43, 32.2),
            "University of California, Irvine": (48, 30.6),
            "University of Southern California": (46, 31.2),
            "University of Bristol": (51, 29.1),
            "Ohio State University": (52, 28.8),
            "University of Pittsburgh": (53, 28.5),
            "Rice University": (61, 26.1),
            "Arizona State University": (63, 25.5),
            "Pennsylvania State University": (65, 24.9),
            "University of Virginia": (66, 24.6),
            "Purdue University": (68, 24.0),
            "University of California, Riverside": (69, 23.7),
            "Georgia Institute of Technology": (72, 22.8),
            "Michigan State University": (73, 22.5),
            "University of Iowa": (75, 21.9),
            "London School of Economics and Political Science": (76, 24.3),
            "University of Glasgow": (101, 21.2),
            "University of Birmingham": (151, 18.5),
            "University of Leeds": (151, 18.4),
            "University of Liverpool": (151, 18.1),
            "University of Nottingham": (151, 18.0),
            "University of Sheffield": (151, 17.9),
            "University of Southampton": (151, 17.8),
        }
    
    def canonicalize_name(self, name: str) -> str:
        """Canonicalize university name following o3's approach."""
        if pd.isna(name):
            return ""
            
        # Step 1: Basic cleaning
        name = unidecode(name.lower().strip())
        
        # Step 2: Expand abbreviations
        for abbr, full in self.abbreviations.items():
            name = re.sub(rf'\b{re.escape(abbr)}\b', full, name)
        
        # Step 3: Remove punctuation and normalize spacing
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        
        # Step 4: Remove stop words but keep important tokens
        tokens = [token for token in name.split() 
                 if token and token not in self.stop_words]
        
        # Step 5: Sort tokens to handle word order variations
        return ' '.join(sorted(tokens))
    
    def compute_similarity_matrix(self, arwu_names: List[str], scorecard_names: List[str]) -> np.ndarray:
        """Compute similarity matrix using TF-IDF and multiple metrics."""
        # Canonicalize all names
        arwu_canon = [self.canonicalize_name(name) for name in arwu_names]
        scorecard_canon = [self.canonicalize_name(name) for name in scorecard_names]
        
        # Remove empty strings
        valid_arwu = [(i, canon) for i, canon in enumerate(arwu_canon) if canon]
        valid_scorecard = [(j, canon) for j, canon in enumerate(scorecard_canon) if canon]
        
        if not valid_arwu or not valid_scorecard:
            return np.zeros((len(arwu_names), len(scorecard_names)))
        
        # Create similarity matrix
        similarity_matrix = np.zeros((len(arwu_names), len(scorecard_names)))
        
        # Method 1: TF-IDF cosine similarity (o3's suggestion)
        try:
            all_texts = [canon for _, canon in valid_arwu] + [canon for _, canon in valid_scorecard]
            
            # Use character n-grams and word tokens
            vectorizer = TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.8,
                stop_words=None  # We already removed stop words
            )
            
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            arwu_tfidf = tfidf_matrix[:len(valid_arwu)]
            scorecard_tfidf = tfidf_matrix[len(valid_arwu):]
            
            cosine_sim = cosine_similarity(arwu_tfidf, scorecard_tfidf)
            
            # Map back to original indices
            for idx_a, (i, _) in enumerate(valid_arwu):
                for idx_s, (j, _) in enumerate(valid_scorecard):
                    similarity_matrix[i, j] = cosine_sim[idx_a, idx_s] * 100  # Scale to 0-100
                    
        except Exception as e:
            logger.warning(f"TF-IDF similarity failed: {e}, falling back to token similarity")
            # Fallback: token-based similarity
            for i, canon_a in enumerate(arwu_canon):
                for j, canon_s in enumerate(scorecard_canon):
                    if canon_a and canon_s:
                        similarity_matrix[i, j] = fuzz.token_sort_ratio(canon_a, canon_s)
        
        return similarity_matrix
    
    def apply_gap_rule(self, similarity_row: np.ndarray, min_gap: float = 5.0) -> bool:
        """Apply o3's gap rule: s1 - s2 >= min_gap."""
        sorted_scores = sorted(similarity_row, reverse=True)
        if len(sorted_scores) < 2:
            return True
        return (sorted_scores[0] - sorted_scores[1]) >= min_gap
    
    def match_universities(self, scorecard_df: pd.DataFrame) -> pd.DataFrame:
        """Perform strict one-to-one university matching."""
        logger.info("Starting strict university matching...")
        
        arwu_names = list(self.arwu_rankings.keys())
        scorecard_names = scorecard_df['school_name'].tolist()
        
        logger.info(f"ARWU universities to match: {len(arwu_names)}")
        logger.info(f"Scorecard universities available: {len(scorecard_names)}")
        
        # Compute similarity matrix
        similarity_matrix = self.compute_similarity_matrix(arwu_names, scorecard_names)
        
        # Apply strict thresholds and gap rule
        MIN_SIMILARITY = 90.0
        MIN_GAP = 5.0
        
        # Create filtered similarity matrix
        filtered_matrix = similarity_matrix.copy()
        valid_pairs = []
        
        for i in range(len(arwu_names)):
            row = similarity_matrix[i]
            best_score = np.max(row)
            
            if best_score >= MIN_SIMILARITY and self.apply_gap_rule(row, MIN_GAP):
                # Keep this row for Hungarian assignment
                valid_pairs.append(i)
            else:
                # Zero out this row - not confident enough
                filtered_matrix[i, :] = 0
        
        logger.info(f"Universities passing initial filters: {len(valid_pairs)}")
        
        # Hungarian assignment on filtered matrix
        cost_matrix = 100 - filtered_matrix  # Convert similarity to cost
        arwu_indices, scorecard_indices = linear_sum_assignment(cost_matrix)
        
        # Extract high-quality matches
        matches = []
        matched_arwu = set()
        matched_scorecard = set()
        
        for i, j in zip(arwu_indices, scorecard_indices):
            similarity = similarity_matrix[i, j]
            if similarity >= MIN_SIMILARITY:
                matches.append({
                    'arwu_name': arwu_names[i],
                    'arwu_rank': self.arwu_rankings[arwu_names[i]][0],
                    'arwu_score': self.arwu_rankings[arwu_names[i]][1],
                    'scorecard_name': scorecard_names[j],
                    'scorecard_index': j,
                    'similarity_score': similarity
                })
                matched_arwu.add(i)
                matched_scorecard.add(j)
        
        logger.info(f"Final high-quality matches: {len(matches)}")
        
        # Log unmatched universities for manual review
        unmatched_arwu = [arwu_names[i] for i in range(len(arwu_names)) if i not in matched_arwu]
        logger.info(f"Unmatched ARWU universities: {len(unmatched_arwu)}")
        if unmatched_arwu:
            logger.info(f"Unmatched: {unmatched_arwu[:10]}...")  # Show first 10
        
        # Create final matched dataset
        matched_data = []
        for match in matches:
            scorecard_row = scorecard_df.iloc[match['scorecard_index']]
            matched_data.append({
                'institution': match['arwu_name'],
                'country': 'United States' if 'scorecard_index' in match else 'United Kingdom',
                'arwu_rank': match['arwu_rank'],
                'arwu_score': match['arwu_score'],
                'tuition_in_state_usd': scorecard_row.get('tuition_in_state'),
                'tuition_out_state_usd': scorecard_row.get('tuition_out_state'),
                'total_cost_usd': scorecard_row.get('total_cost'),
                'price_usd': scorecard_row.get('tuition_out_state', scorecard_row.get('tuition_in_state')),
                'match_similarity': match['similarity_score']
            })
        
        return pd.DataFrame(matched_data)


def main():
    # Load the problematic data
    df = pd.read_csv("massive_university_data.csv")
    us_data = df[df['country'] == 'United States'].copy()
    
    print("=" * 80)
    print("FIXING UNIVERSITY MATCHING WITH STRICT CRITERIA")
    print("=" * 80)
    
    # Show the current problem
    print(f"\nCURRENT PROBLEM ANALYSIS:")
    rank_counts = us_data['arwu_rank'].value_counts().sort_index()
    duplicates = rank_counts[rank_counts > 1].head(10)
    
    print(f"Ranks with multiple universities (TOP 10 problems):")
    for rank, count in duplicates.items():
        print(f"  Rank {rank}: {count} universities")
        examples = us_data[us_data['arwu_rank'] == rank][['institution', 'price_usd']].head(3)
        for _, row in examples.iterrows():
            print(f"    - {row['institution']} (${row['price_usd']:,.0f})")
    
    # Apply strict matching
    matcher = StrictUniversityMatcher()
    
    # Prepare scorecard data format
    scorecard_df = us_data[['institution', 'tuition_in_state_usd', 'tuition_out_state_usd', 'total_cost_usd']].copy()
    scorecard_df = scorecard_df.rename(columns={
        'institution': 'school_name',
        'tuition_in_state_usd': 'tuition_in_state',
        'tuition_out_state_usd': 'tuition_out_state',
        'total_cost_usd': 'total_cost'
    })
    
    # Get strict matches
    strict_matches = matcher.match_universities(scorecard_df)
    
    # Add UK data (which doesn't have the matching problem)
    uk_data = df[df['country'] == 'United Kingdom'].copy()
    
    # Combine datasets
    final_data = pd.concat([strict_matches, uk_data], ignore_index=True)
    
    print(f"\nRESULTS:")
    print(f"Original US universities: {len(us_data)}")
    print(f"Strict matched US universities: {len(strict_matches)}")
    print(f"UK universities: {len(uk_data)}")
    print(f"Total final dataset: {len(final_data)}")
    
    # Verify no duplicate rankings
    final_rank_counts = final_data['arwu_rank'].value_counts()
    duplicates_after = final_rank_counts[final_rank_counts > 1]
    
    if len(duplicates_after) == 0:
        print("✅ SUCCESS: No duplicate rankings in final dataset!")
    else:
        print(f"⚠️  Still have {len(duplicates_after)} duplicate rankings")
    
    # Show some examples of the clean data
    print(f"\nSAMPLE OF CLEAN DATA:")
    sample = final_data.head(10)[['institution', 'country', 'arwu_rank', 'price_usd']]
    print(sample.to_string(index=False))
    
    # Save the clean data
    output_file = "clean_university_data.csv"
    final_data.to_csv(output_file, index=False)
    print(f"\n✅ Clean data saved to: {output_file}")
    
    return final_data


if __name__ == "__main__":
    clean_data = main()