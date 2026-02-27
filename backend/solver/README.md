# Shift Recommendation Algorithm

## Overview

This algorithm recommends the most suitable staff members for shifts based on comprehensive burnout and workload analysis. It prevents staff overwork by considering multiple factors including wellness scores, recent workload, incident exposure, and department preferences.

## How It Works

### Scoring System

Each staff member receives a **suitability score** for a given shift. Higher scores indicate better suitability.

The algorithm considers these factors:

#### 1. **Availability (Critical)** - Weight: 100
- Staff must have `ACTIVE` status
- If not available, score = 0 (cannot be assigned)

#### 2. **Department Match** - Weight: 20
- **Bonus**: +20 points if shift department matches staff's primary department
- **Penalty**: -5 points if working outside primary department
- Ensures staff work in familiar environments where they're most effective

#### 3. **Wellness Score** - Weight: 30
Penalizes poor mental/physical health indicators:
- **Fatigue Score** (1-10): Higher fatigue = lower suitability
- **Stress Score** (1-10): Higher stress = lower suitability
- **Burnout Risk Level**: 
  - HIGH: -45 points
  - MEDIUM: -21 points
  - LOW: No penalty

#### 4. **Workload** - Weight: 25
Penalizes recent overwork:
- **Total Hours**: 
  - >50 hours/week: -25 points
  - >40 hours/week: -12.5 points
  - <30 hours/week: +7.5 points (bonus)
- **Night Shifts**:
  - ≥4 night shifts: -20 points
  - ≥3 night shifts: -12.5 points
  - ≥2 night shifts: -5 points
- **Consecutive Days**:
  - ≥6 days: -30 points (urgent rest needed)
  - ≥4 days: -15 points
  - ≥3 days: -7.5 points
- **Overtime Hours**: Scaled penalty up to -25 points

#### 5. **Incident Exposure** - Weight: 15
Penalizes recent traumatic incidents:
- **Severity**: HIGH > MEDIUM > LOW (1.5x, 1.0x, 0.5x multiplier)
- **Recency**: Exponential decay (30-day half-life)
  - Recent incidents have higher impact
  - Impact diminishes over time
- **Emotional Weight**: 0-10 scale from incident report

Formula: `penalty = weight × severity_multiplier × recency_factor × emotional_factor`

#### 6. **Experience** - Weight: 5
Small bonus for tenure:
- More experienced staff get slight preference (up to +5 points)
- Caps at 5 years of service
- Recognizes that experience helps with stress management

#### 7. **Shift Type** - Weight: 10
Considers night shift fatigue:
- If night shift AND staff has worked ≥3 night shifts recently: -8 points
- If night shift AND staff has worked ≥2 night shifts recently: -4 points

### Score Calculation

```
Total Score = 50 (base) + Σ(component scores)
Minimum Score = 0
```

## API Usage

### Get Shift Recommendations

**Endpoint**: `GET /api/shift/{shift_id}/recommendations?top_n=5`

**Description**: Returns top N staff recommendations for a specific shift

**Response**:
```json
{
  "shift_id": 1,
  "shift_start": "2026-03-01T08:00:00Z",
  "shift_type": "DAY",
  "department": "ED",
  "recommendations": [
    {
      "staff_id": 5,
      "staff_name": "Jane Smith",
      "suitability_score": 78.50,
      "score_breakdown": {
        "availability": 100.0,
        "department_match": 20.0,
        "wellness": -9.0,
        "workload": 7.5,
        "incident": -2.3,
        "experience": 4.0,
        "shift_type": 0.0
      },
      "warnings": []
    },
    {
      "staff_id": 12,
      "staff_name": "John Doe",
      "suitability_score": 45.20,
      "score_breakdown": {
        "availability": 100.0,
        "department_match": 20.0,
        "wellness": -30.0,
        "workload": -25.0,
        "incident": -15.0,
        "experience": 2.0,
        "shift_type": -8.0
      },
      "warnings": [
        "High burnout risk or poor wellness scores",
        "High recent workload",
        "Recent high-severity incident exposure",
        "Already worked many night shifts recently"
      ]
    }
  ]
}
```

### Get Staff Profile

**Endpoint**: `GET /api/staff/{staff_id}/profile`

**Description**: Get complete staff profile with wellness and workload data

**Response**:
```json
{
  "staff_id": 5,
  "name": "Jane Smith",
  "status": "ACTIVE",
  "hire_date": "2020-03-15",
  "primary_department_id": 1,
  "wellness": {
    "fatigue_score": 3,
    "stress_score": 4,
    "burnout_risk_level": "LOW"
  },
  "workload": {
    "total_hours": 35.0,
    "night_shifts": 1,
    "consecutive_days": 2,
    "overtime_hours": 0.0
  },
  "recent_incident": {
    "severity": null,
    "emotional_weight": null,
    "days_since": null
  }
}
```

## Python Usage

```python
from solver.shift_recommender import ShiftRecommender, StaffProfile, Shift
from datetime import datetime

# Create staff profiles
staff = StaffProfile(
    staff_id=1,
    first_name="Jane",
    last_name="Doe",
    status="ACTIVE",
    hire_date=datetime(2020, 1, 15),
    primary_department_id=1,
    role_id=1,
    fatigue_score=3,
    stress_score=4,
    burnout_risk_level="LOW",
    total_hours=35.0,
    night_shifts=1,
    consecutive_days=2,
    overtime_hours=0.0
)

# Define shift
shift = Shift(
    shift_id=1,
    department_id=1,
    shift_start=datetime(2026, 3, 1, 8, 0),
    shift_end=datetime(2026, 3, 1, 16, 0),
    shift_type="DAY"
)

# Get recommendation
recommender = ShiftRecommender()
recommendation = recommender.calculate_suitability_score(staff, shift, "ED")

print(f"Suitability Score: {recommendation.suitability_score}")
print(f"Warnings: {recommendation.warnings}")
```

## Key Features

✅ **Burnout Prevention**: Heavily penalizes overworked staff  
✅ **Wellness Priority**: Considers mental health and fatigue  
✅ **Incident Awareness**: Accounts for traumatic event exposure  
✅ **Department Matching**: Prefers staff in their primary department  
✅ **Recency Weighting**: Recent data has more impact than old data  
✅ **Transparent Scoring**: Full breakdown of score components  
✅ **Warning System**: Highlights concerning patterns  

## Customization

You can adjust the weights in the `ShiftRecommender.WEIGHTS` dictionary:

```python
WEIGHTS = {
    'department_match': 20.0,
    'availability': 100.0,
    'wellness': 30.0,
    'workload': 25.0,
    'incident': 15.0,
    'experience': 5.0,
    'shift_type': 10.0,
}
```

Increase weights to make certain factors more important in the final score.

## Implementation Notes

- **Data Sources**: 
  - `staff` table: Basic info, hire date, department
  - `wellness_score` table: Fatigue, stress, burnout risk
  - `workload_record` table: Hours, night shifts, consecutive days, overtime
  - `incident_exposure` table: Severity, emotional impact, timing

- **Recency**: Algorithm uses most recent records for wellness, workload, and incidents

- **Time Zones**: All timestamps should be timezone-aware for accurate calculations

- **Missing Data**: Algorithm gracefully handles missing data by skipping penalties/bonuses for unavailable metrics

## Future Enhancements

Potential improvements:
- Machine learning to optimize weights based on historical outcomes
- Predict future burnout risk based on assignment patterns
- Consider leave requests and availability windows
- Factor in shift preferences and swap requests
- Multi-shift optimization (assign entire week at once)
