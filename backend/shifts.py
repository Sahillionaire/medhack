from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Optional
import os

from solver.shift_recommender import (
    ShiftRecommender, 
    StaffProfile, 
    Shift, 
    StaffRecommendation
)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/shifts")
def get_shifts():
    """Get all shifts"""
    response = supabase.table("shift").select("*").execute()
    return response.data


@app.get("/api/shift/{shift_id}/recommendations")
def get_shift_recommendations(shift_id: int, top_n: int = 5):
    """
    Get top N staff recommendations for a specific shift based on burnout levels
    and workload considerations.
    
    Args:
        shift_id: ID of the shift to get recommendations for
        top_n: Number of top recommendations to return (default: 5)
    
    Returns:
        List of staff recommendations with suitability scores
    """
    try:
        # Fetch shift details
        shift_response = supabase.table("shift").select(
            "*, department(department_name)"
        ).eq("shift_id", shift_id).execute()
        
        if not shift_response.data:
            raise HTTPException(status_code=404, detail="Shift not found")
        
        shift_data = shift_response.data[0]
        
        # Create Shift object
        shift = Shift(
            shift_id=shift_data['shift_id'],
            department_id=shift_data['department_id'],
            shift_start=datetime.fromisoformat(shift_data['shift_start'].replace('Z', '+00:00')),
            shift_end=datetime.fromisoformat(shift_data['shift_end'].replace('Z', '+00:00')),
            shift_type=shift_data['shift_type'],
            patient_ratio_score=shift_data.get('patient_ratio_score'),
            spontaneity_score=shift_data.get('spontaneity_score')
        )
        
        department_name = shift_data['department']['department_name'] if shift_data.get('department') else None
        
        # Fetch all active staff
        staff_list = _fetch_staff_profiles()
        
        # Get recommendations
        recommender = ShiftRecommender()
        recommendations = recommender.recommend_top_staff(
            staff_list, 
            shift, 
            department_name,
            top_n
        )
        
        # Format response
        return {
            "shift_id": shift_id,
            "shift_start": shift_data['shift_start'],
            "shift_type": shift_data['shift_type'],
            "department": department_name,
            "recommendations": [
                {
                    "staff_id": rec.staff_id,
                    "staff_name": rec.staff_name,
                    "suitability_score": round(rec.suitability_score, 2),
                    "score_breakdown": {k: round(v, 2) for k, v in rec.breakdown.items()},
                    "warnings": rec.warnings
                }
                for rec in recommendations
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/staff/{staff_id}/profile")
def get_staff_profile(staff_id: int):
    """
    Get complete staff profile including wellness and workload data
    """
    try:
        profile = _fetch_single_staff_profile(staff_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Staff member not found")
        
        return {
            "staff_id": profile.staff_id,
            "name": f"{profile.first_name} {profile.last_name}",
            "status": profile.status,
            "hire_date": profile.hire_date.isoformat(),
            "primary_department_id": profile.primary_department_id,
            "wellness": {
                "fatigue_score": profile.fatigue_score,
                "stress_score": profile.stress_score,
                "burnout_risk_level": profile.burnout_risk_level
            },
            "workload": {
                "total_hours": profile.total_hours,
                "night_shifts": profile.night_shifts,
                "consecutive_days": profile.consecutive_days,
                "overtime_hours": profile.overtime_hours
            },
            "recent_incident": {
                "severity": profile.recent_incident_severity,
                "emotional_weight": profile.recent_incident_weight,
                "days_since": profile.days_since_incident
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _fetch_staff_profiles() -> List[StaffProfile]:
    """
    Fetch all staff profiles with wellness, workload, and incident data
    """
    staff_list = []
    
    # Fetch staff with department info
    staff_response = supabase.table("staff").select("*").execute()
    
    for staff_data in staff_response.data:
        staff_id = staff_data['staff_id']
        
        # Fetch most recent wellness score
        wellness_response = supabase.table("wellness_score").select("*").eq(
            "staff_id", staff_id
        ).order("date_recorded", desc=True).limit(1).execute()
        
        wellness = wellness_response.data[0] if wellness_response.data else {}
        
        # Fetch most recent workload record (current week)
        # Get the start of the current week
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        workload_response = supabase.table("workload_record").select("*").eq(
            "staff_id", staff_id
        ).order("week_start_date", desc=True).limit(1).execute()
        
        workload = workload_response.data[0] if workload_response.data else {}
        
        # Fetch most recent incident exposure
        incident_response = supabase.table("incident_exposure").select("*").eq(
            "staff_id", staff_id
        ).order("recorded_at", desc=True).limit(1).execute()
        
        incident = incident_response.data[0] if incident_response.data else {}
        
        # Calculate days since incident
        days_since_incident = None
        if incident.get('recorded_at'):
            incident_date = datetime.fromisoformat(incident['recorded_at'].replace('Z', '+00:00'))
            days_since_incident = (datetime.now(incident_date.tzinfo) - incident_date).days
        
        # Create StaffProfile object
        profile = StaffProfile(
            staff_id=staff_id,
            first_name=staff_data['first_name'],
            last_name=staff_data['last_name'],
            status=staff_data['status'],
            hire_date=datetime.fromisoformat(staff_data['hire_date']) if staff_data.get('hire_date') else datetime.now(),
            primary_department_id=staff_data['primary_department_id'],
            role_id=staff_data['role_id'],
            fatigue_score=wellness.get('fatigue_score'),
            stress_score=wellness.get('stress_score'),
            burnout_risk_level=wellness.get('burnout_risk_level'),
            total_hours=float(workload.get('total_hours')) if workload.get('total_hours') else None,
            night_shifts=workload.get('night_shifts'),
            consecutive_days=workload.get('consecutive_days'),
            overtime_hours=float(workload.get('overtime_hours')) if workload.get('overtime_hours') else None,
            recent_incident_severity=incident.get('severity_level'),
            recent_incident_weight=float(incident.get('emotional_weight_score')) if incident.get('emotional_weight_score') else None,
            days_since_incident=days_since_incident
        )
        
        staff_list.append(profile)
    
    return staff_list


def _fetch_single_staff_profile(staff_id: int) -> Optional[StaffProfile]:
    """
    Fetch a single staff profile with all relevant data
    """
    profiles = _fetch_staff_profiles()
    for profile in profiles:
        if profile.staff_id == staff_id:
            return profile
    return None