"""
Simple demo to view shift recommendations
"""

import requests
import json

print("\n🏥 SHIFT RECOMMENDATION DEMO 🏥\n")
print("Server: http://127.0.0.1:8000\n")
print("=" * 70)

# Test 1: Get recommendations
print("\n📋 GETTING RECOMMENDATIONS FOR SHIFT #1...\n")

try:
    response = requests.get("http://127.0.0.1:8000/api/shift/1/recommendations?top_n=5", timeout=10)
    data = response.json()
    
    print(f"Shift: {data['shift_type']} shift on {data['shift_start']}")
    print(f"Department: {data.get('department', 'N/A')}\n")
    print("=" * 70)
    print("TOP 5 STAFF RECOMMENDATIONS")
    print("=" * 70)
    
    for i, rec in enumerate(data['recommendations'], 1):
        print(f"\n{i}. {rec['staff_name']} (ID: {rec['staff_id']})")
        print(f"   ⭐ Suitability Score: {rec['suitability_score']:.1f}")
        
        if rec['warnings']:
            print(f"   ⚠️  Warnings: {', '.join(rec['warnings'])}")
        else:
            print(f"   ✅ Good candidate - no warnings!")
    
    print("\n" + "=" * 70)
    print(f"🏆 BEST CHOICE: {data['recommendations'][0]['staff_name']}")
    print(f"   Score: {data['recommendations'][0]['suitability_score']:.1f}")
    print("=" * 70)
    
except requests.exceptions.Timeout:
    print("❌ Request timed out. Is the server running?")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server. Make sure it's running at http://127.0.0.1:8000")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n\n📌 To view in browser:")
print("   http://127.0.0.1:8000/api/shift/1/recommendations?top_n=5")
print("\n📌 To view all shifts:")
print("   http://127.0.0.1:8000/api/shifts")
print()
