"""
Quick test script to see shift recommendations in action
Run this after starting the FastAPI server
"""

import requests
import json

# API base URL (adjust if your server runs on a different port)
BASE_URL = "http://localhost:8000"

def test_shift_recommendations():
    """Test the shift recommendation endpoint"""
    print("=" * 70)
    print("TESTING SHIFT RECOMMENDATIONS")
    print("=" * 70)
    
    # Get all shifts first
    print("\n1. Fetching available shifts...")
    try:
        response = requests.get(f"{BASE_URL}/api/shifts")
        shifts = response.json()
        
        if not shifts:
            print("❌ No shifts found in database. Please insert sample shifts first.")
            return
        
        print(f"✅ Found {len(shifts)} shifts")
        print("\nFirst few shifts:")
        for shift in shifts[:3]:
            print(f"  - Shift ID {shift['shift_id']}: {shift['shift_type']} shift at {shift['shift_start']}")
    
    except Exception as e:
        print(f"❌ Error fetching shifts: {e}")
        print("Is the server running? Start it with: uvicorn shifts:app --reload")
        return
    
    # Get recommendations for the first shift
    shift_id = shifts[0]['shift_id']
    print(f"\n2. Getting top 5 staff recommendations for Shift #{shift_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/shift/{shift_id}/recommendations?top_n=5")
        data = response.json()
        
        print(f"\n✅ Recommendations for {data['shift_type']} shift on {data['shift_start']}")
        print(f"   Department: {data.get('department', 'N/A')}")
        print("\n" + "=" * 70)
        print("TOP STAFF RECOMMENDATIONS")
        print("=" * 70)
        
        for i, rec in enumerate(data['recommendations'], 1):
            print(f"\n{i}. {rec['staff_name']} (ID: {rec['staff_id']})")
            print(f"   Suitability Score: {rec['suitability_score']:.2f}")
            print(f"   Score Breakdown:")
            for component, score in rec['score_breakdown'].items():
                emoji = "✅" if score >= 0 else "⚠️"
                print(f"      {emoji} {component}: {score:+.2f}")
            
            if rec['warnings']:
                print(f"   ⚠️  Warnings:")
                for warning in rec['warnings']:
                    print(f"      - {warning}")
            else:
                print(f"   ✅ No warnings - good candidate!")
        
        print("\n" + "=" * 70)
        print("RECOMMENDATION SUMMARY")
        print("=" * 70)
        
        best = data['recommendations'][0]
        print(f"🏆 Best choice: {best['staff_name']} (Score: {best['suitability_score']:.2f})")
        
        if best['warnings']:
            print(f"   Note: This staff member has some concerns, but is the best available.")
        else:
            print(f"   This staff member is well-rested and suitable for the shift!")
    
    except Exception as e:
        print(f"❌ Error getting recommendations: {e}")

def test_staff_profile():
    """Test the staff profile endpoint"""
    print("\n\n" + "=" * 70)
    print("TESTING STAFF PROFILE")
    print("=" * 70)
    
    staff_id = 1
    print(f"\nFetching profile for staff member #{staff_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/staff/{staff_id}/profile")
        
        if response.status_code == 404:
            print(f"❌ Staff member #{staff_id} not found. Try a different ID.")
            return
        
        profile = response.json()
        
        print(f"\n✅ Profile for {profile['name']}")
        print(f"   Status: {profile['status']}")
        print(f"   Hire Date: {profile['hire_date']}")
        print(f"\n   Wellness Scores:")
        print(f"      Fatigue: {profile['wellness']['fatigue_score']}/10")
        print(f"      Stress: {profile['wellness']['stress_score']}/10")
        print(f"      Burnout Risk: {profile['wellness']['burnout_risk_level']}")
        print(f"\n   Workload (Current Week):")
        print(f"      Total Hours: {profile['workload']['total_hours']}")
        print(f"      Night Shifts: {profile['workload']['night_shifts']}")
        print(f"      Consecutive Days: {profile['workload']['consecutive_days']}")
        print(f"      Overtime Hours: {profile['workload']['overtime_hours']}")
        
        if profile['recent_incident']['severity']:
            print(f"\n   Recent Incident:")
            print(f"      Severity: {profile['recent_incident']['severity']}")
            print(f"      Days Since: {profile['recent_incident']['days_since']}")
    
    except Exception as e:
        print(f"❌ Error getting staff profile: {e}")

if __name__ == "__main__":
    print("\n🏥 SHIFT RECOMMENDATION SYSTEM - TEST SCRIPT 🏥\n")
    
    # Test recommendations
    test_shift_recommendations()
    
    # Test staff profile
    test_staff_profile()
    
    print("\n\n" + "=" * 70)
    print("✅ Testing Complete!")
    print("=" * 70)
    print("\nTo test with different shifts, use:")
    print(f"  GET {BASE_URL}/api/shift/{{shift_id}}/recommendations?top_n=5")
    print("\nTo view different staff profiles, use:")
    print(f"  GET {BASE_URL}/api/staff/{{staff_id}}/profile")
    print()
