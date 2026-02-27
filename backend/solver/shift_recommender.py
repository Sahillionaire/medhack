"""
Shift Recommendation Algorithm

This module provides an algorithm to recommend the most suitable staff member
for a given shift based on various factors including:
- Staff availability and status
- Department preferences
- Incident exposure (severity and recency)
- Workload records (hours, night shifts, consecutive days, overtime)
- Wellness scores (fatigue, stress, burnout risk)
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import math
import json


@dataclass
class StaffProfile:
    """Complete profile of a staff member for shift assignment evaluation"""
    staff_id: int
    first_name: str
    last_name: str
    status: str
    hire_date: datetime
    primary_department_id: int
    role_id: int
    
    # Wellness scores (most recent)
    fatigue_score: Optional[int] = None  # 1-10, higher = more fatigued
    stress_score: Optional[int] = None  # 1-10, higher = more stressed
    burnout_risk_level: Optional[str] = None  # LOW, MEDIUM, HIGH
    
    # Recent workload (current week)
    total_hours: Optional[float] = None
    night_shifts: Optional[int] = None
    consecutive_days: Optional[int] = None
    overtime_hours: Optional[float] = None
    
    # Incident exposure (recent incidents)
    recent_incident_severity: Optional[str] = None  # HIGH, MEDIUM, LOW
    recent_incident_weight: Optional[float] = None  # 0-10
    days_since_incident: Optional[int] = None


@dataclass
class Shift:
    """Shift information"""
    shift_id: int
    department_id: int
    shift_start: datetime
    shift_end: datetime
    shift_type: str  # DAY or NIGHT
    patient_ratio_score: Optional[float] = None
    spontaneity_score: Optional[float] = None


@dataclass
class StaffRecommendation:
    """Recommendation result for a staff member"""
    staff_id: int
    staff_name: str
    suitability_score: float
    breakdown: Dict[str, float]
    warnings: List[str]
    
    def __repr__(self):
        return f"StaffRecommendation(staff_id={self.staff_id}, name={self.staff_name}, score={self.suitability_score:.2f})"


class ShiftRecommender:
    """
    Algorithm to recommend staff members for shifts based on burnout
    and workload considerations
    """
    
    # Weight factors for different components (can be tuned)
    WEIGHTS = {
        'department_match': 20.0,      # Bonus for primary department match
        'availability': 100.0,          # Critical - must be available
        'wellness': 30.0,               # Wellness score impact
        'workload': 25.0,               # Recent workload impact
        'incident': 15.0,               # Recent incident impact
        'experience': 5.0,              # Experience bonus
        'shift_type': 10.0,             # Night shift considerations
    }
    
    # Department priority scores (higher = higher stress department)
    DEPARTMENT_PRIORITY = {
        'ED': 3,      # Emergency Department - highest stress
        'ICU': 2,     # Intensive Care Unit - high stress
        'GENERAL': 1  # General - lower stress
    }
    
    def __init__(self):
        self.recommendations: List[StaffRecommendation] = []
    
    def calculate_suitability_score(
        self, 
        staff: StaffProfile, 
        shift: Shift,
        department_name: Optional[str] = None
    ) -> StaffRecommendation:
        """
        Calculate suitability score for a staff member for a given shift.
        
        Higher score = more suitable for the shift
        Lower score = less suitable (likely overworked/stressed)
        
        Args:
            staff: Staff member profile
            shift: Shift details
            department_name: Name of the shift's department (e.g., 'ED', 'ICU', 'GENERAL')
        
        Returns:
            StaffRecommendation with score and breakdown
        """
        breakdown = {}
        warnings = []
        total_score = 50.0  # Base score
        
        # 1. AVAILABILITY CHECK (Critical)
        availability_score = self._calculate_availability_score(staff)
        breakdown['availability'] = availability_score
        
        if availability_score == 0:
            warnings.append("Staff member is not available")
            return StaffRecommendation(
                staff_id=staff.staff_id,
                staff_name=f"{staff.first_name} {staff.last_name}",
                suitability_score=0.0,
                breakdown=breakdown,
                warnings=warnings
            )
        
        # 2. DEPARTMENT MATCH
        department_score = self._calculate_department_score(
            staff, shift, department_name
        )
        breakdown['department_match'] = department_score
        total_score += department_score
        
        # 3. WELLNESS SCORE (penalize high fatigue/stress/burnout)
        wellness_score = self._calculate_wellness_score(staff)
        breakdown['wellness'] = wellness_score
        total_score += wellness_score
        
        if wellness_score < -20:
            warnings.append("High burnout risk or poor wellness scores")
        
        # 4. WORKLOAD SCORE (penalize overwork)
        workload_score = self._calculate_workload_score(staff, shift)
        breakdown['workload'] = workload_score
        total_score += workload_score
        
        if workload_score < -15:
            warnings.append("High recent workload")
        
        # 5. INCIDENT EXPOSURE (penalize recent traumatic incidents)
        incident_score = self._calculate_incident_score(staff)
        breakdown['incident'] = incident_score
        total_score += incident_score
        
        if incident_score < -10:
            warnings.append("Recent high-severity incident exposure")
        
        # 6. EXPERIENCE BONUS (more experienced = slightly better)
        experience_score = self._calculate_experience_score(staff)
        breakdown['experience'] = experience_score
        total_score += experience_score
        
        # 7. SHIFT TYPE CONSIDERATION (night shift fatigue)
        shift_type_score = self._calculate_shift_type_score(staff, shift)
        breakdown['shift_type'] = shift_type_score
        total_score += shift_type_score
        
        if shift.shift_type == 'NIGHT' and staff.night_shifts and staff.night_shifts >= 3:
            warnings.append("Already worked many night shifts recently")
        
        # Ensure score doesn't go negative
        total_score = max(0.0, total_score)
        
        return StaffRecommendation(
            staff_id=staff.staff_id,
            staff_name=f"{staff.first_name} {staff.last_name}",
            suitability_score=total_score,
            breakdown=breakdown,
            warnings=warnings
        )
    
    def _calculate_availability_score(self, staff: StaffProfile) -> float:
        """Check if staff is available (ACTIVE status)"""
        if staff.status.upper() == 'ACTIVE':
            return self.WEIGHTS['availability']
        return 0.0
    
    def _calculate_department_score(
        self, 
        staff: StaffProfile, 
        shift: Shift,
        department_name: Optional[str]
    ) -> float:
        """
        Give bonus for primary department match.
        Consider department stress levels.
        """
        score = 0.0
        
        # Primary department match bonus
        if staff.primary_department_id == shift.department_id:
            score += self.WEIGHTS['department_match']
        else:
            # Small penalty for working outside primary department
            score -= 5.0
        
        return score
    
    def _calculate_wellness_score(self, staff: StaffProfile) -> float:
        """
        Penalize staff with poor wellness indicators.
        Lower fatigue/stress = higher score
        """
        score = 0.0
        weight = self.WEIGHTS['wellness']
        
        # Fatigue score (1-10, higher = worse)
        if staff.fatigue_score is not None:
            # Convert to penalty: 1 = -3, 10 = -30
            fatigue_penalty = (staff.fatigue_score - 1) / 9.0
            score -= weight * fatigue_penalty
        
        # Stress score (1-10, higher = worse)
        if staff.stress_score is not None:
            stress_penalty = (staff.stress_score - 1) / 9.0
            score -= weight * stress_penalty
        
        # Burnout risk level
        if staff.burnout_risk_level:
            level = staff.burnout_risk_level.upper()
            if level == 'HIGH':
                score -= weight * 1.5  # Heavy penalty
            elif level == 'MEDIUM':
                score -= weight * 0.7  # Moderate penalty
            # LOW or None = no penalty
        
        return score
    
    def _calculate_workload_score(self, staff: StaffProfile, shift: Shift) -> float:
        """
        Penalize staff with high recent workload.
        Consider total hours, night shifts, consecutive days, overtime.
        """
        score = 0.0
        weight = self.WEIGHTS['workload']
        
        # Total hours (penalize if > 40 hours/week)
        if staff.total_hours is not None:
            if staff.total_hours > 50:
                score -= weight * 1.0  # Heavy penalty
            elif staff.total_hours > 40:
                score -= weight * 0.5  # Moderate penalty
            elif staff.total_hours < 30:
                score += weight * 0.3  # Bonus for light workload
        
        # Night shifts (penalize if already worked many)
        if staff.night_shifts is not None:
            if staff.night_shifts >= 4:
                score -= weight * 0.8
            elif staff.night_shifts >= 3:
                score -= weight * 0.5
            elif staff.night_shifts >= 2:
                score -= weight * 0.2
        
        # Consecutive days (need rest)
        if staff.consecutive_days is not None:
            if staff.consecutive_days >= 6:
                score -= weight * 1.2  # Really needs a break
            elif staff.consecutive_days >= 4:
                score -= weight * 0.6
            elif staff.consecutive_days >= 3:
                score -= weight * 0.3
        
        # Overtime hours
        if staff.overtime_hours is not None and staff.overtime_hours > 0:
            overtime_penalty = min(staff.overtime_hours / 10.0, 1.0)
            score -= weight * overtime_penalty
        
        return score
    
    def _calculate_incident_score(self, staff: StaffProfile) -> float:
        """
        Penalize staff with recent traumatic incident exposure.
        Recent high-severity incidents have higher weight.
        """
        score = 0.0
        weight = self.WEIGHTS['incident']
        
        if staff.recent_incident_severity is None:
            return score  # No recent incidents = no penalty
        
        severity = staff.recent_incident_severity.upper()
        emotional_weight = staff.recent_incident_weight or 5.0
        days_since = staff.days_since_incident or 0
        
        # Severity multiplier
        severity_multiplier = {
            'HIGH': 1.5,
            'MEDIUM': 1.0,
            'LOW': 0.5
        }.get(severity, 1.0)
        
        # Recency factor (exponential decay: more recent = higher impact)
        # After 30 days, impact is minimal
        recency_factor = math.exp(-days_since / 30.0)
        
        # Emotional weight normalized (0-10 scale to 0-1)
        emotional_factor = emotional_weight / 10.0
        
        # Combined penalty
        penalty = weight * severity_multiplier * recency_factor * emotional_factor
        score -= penalty
        
        return score
    
    def _calculate_experience_score(self, staff: StaffProfile) -> float:
        """
        Give small bonus for experience.
        More experienced staff might handle stress better.
        """
        score = 0.0
        weight = self.WEIGHTS['experience']
        
        if staff.hire_date:
            today = datetime.now()
            years_of_service = (today - staff.hire_date).days / 365.25
            
            # Cap bonus at 5 years
            experience_bonus = min(years_of_service / 5.0, 1.0)
            score += weight * experience_bonus
        
        return score
    
    def _calculate_shift_type_score(self, staff: StaffProfile, shift: Shift) -> float:
        """
        Consider shift type (day vs night).
        If night shift and staff has worked many night shifts, penalize.
        """
        score = 0.0
        
        if shift.shift_type == 'NIGHT':
            weight = self.WEIGHTS['shift_type']
            
            # If staff has worked many night shifts, give penalty
            if staff.night_shifts is not None:
                if staff.night_shifts >= 3:
                    score -= weight * 0.8
                elif staff.night_shifts >= 2:
                    score -= weight * 0.4
        
        return score
    
    def recommend_top_staff(
        self,
        available_staff: List[StaffProfile],
        shift: Shift,
        department_name: Optional[str] = None,
        top_n: int = 5
    ) -> List[StaffRecommendation]:
        """
        Recommend the top N staff members for a given shift.
        
        Args:
            available_staff: List of staff profiles to consider
            shift: The shift to assign
            department_name: Name of the department (for priority calculation)
            top_n: Number of top recommendations to return
        
        Returns:
            List of top N staff recommendations, sorted by suitability score (descending)
        """
        recommendations = []
        
        for staff in available_staff:
            recommendation = self.calculate_suitability_score(staff, shift, department_name)
            recommendations.append(recommendation)
        
        # Sort by suitability score (descending)
        recommendations.sort(key=lambda x: x.suitability_score, reverse=True)
        
        return recommendations[:top_n]
    
    def explain_recommendation(self, recommendation: StaffRecommendation) -> str:
        """
        Generate a human-readable explanation of the recommendation.
        
        Args:
            recommendation: The staff recommendation to explain
        
        Returns:
            String explanation
        """
        lines = [
            f"\nRecommendation for {recommendation.staff_name} (ID: {recommendation.staff_id})",
            f"Overall Suitability Score: {recommendation.suitability_score:.2f}",
            "\nScore Breakdown:"
        ]
        
        for component, score in recommendation.breakdown.items():
            lines.append(f"  - {component}: {score:+.2f}")
        
        if recommendation.warnings:
            lines.append("\nWarnings:")
            for warning in recommendation.warnings:
                lines.append(f"  ⚠ {warning}")
        
        return "\n".join(lines)



def allocate_shifts(
    self,
    staff_list: List[StaffProfile],
    shifts: List[Shift],
    department_name: str = None
):
    roster = []
    assigned_staff_ids = set()

    for shift in shifts:
        # Filter staff not already assigned
        available_staff = [
            s for s in staff_list
            if s.staff_id not in assigned_staff_ids
        ]

        # Rank staff for this shift
        recommendations = self.recommend_top_staff(
            available_staff,
            shift,
            department_name,
            top_n=len(available_staff)
        )

        # Determine how many staff needed
        required = getattr(shift, "required_staff_count", 1)

        selected = []
        for rec in recommendations:
            if len(selected) >= required:
                break

            selected.append(rec)
            assigned_staff_ids.add(rec.staff_id)

        # Store result
        roster.append({
            "shift_id": shift.shift_id,
            "department_id": shift.department_id,
            "shift_type": shift.shift_type,
            "shift_start": shift.shift_start.isoformat(),
            "shift_end": shift.shift_end.isoformat(),
            "assigned_staff": [
                {
                    "staff_id": r.staff_id,
                    "name": r.staff_name,
                    "score": r.suitability_score
                }
                for r in selected
            ]
        })

    return roster