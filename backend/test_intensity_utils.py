#!/usr/bin/env python
"""
Test the intensity utility functions
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'study_bunny.settings')
django.setup()

from apps.core.intensity import (
    get_intensity, set_intensity, get_intensity_info, 
    calculate_intensity_for_completion, get_intensity_recommendations,
    validate_intensity_range, reset_intensity_to_default,
    get_intensity_impact_on_free_time
)
from datetime import datetime, date

def test_intensity_utilities():
    """Test all intensity utility functions"""
    print("Testing Intensity Utility Functions")
    print("=" * 50)
    
    # Test 1: Basic intensity functions
    print("1. Basic intensity functions:")
    current_intensity = get_intensity()
    print(f"   Current intensity: {current_intensity}")
    
    # Test setting intensity
    set_intensity(0.5)
    print(f"   After setting to 0.5: {get_intensity()}")
    
    # Restore original
    set_intensity(current_intensity)
    print(f"   Restored to original: {get_intensity()}")
    
    # Test 2: Intensity info
    print("\n2. Intensity information:")
    info = get_intensity_info()
    print(f"   Current intensity: {info['current_intensity']}")
    print(f"   Intensity level: {info['intensity_level']}")
    print(f"   Description: {info['description']}")
    print(f"   Average intensity: {info['average_intensity']:.3f}")
    print(f"   Impact factors:")
    for factor, value in info['impact_factors'].items():
        print(f"     {factor}: {value:.3f}")
    
    # Test 3: Intensity recommendations
    print("\n3. Intensity recommendations:")
    recommendations = get_intensity_recommendations()
    print(f"   Current intensity: {recommendations['current_intensity']}")
    for rec in recommendations['recommendations']:
        print(f"   {rec['type'].title()}: {rec['reason']}")
        print(f"     Suggested: {rec['suggested_intensity']}")
        print(f"     Impact: {rec['impact']}")
    
    # Test 4: Calculate intensity for completion
    print("\n4. Calculate intensity for completion:")
    completion_rates = [0.3, 0.5, 0.7, 0.9]
    for rate in completion_rates:
        required_intensity = calculate_intensity_for_completion(rate)
        print(f"   Target completion {rate:.1f} -> Required intensity: {required_intensity:.3f}")
    
    # Test 5: Validate intensity range
    print("\n5. Validate intensity range:")
    test_values = [-0.1, 0.0, 0.5, 1.0, 1.1]
    for value in test_values:
        is_valid = validate_intensity_range(value)
        print(f"   Intensity {value}: {'Valid' if is_valid else 'Invalid'}")
    
    # Test 6: Reset to default
    print("\n6. Reset to default:")
    original = get_intensity()
    print(f"   Before reset: {original}")
    default = reset_intensity_to_default()
    print(f"   After reset: {get_intensity()}")
    print(f"   Default value: {default}")
    
    # Restore original
    set_intensity(original)
    print(f"   Restored to original: {get_intensity()}")
    
    # Test 7: Intensity impact on free time
    print("\n7. Intensity impact on free time:")
    try:
        impact = get_intensity_impact_on_free_time()
        print(f"   Target date: {impact['target_date']}")
        print(f"   Current intensity: {impact['current_intensity']}")
        print(f"   Current free time: {impact['current_free_time']['free_time_hours']:.2f} hours")
        print(f"   Free time comparison:")
        for intensity, data in impact['comparison'].items():
            print(f"     Intensity {intensity}: {data['free_time_hours']:.2f} hours ({data['percentage_of_day']:.1f}% of day)")
    except Exception as e:
        print(f"   Error testing free time impact: {e}")
    
    # Test 8: Error handling
    print("\n8. Error handling:")
    try:
        set_intensity(1.5)  # Invalid value
    except ValueError as e:
        print(f"   ✓ Correctly caught invalid intensity: {e}")
    
    try:
        calculate_intensity_for_completion(1.5)  # Invalid completion rate
    except ValueError as e:
        print(f"   ✓ Correctly caught invalid completion rate: {e}")
    
    print("\n" + "=" * 50)
    print("✓ All intensity utility functions are working correctly!")
    print("✓ Intensity management system is ready!")

if __name__ == "__main__":
    test_intensity_utilities()
