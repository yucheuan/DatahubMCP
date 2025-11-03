from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from models import ChildAttendance, AgencySites, AgencySiteRooms, DailyAttendanceLog, CenterSupportReport, LessonPlansPreschool, LessonPlansIT, LessonPlansDetail, DRDPItems, DRDPRecord
from database import get_db_session
from google_service import get_sheets_service, get_forms_service, get_drive_service
from datetime import datetime, timedelta
import json

# Initialize FastMCP server
mcp = FastMCP()


# ============================================================================
# DRDP MAPPING HELPER FUNCTION
# ============================================================================

def convert_drdp_value_to_level(value: Optional[float]) -> Optional[str]:
    """Convert numeric DRDP value to text description.
    
    Args:
        value: Numeric DRDP value (e.g., 5, 5.5, 4.5, 11, 99, 0)
    
    Returns:
        Text description of the DRDP level
    
    Examples:
        5 -> "Exploring Later"
        5.5 -> "Exploring Later + Emerging"
        4.5 -> "Exploring Middle + Emerging"
        11 -> "Unable to rate"
        99 -> "Conditional measure"
        0 -> "Not Yet"
    """
    if value is None:
        return None
    
    # Handle special values
    if value == 11:
        return "Unable to rate"
    if value == 99:
        return "Conditional measure"
    if value == 0:
        return "Not Yet"
    
    # Mapping for base values (integer part)
    base_mapping = {
        1: "Responding Earlier",
        2: "Responding Later",
        3: "Exploring Earlier",
        4: "Exploring Middle",
        5: "Exploring Later",
        6: "Building Earlier",
        7: "Building Middle",
        8: "Building Later",
        9: "Integrating Earlier"
    }
    
    # Split into integer and decimal parts
    base_value = int(value)
    decimal_part = value - base_value
    
    # Get base level description
    base_description = base_mapping.get(base_value, f"Unknown ({base_value})")
    
    # Check if there's an emerging component (0.5)
    if abs(decimal_part - 0.5) < 0.01:  # Check for 0.5 with small tolerance for floating point
        return f"{base_description} + Emerging"
    elif decimal_part > 0.01:  # Some other decimal value
        return f"{base_description} + {decimal_part}"
    else:
        return base_description


# Add tools
@mcp.tool()
def get_sites_with_classrooms(site_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all sites with their classrooms in a hierarchical structure.
    
    Args:
        site_name: Optional filter by site name (partial match supported)
    
    Returns:
        List of sites, each containing their classroom information
    """
    with get_db_session() as db:
        # Query sites
        sites_query = db.query(AgencySites)
        if site_name:
            sites_query = sites_query.filter(AgencySites.Site_Name.like(f"%{site_name}%"))
        
        sites = sites_query.all()
        
        result = []
        for site in sites:
            # Query classrooms for this site
            classrooms = db.query(AgencySiteRooms).filter(
                AgencySiteRooms.Site_ID == site.Site_ID
            ).all()
            
            result.append({
                "site_id": site.Site_ID,
                "site_name": site.Site_Name,
                "site_address": site.Site_Address,
                "site_zip": site.Site_Zip,
                "classrooms": [
                    {
                        "room_id": room.Room_ID,
                        "room_name": room.Room_Name,
                        # "room_age_group": room.Room_AgeGroup
                    }
                    for room in classrooms
                ]
            })
        
        return result


@mcp.tool()
def query_attendance_logs(
    site_id: Optional[str] = None,
    room_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """Query daily attendance logs for sites or classrooms within a date range.
    
    Args:
        site_id: Optional filter by Site_ID to get logs for a specific site
        room_id: Optional filter by Room_ID to get logs for a specific classroom
        start_date: Start date in YYYY-MM-DD format (defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to today)
        limit: Maximum number of records to return (default: 500)
    
    Returns:
        Dictionary containing the query parameters used and list of attendance log records
    
    Note:
        - Date range cannot exceed 3 months from today
        - If no dates specified, defaults to last 7 days
    """
    # Set default date range (last 7 days)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    three_months_ago = today - timedelta(days=90)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid start_date format. Use YYYY-MM-DD format.",
                "records": []
            }
    else:
        start_dt = today - timedelta(days=7)
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid end_date format. Use YYYY-MM-DD format.",
                "records": []
            }
    else:
        end_dt = today
    
    # Validate date range doesn't exceed 3 months from today
    if start_dt < three_months_ago:
        return {
            "error": f"Start date cannot be more than 3 months ago. Earliest allowed date: {three_months_ago.strftime('%Y-%m-%d')}",
            "records": []
        }
    
    if end_dt > today:
        return {
            "error": f"End date cannot be in the future. Latest allowed date: {today.strftime('%Y-%m-%d')}",
            "records": []
        }
    
    if start_dt > end_dt:
        return {
            "error": "Start date cannot be after end date.",
            "records": []
        }
    
    with get_db_session() as db:
        query = db.query(DailyAttendanceLog)
        
        # Apply filters
        if site_id:
            query = query.filter(DailyAttendanceLog.Site_ID == site_id)
        
        if room_id:
            query = query.filter(DailyAttendanceLog.Room_ID == room_id)
        
        # Apply date range filter on Form_Date
        query = query.filter(
            DailyAttendanceLog.Form_Date >= start_dt,
            DailyAttendanceLog.Form_Date <= end_dt
        )
        
        # Order by date descending (most recent first)
        query = query.order_by(DailyAttendanceLog.Form_Date.desc())
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query and convert to dictionaries
        results = query.all()
        
        return {
            "query_info": {
                "site_id": site_id,
                "room_id": room_id,
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "end_date": end_dt.strftime("%Y-%m-%d"),
                "total_records": len(results)
            },
            "records": [
                {
                    "form_id": record.Form_ID,
                    "site_id": record.Site_ID,
                    "room_id": record.Room_ID,
                    "form_date": record.Form_Date.strftime("%Y-%m-%d") if record.Form_Date else None,
                    "dor": record.DOR.strftime("%Y-%m-%d %H:%M:%S") if record.DOR else None,
                    "log_type1": record.Log_Type1,
                    "log_type2": record.Log_Type2,
                    "log_description": record.Log_Description,
                    "timein": record.Timein,
                    "timeout": record.Timeout,
                    "breakfast": record.Breakfast,
                    "lunch": record.Lunch,
                    "pm_snack": record.PM_Snack,
                    "meal_confirm_datetime": record.Meal_Confirm_Datetime.strftime("%Y-%m-%d %H:%M:%S") if record.Meal_Confirm_Datetime else None
                }
                for record in results
            ]
        }

@mcp.tool()
def query_center_support_reports(
    site_id: Optional[str] = None,
    user_id: Optional[str] = None,
    staff_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """Query center support reports within a date range.
    
    Args:
        site_id: Optional filter by Site_ID to get reports for a specific site
        user_id: Optional filter by User_ID to get reports for a specific user (exact match)
        staff_name: Optional filter by staff name (searches within User_ID email, e.g., "firstname.lastname")
        start_date: Start date in YYYY-MM-DD format (defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to today)
        limit: Maximum number of records to return (default: 500)
    
    Returns:
        Dictionary containing the query parameters used and list of support report records
    
    Note:
        - Date range cannot exceed 1 year
        - If no dates specified, defaults to last 7 days (1 week)
        - User_ID format is typically firstname.lastname@domain.org (adjust based on your organization)
        - staff_name will search for partial matches in User_ID (e.g., "john" will match "john.doe@domain.org")
    """
    # Set default date range (last 7 days / 1 week)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    one_year_ago = today - timedelta(days=365)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid start_date format. Use YYYY-MM-DD format.",
                "records": []
            }
    else:
        start_dt = today - timedelta(days=7)  # Default: 1 week ago
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid end_date format. Use YYYY-MM-DD format.",
                "records": []
            }
    else:
        end_dt = today
    
    # Validate end date is not in the future
    if end_dt > today:
        return {
            "error": f"End date cannot be in the future. Latest allowed date: {today.strftime('%Y-%m-%d')}",
            "records": []
        }
    
    # Validate start date is not before end date
    if start_dt > end_dt:
        return {
            "error": "Start date cannot be after end date.",
            "records": []
        }
    
    # Validate date range doesn't exceed 1 year
    date_difference = (end_dt - start_dt).days
    if date_difference > 365:
        return {
            "error": f"Date range cannot exceed 1 year (365 days). Current range: {date_difference} days. Please reduce the date range.",
            "records": []
        }
    
    with get_db_session() as db:
        query = db.query(CenterSupportReport)
        
        # Apply filters
        if site_id:
            query = query.filter(CenterSupportReport.Site_ID == site_id)
        
        if user_id:
            query = query.filter(CenterSupportReport.User_ID == user_id)
        
        if staff_name:
            # Search for staff name within User_ID (e.g., "john" matches "john.doe@domain.org")
            query = query.filter(CenterSupportReport.User_ID.like(f"%{staff_name}%"))
        
        # Apply date range filter on Form_Date
        query = query.filter(
            CenterSupportReport.Form_Date >= start_dt,
            CenterSupportReport.Form_Date <= end_dt
        )
        
        # Order by date descending (most recent first)
        query = query.order_by(CenterSupportReport.Form_Date.desc())
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query and convert to dictionaries
        results = query.all()
        
        return {
            "query_info": {
                "site_id": site_id,
                "user_id": user_id,
                "staff_name": staff_name,
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "end_date": end_dt.strftime("%Y-%m-%d"),
                "duration_days": date_difference,
                "total_records": len(results)
            },
            "records": [
                {
                    "form_id": record.Form_ID,
                    "user_id": record.User_ID,
                    "site_id": record.Site_ID,
                    "form_date": record.Form_Date.strftime("%Y-%m-%d") if record.Form_Date else None,
                    "start_time": record.Start_Time,
                    "end_time": record.End_Time,
                    "support_log": record.Support_Log,
                    "category": record.Category,
                    "onsite_remote": record.OnsiteRemote,
                    "strategies": record.Strategies,
                    "strategies_other": record.Strategies_Other,
                    "debrief": record.Debrief
                }
                for record in results
            ]
        }

def get_drdp_measures_for_lesson_plan(db, form_id: str) -> List[Dict[str, Any]]:
    """Helper function to retrieve DRDP measures for a lesson plan.
    
    Args:
        db: Database session
        form_id: Form_ID of the lesson plan
    
    Returns:
        List of DRDP measures with their details
    """
    # Query LessonPlansDetail for records with P_No starting with "P5_"
    lesson_plan_details = db.query(LessonPlansDetail).filter(
        LessonPlansDetail.Form_ID == form_id,
        LessonPlansDetail.P_No.like("P5_%")
    ).all()
    
    drdp_measures = []
    
    for detail in lesson_plan_details:
        p_no = detail.P_No
        p_content = detail.P_Content
        
        # Parse P_Content as comma-separated values
        if p_content:
            # Split by comma and strip whitespace
            uuid_items = [item.strip() for item in p_content.split(',') if item.strip()]
        else:
            uuid_items = []
        
        # Query DRDPItems for each UUID_Item
        for uuid_item in uuid_items:
            if uuid_item:  # Skip empty strings
                drdp_item = db.query(DRDPItems).filter(
                    DRDPItems.UUID_Item == uuid_item
                ).first()
                
                if drdp_item:
                    drdp_measures.append({
                        "p_no": p_no,
                        "uuid_item": uuid_item,
                        "item_name": drdp_item.Item_Name,
                        "item_category": drdp_item.Item_Catagory  # Note: Database column is misspelled as "Catagory"
                    })
    
    return drdp_measures

@mcp.tool()
def query_lesson_plans(
    lesson_type: str,
    site_id: Optional[str] = None,
    room_id: Optional[str] = None,
    teacher_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """Query lesson plans within a date range, including DRDP measures.
    
    Args:
        lesson_type: Type of lesson plan to query - either "preschool" or "it" (infant/toddler)
        site_id: Optional filter by Site_ID to get lesson plans for a specific site
        room_id: Optional filter by Room_ID to get lesson plans for a specific classroom
        teacher_name: Optional filter by Teacher_Name (partial match supported)
        start_date: Start date in YYYY-MM-DD format (defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to today)
        limit: Maximum number of records to return (default: 500)
    
    Returns:
        Dictionary containing the query parameters used and list of lesson plan records with DRDP measures
    
    Note:
        - Date range cannot exceed 1 year (365 days)
        - If no dates specified, defaults to last 7 days (1 week)
        - lesson_type must be either "preschool" or "it"
        - Each lesson plan record includes DRDP measures from P5_* fields (P5_1, P5_2, P5_3, P5_4, P5_5)
    """
    # Validate lesson type
    if lesson_type.lower() not in ["preschool", "it"]:
        return {
            "error": "Invalid lesson_type. Must be either 'preschool' or 'it' (infant/toddler).",
            "records": []
        }
    
    # Select the appropriate model based on lesson type
    model = LessonPlansPreschool if lesson_type.lower() == "preschool" else LessonPlansIT
    
    # Set default date range (last 7 days / 1 week)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    one_year_ago = today - timedelta(days=365)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid start_date format. Use YYYY-MM-DD format.",
                "records": []
            }
    else:
        start_dt = today - timedelta(days=7)  # Default: 1 week ago
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid end_date format. Use YYYY-MM-DD format.",
                "records": []
            }
    else:
        end_dt = today
    
    # Validate end date is not in the future
    if end_dt > today:
        return {
            "error": f"End date cannot be in the future. Latest allowed date: {today.strftime('%Y-%m-%d')}",
            "records": []
        }
    
    # Validate start date is not before end date
    if start_dt > end_dt:
        return {
            "error": "Start date cannot be after end date.",
            "records": []
        }
    
    # Validate date range doesn't exceed 1 year
    date_difference = (end_dt - start_dt).days
    if date_difference > 365:
        return {
            "error": f"Date range cannot exceed 1 year (365 days). Current range: {date_difference} days. Please reduce the date range.",
            "records": []
        }
    
    with get_db_session() as db:
        query = db.query(model)
        
        # Apply filters
        if site_id:
            query = query.filter(model.Site_ID == site_id)
        
        if room_id:
            query = query.filter(model.Room_ID == room_id)
        
        if teacher_name:
            # Search for teacher name (partial match)
            query = query.filter(model.Teacher_Name.like(f"%{teacher_name}%"))
        
        # Apply date range filter on Form_Date (using DOR for date of record)
        query = query.filter(
            model.DOR >= start_dt,
            model.DOR <= end_dt
        )
        
        # Order by date descending (most recent first)
        query = query.order_by(model.DOR.desc())
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query and convert to dictionaries
        results = query.all()
        
        # Build response based on lesson type
        records = []
        for record in results:
            # Get DRDP measures for this lesson plan
            drdp_measures = get_drdp_measures_for_lesson_plan(db, record.Form_ID)
            
            base_record = {
                "form_id": record.Form_ID,
                "dor": record.DOR.strftime("%Y-%m-%d %H:%M:%S") if record.DOR else None,
                "site_id": record.Site_ID,
                "room_id": record.Room_ID,
                "week_count": record.WeekCount,
                "teacher_name": record.Teacher_Name,
                "study_topic": record.Study_Topic,
                "focus_week": record.Focus_Week,
                "intentional_teaching_cards": record.IntentionalTeachingCards,
                "mighty_minutes": record.MightyMinutes,
                "vocabulary": record.Vocabulary,
                "books": record.Books,
                "family_engagement": record.FamilyEngagement,
                "individualizations": record.Individualizations,
                "blocks": record.Blocks,
                "water_sensory": record.WaterSensory,
                "art": record.Art,
                "music_movement": record.MusicMovement,
                "dramatic_play": record.DramaticPlay,
                "manipulatives": record.Manipulatives,
                "outdoor_classroom": record.OutdoorClassroom,
                "teachers": record.Teachers,
                "enroll_year": record.Enroll_Year,
                "drdp_measures": drdp_measures
            }
            
            # Add preschool-specific fields
            if lesson_type.lower() == "preschool":
                base_record.update({
                    "science": record.Science,
                    "l_math": record.L_Math,
                    "writing": record.Writing,
                    "library": record.Library,
                    "other": record.Other,
                })
            else:  # IT (infant/toddler)
                base_record.update({
                    "infant_modification": record.Infant_Modification,
                    "science_math": record.ScienceMath,
                })
            
            records.append(base_record)
        
        return {
            "query_info": {
                "lesson_type": lesson_type,
                "site_id": site_id,
                "room_id": room_id,
                "teacher_name": teacher_name,
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "end_date": end_dt.strftime("%Y-%m-%d"),
                "duration_days": date_difference,
                "total_records": len(results)
            },
            "records": records
        }

@mcp.tool()
def query_drdp_records(
    site_id: Optional[str] = None,
    room_id: Optional[str] = None,
    child_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 500
) -> Dict[str, Any]:
    """Query DRDP assessment records with converted level descriptions.
    
    Args:
        site_id: Optional filter by Site_ID to get records for a specific site
        room_id: Optional filter by Room_ID to get records for a specific classroom
        child_id: Optional filter by Child_ID to get records for a specific child
        start_date: Start date in YYYY-MM-DD format (defaults to 7 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to today)
        limit: Maximum number of records to return (default: 500)
    
    Returns:
        Dictionary containing the query parameters used and list of DRDP records with converted levels
    
    Note:
        - Date range cannot exceed 1 year (365 days)
        - If no dates specified, defaults to last 7 days (1 week)
        - Only includes records from enrollment year "20-21" and later
        - DRDP measurement values are converted to descriptive levels (e.g., "Exploring Later + Emerging")
    """
    # Set default date range (last 7 days / 1 week)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    one_year_ago = today - timedelta(days=365)
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid start_date format. Use YYYY-MM-DD format.",
                "records": []
            }
    else:
        start_dt = today - timedelta(days=7)  # Default: 1 week ago
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {
                "error": "Invalid end_date format. Use YYYY-MM-DD format.",
                "records": []
            }
    else:
        end_dt = today
    
    # Validate end date is not in the future
    if end_dt > today:
        return {
            "error": f"End date cannot be in the future. Latest allowed date: {today.strftime('%Y-%m-%d')}",
            "records": []
        }
    
    # Validate start date is not before end date
    if start_dt > end_dt:
        return {
            "error": "Start date cannot be after end date.",
            "records": []
        }
    
    # Validate date range doesn't exceed 1 year
    date_difference = (end_dt - start_dt).days
    if date_difference > 365:
        return {
            "error": f"Date range cannot exceed 1 year (365 days). Current range: {date_difference} days. Please reduce the date range.",
            "records": []
        }
    
    with get_db_session() as db:
        query = db.query(DRDPRecord)
        
        # Filter out records with Enroll_Year earlier than "20-21"
        query = query.filter(DRDPRecord.Enroll_Year >= "20-21")
        
        # Apply filters
        if site_id:
            query = query.filter(DRDPRecord.Site_ID == site_id)
        
        if room_id:
            query = query.filter(DRDPRecord.Room_ID == room_id)
        
        if child_id:
            query = query.filter(DRDPRecord.Child_ID == child_id)
        
        # Apply date range filter on Submit_Datetime
        query = query.filter(
            DRDPRecord.Submit_Datetime >= start_dt,
            DRDPRecord.Submit_Datetime <= end_dt
        )
        
        # Order by date descending (most recent first)
        query = query.order_by(DRDPRecord.Submit_Datetime.desc())
        
        # Apply limit
        query = query.limit(limit)
        
        # Execute query and convert to dictionaries
        results = query.all()
        
        # List of DRDP measurement columns to convert
        drdp_columns = [
            'ATL_REG_1', 'ATL_REG_2', 'ATL_REG_3', 'ATL_REG_4', 'ATL_REG_5', 'ATL_REG_6', 'ATL_REG_7',
            'SED_1', 'SED_2', 'SED_3', 'SED_4', 'SED_5',
            'LLD_1', 'LLD_2', 'LLD_3', 'LLD_4', 'LLD_5', 'LLD_6', 'LLD_7', 'LLD_8', 'LLD_9', 'LLD_10',
            'ELD_1', 'ELD_2', 'ELD_3', 'ELD_4',
            'COG_1', 'COG_2', 'COG_3', 'COG_4', 'COG_5', 'COG_6', 'COG_7', 'COG_8', 'COG_9', 'COG_10', 'COG_11',
            'PD_HLTH_1', 'PD_HLTH_2', 'PD_HLTH_3', 'PD_HLTH_4', 'PD_HLTH_5', 'PD_HLTH_6', 'PD_HLTH_7', 'PD_HLTH_8', 'PD_HLTH_9', 'PD_HLTH_10'
        ]
        
        return {
            "query_info": {
                "site_id": site_id,
                "room_id": room_id,
                "child_id": child_id,
                "start_date": start_dt.strftime("%Y-%m-%d"),
                "end_date": end_dt.strftime("%Y-%m-%d"),
                "duration_days": date_difference,
                "total_records": len(results)
            },
            "records": [
                {
                    "form_id": record.Form_ID,
                    "enroll_year": record.Enroll_Year,
                    "child_id": record.Child_ID,
                    "dor": record.DOR.strftime("%Y-%m-%d %H:%M:%S") if record.DOR else None,
                    "site_id": record.Site_ID,
                    "room_id": record.Room_ID,
                    "submit_datetime": record.Submit_Datetime.strftime("%Y-%m-%d %H:%M:%S") if record.Submit_Datetime else None,
                    # DRDP measurements with converted levels
                    "measurements": {
                        col.lower(): {
                            "numeric_value": getattr(record, col),
                            "level_description": convert_drdp_value_to_level(getattr(record, col))
                        }
                        for col in drdp_columns
                    }
                }
                for record in results
            ]
        }


# ============================================================================
# GOOGLE SHEETS TOOLS
# ============================================================================

@mcp.tool()
def list_spreadsheets(max_results: int = 20) -> str:
    """
    List user's Google Spreadsheets
    
    Args:
        max_results: Maximum number of spreadsheets to return (default: 20)
    
    Returns:
        JSON string with spreadsheet names, IDs, and URLs
    """
    service = get_drive_service()
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        pageSize=max_results,
        fields="files(id, name, webViewLink)"
    ).execute()
    
    files = results.get('files', [])
    spreadsheets = [{
        'name': f['name'],
        'id': f['id'],
        'url': f['webViewLink']
    } for f in files]
    
    return json.dumps(spreadsheets, indent=2)


@mcp.tool()
def read_sheet(spreadsheet_id: str, range_name: str = "Sheet1") -> str:
    """
    Read data from a Google Sheet
    
    Args:
        spreadsheet_id: The ID of the spreadsheet (from the URL)
        range_name: The A1 notation of the range to read (default: Sheet1)
    
    Returns:
        JSON string with the sheet data
    """
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    values = result.get('values', [])
    return json.dumps(values, indent=2)


# @mcp.tool()
# def write_sheet(spreadsheet_id: str, range_name: str, values: list) -> str:
#     """
#     Write data to a Google Sheet
    
#     Args:
#         spreadsheet_id: The ID of the spreadsheet
#         range_name: The A1 notation of where to write
#         values: 2D list of values to write
    
#     Returns:
#         Confirmation message
#     """
#     service = get_sheets_service()
#     body = {'values': values}
    
#     result = service.spreadsheets().values().update(
#         spreadsheetId=spreadsheet_id,
#         range=range_name,
#         valueInputOption='RAW',
#         body=body
#     ).execute()
    
#     return f"Updated {result.get('updatedCells')} cells"


# @mcp.tool()
# def append_sheet(spreadsheet_id: str, range_name: str, values: list) -> str:
#     """
#     Append data to a Google Sheet
    
#     Args:
#         spreadsheet_id: The ID of the spreadsheet
#         range_name: The A1 notation of the range
#         values: 2D list of values to append
    
#     Returns:
#         Confirmation message
#     """
#     service = get_sheets_service()
#     body = {'values': values}
    
#     result = service.spreadsheets().values().append(
#         spreadsheetId=spreadsheet_id,
#         range=range_name,
#         valueInputOption='RAW',
#         body=body
#     ).execute()
    
#     return f"Appended {result.get('updates').get('updatedCells')} cells"


@mcp.tool()
def create_spreadsheet(title: str) -> str:
    """
    Create a new Google Spreadsheet
    
    Args:
        title: The title of the new spreadsheet
    
    Returns:
        JSON with spreadsheet ID and URL
    """
    service = get_sheets_service()
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    
    result = service.spreadsheets().create(body=spreadsheet).execute()
    
    return json.dumps({
        'spreadsheet_id': result.get('spreadsheetId'),
        'url': result.get('spreadsheetUrl')
    }, indent=2)


@mcp.tool()
def create_form(title: str, description: str = "") -> str:
    """
    Create a new Google Form
    
    Args:
        title: The title of the form
        description: Optional description for the form
    
    Returns:
        JSON with form ID and URL
    """
    service = get_forms_service()
    form = {
        'info': {
            'title': title,
            'documentTitle': title
        }
    }
    
    if description:
        form['info']['description'] = description
    
    result = service.forms().create(body=form).execute()
    
    return json.dumps({
        'form_id': result.get('formId'),
        'url': result.get('responderUri')
    }, indent=2)

# ============================================================================
# GOOGLE SHEETS RESOURCES
# ============================================================================

@mcp.resource("sheet://{spreadsheet_id}/{range_name}")
def get_sheet_resource(spreadsheet_id: str, range_name: str = "Sheet1") -> str:
    """
    Resource for accessing Google Sheet data
    
    Args:
        spreadsheet_id: The spreadsheet ID
        range_name: The range to read
    
    Returns:
        Sheet data as text
    """
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    values = result.get('values', [])
    
    # Format as readable text
    output = []
    for row in values:
        output.append(' | '.join(str(cell) for cell in row))
    
    return '\n'.join(output)


# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

@mcp.prompt()
def analyze_sheet_data():
    """Analyze data from a Google Sheet with comprehensive insights"""
    return """I need help analyzing data from a Google Sheet. Please follow this workflow:

1. **Data Retrieval & Overview**
   - Ask me for the spreadsheet name and range (or help me list my spreadsheets if needed), unless the user has already retrieved a spreadsheet
   - Read the sheet data using the read_sheet tool
   - Provide a high-level summary:
     * Total number of rows and columns
     * Column headers/names
     * Date range (if applicable)
     * Brief description of what type of data this appears to be

2. **Data Structure Analysis**
   - Identify data types in each column (text, numeric, dates, categorical, etc.)
   - Note which columns contain responses vs. metadata
   - Check for missing, empty, or inconsistent values
   - Identify any obvious patterns in data organization

3. **Quantitative Analysis** (where applicable)
   - Calculate relevant statistics:
     * For numeric columns: averages, ranges (min/max), totals
     * For categorical data: frequency distributions, most common values
     * For rating scales: score distributions and averages
   - Identify any outliers or unusual values

4. **Qualitative Insights** (where applicable)
   - Summarize themes in text responses
   - Identify common keywords or topics
   - Note any particularly interesting or concerning comments
   - Highlight consensus vs. divergent opinions

5. **Key Findings & Recommendations**
   - Summarize 3-5 most important insights from the data
   - Flag any data quality issues or anomalies
   - Suggest improvements (data cleaning, additional fields, validation rules)
   - Recommend next steps for analysis or action
   - Propose visualization options that would make the data clearer

Please present findings in a clear, scannable format with specific examples and numbers from the actual data."""


@mcp.prompt()
def create_report_template():
    """Create a professional report document in the canvas"""
    return """Help me create a professional report document with the following structure. Please create this as a well-formatted markdown document in the canvas:

1. **Report Header**
   - Report title
   - Company name (Lonely Octopus)
   - Report period/date range
   - Date generated

2. **Executive Summary**
   - Brief overview of key findings (2-3 paragraphs)
   - Highlight the most critical insights
   - Bottom-line recommendation or conclusion

3. **Key Metrics Dashboard**
   - Create a clean table with columns: Metric | Value | Change | Status
   - Include 5-8 relevant metrics with placeholder values
   - Add brief context notes below the table

4. **Detailed Analysis**
   - Break down findings into logical sections
   - Use clear headers for each topic area
   - Include supporting data and evidence
   - Present information in scannable format

5. **Findings & Recommendations**
   - **Key Findings**: List 3-5 most important discoveries
   - **Recommendations**: Specific, actionable suggestions
   - **Action Items**: Table with columns for Item, Owner, Due Date, Priority

6. **Appendix/Additional Notes**
   - Methodology or data sources (if applicable)
   - Assumptions made
   - Areas for further investigation
   - Additional context or supporting information

Please format the report with:
- Clear hierarchy using markdown headers
- Professional tables for data presentation
- Bold text for emphasis on key points
- Appropriate spacing for readability
- Placeholder content that can be easily customized"""


@mcp.prompt()
def form_to_sheet():
    """Create a Google Form and spreadsheet workflow for data collection"""
    return """Help me set up a complete data collection workflow using Google Forms and Sheets:

1. **Understand Requirements**
   - Ask me what type of data I want to collect
   - Ask about the purpose (survey, registration, feedback, etc.)
   - Confirm the key fields/questions needed

2. **Create Google Form**
   - Use create_form tool with an appropriate title and description
   - Provide the form URL for editing
   - Suggest question types for each field (short answer, multiple choice, etc.)

3. **Create Response Spreadsheet**
   - Create a new spreadsheet with create_spreadsheet tool
   - Name it to match the form (e.g., "Form Name - Responses")
   - Set up the first row with column headers matching the form questions
   - Add a "Timestamp" column as the first column

4. **Integration Instructions**
   - Provide step-by-step instructions to link the form to the spreadsheet:
     * Open the Form in edit mode
     * Click "Responses" tab
     * Click the green Sheets icon
     * Select "Create a new spreadsheet" or link to existing
   - Note: This step requires manual action in the Google Forms interface

5. **Setup Recommendations**
   - Suggest form settings (collect email, limit to 1 response, etc.)
   - Recommend data validation rules
   - Propose notification settings for new responses
   - Suggest basic formulas or formatting for the response sheet

6. **Provide Summary**
   - Form URL for editing and sharing
   - Spreadsheet URL for viewing responses
   - Quick reference guide for managing the workflow

Please provide all URLs and IDs clearly formatted for easy access."""


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')