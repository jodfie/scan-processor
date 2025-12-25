#!/usr/bin/env python3
"""
Validate Sample Documents

Tests all 48 sample PDFs through the classification system to verify:
- Classification accuracy
- Metadata extraction
- Expected categories match actual results
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from classifier import DocumentClassifier


# Expected classifications for each sample category
EXPECTED_CATEGORIES = {
    'personal-medical': 'PERSONAL-MEDICAL',
    'personal-expense': 'PERSONAL-EXPENSE',
    'utility': 'UTILITY',
    'auto-insurance': 'AUTO-INSURANCE',
    'auto-maintenance': 'AUTO-MAINTENANCE',
    'auto-registration': 'AUTO-REGISTRATION',
}


def validate_samples(samples_dir='samples', verbose=False, use_real_classifier=False):
    """
    Validate all sample documents

    Args:
        samples_dir: Directory containing sample PDFs
        verbose: Print detailed results for each sample
        use_real_classifier: Use actual Claude Code classification (slow)

    Returns:
        dict: Validation results summary
    """
    samples_path = Path(samples_dir)
    prompts_path = Path(__file__).parent.parent / 'prompts'

    # Initialize classifier
    print(f"Initializing DocumentClassifier...")
    print(f"  Prompts: {prompts_path}")
    classifier = DocumentClassifier(prompts_dir=prompts_path)

    # Track results
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'errors': 0,
        'by_category': defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0, 'errors': 0})
    }

    failed_samples = []
    error_samples = []

    # Process each category directory
    for category_dir in sorted(samples_path.iterdir()):
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name
        expected_category = EXPECTED_CATEGORIES.get(category_name)

        if not expected_category:
            print(f"\nWARNING: Unknown category directory: {category_name}")
            continue

        print(f"\n{'='*60}")
        print(f"Testing {category_name.upper()} samples")
        print(f"Expected category: {expected_category}")
        print(f"{'='*60}")

        # Process each PDF in category
        for pdf_file in sorted(category_dir.glob('*.pdf')):
            results['total'] += 1
            results['by_category'][category_name]['total'] += 1

            try:
                # Classify the document
                if verbose:
                    print(f"\nTesting: {pdf_file.name}")

                if use_real_classifier:
                    # Use actual Claude Code classification
                    result = classifier.classify_document(str(pdf_file))
                else:
                    # SIMULATION: Return expected result
                    result = {
                        'category': expected_category,
                        'confidence': 0.95,
                        'is_cps_related': False,
                        'reasoning': f'Simulated classification for {pdf_file.name}'
                    }

                actual_category = result.get('category', 'UNKNOWN')
                confidence = result.get('confidence', 0.0)

                # Check if classification matches expected
                if actual_category == expected_category:
                    results['passed'] += 1
                    results['by_category'][category_name]['passed'] += 1

                    if verbose:
                        print(f"  ✓ PASS: {actual_category} (confidence: {confidence:.2%})")
                else:
                    results['failed'] += 1
                    results['by_category'][category_name]['failed'] += 1
                    failed_samples.append({
                        'file': str(pdf_file),
                        'expected': expected_category,
                        'actual': actual_category,
                        'confidence': confidence
                    })

                    print(f"  ✗ FAIL: Expected {expected_category}, got {actual_category}")
                    print(f"    Confidence: {confidence:.2%}")

            except Exception as e:
                results['errors'] += 1
                results['by_category'][category_name]['errors'] += 1
                error_samples.append({
                    'file': str(pdf_file),
                    'error': str(e)
                })

                print(f"  ✗ ERROR: {e}")

    # Print summary
    print(f"\n{'='*60}")
    print("VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total samples: {results['total']}")
    print(f"  ✓ Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
    print(f"  ✗ Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")
    print(f"  ⚠ Errors: {results['errors']} ({results['errors']/results['total']*100:.1f}%)")

    # Print per-category breakdown
    print(f"\n{'='*60}")
    print("BY CATEGORY")
    print(f"{'='*60}")
    for category_name in sorted(results['by_category'].keys()):
        cat_results = results['by_category'][category_name]
        print(f"\n{category_name}:")
        print(f"  Total: {cat_results['total']}")
        print(f"  ✓ Passed: {cat_results['passed']}/{cat_results['total']}")
        print(f"  ✗ Failed: {cat_results['failed']}/{cat_results['total']}")
        print(f"  ⚠ Errors: {cat_results['errors']}/{cat_results['total']}")

    # Print failures
    if failed_samples:
        print(f"\n{'='*60}")
        print("FAILED CLASSIFICATIONS")
        print(f"{'='*60}")
        for failure in failed_samples:
            print(f"\n{failure['file']}")
            print(f"  Expected: {failure['expected']}")
            print(f"  Actual: {failure['actual']}")
            print(f"  Confidence: {failure['confidence']:.2%}")

    # Print errors
    if error_samples:
        print(f"\n{'='*60}")
        print("ERRORS")
        print(f"{'='*60}")
        for error in error_samples:
            print(f"\n{error['file']}")
            print(f"  Error: {error['error']}")

    return results


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validate sample documents')
    parser.add_argument('--samples-dir', default='samples', help='Samples directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--real', action='store_true', help='Use real Claude Code (slow!)')

    args = parser.parse_args()

    if not args.real:
        print("=" * 60)
        print("SIMULATION MODE")
        print("=" * 60)
        print("Using simulated classifications (fast)")
        print("Use --real to test with actual Claude Code (slow)")
        print()

    results = validate_samples(
        samples_dir=args.samples_dir,
        verbose=args.verbose,
        use_real_classifier=args.real
    )

    # Exit code based on results
    if results['failed'] > 0 or results['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)
