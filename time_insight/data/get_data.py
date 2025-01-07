from sqlalchemy.orm import Session
from time_insight.data.database import engine
from time_insight.data.models import Application, ApplicationActivity, UserSession, UserSessionType
from datetime import datetime

from time_insight.log import log_to_console

def get_programs_data(start_date, end_date, count):
    """
    Get all programs and activities data within specified time range.
    
    :param: start_date: datetime, start date of the range
    :param: end_date: datetime, end date of the range
    :param: count: int, not implemented
    """
    try:
        start_of_day = datetime(start_date.year(), start_date.month(), start_date.day(), 0, 0, 0)
        end_of_day = datetime(end_date.year(), end_date.month(), end_date.day(), 23, 59, 59)

        with Session(engine) as session:
            programs = session.query(
                Application.id.label("Application ID"),
                Application.name.label("Name"),
                Application.desc.label("Description"),
                Application.enrollment_date.label("Enrollment Date"),
                Application.path.label("Path"),
                ApplicationActivity.id.label("Activity ID"),
                ApplicationActivity.window_name.label("Window Name"),
                ApplicationActivity.additional_info.label("Additional Info"),
                ApplicationActivity.session_start.label("Start Time"),
                ApplicationActivity.session_end.label("End Time"),
                ApplicationActivity.duration.label("Duration"),
            ).join(ApplicationActivity, Application.id == ApplicationActivity.application_id) \
                .filter(
                    ApplicationActivity.session_start >= start_of_day,
                    ApplicationActivity.session_end <= end_of_day
                ).all()

            programs_data = []
            for program in programs:
                programs_data.append({
                    "Application ID": program[0],
                    "Name": program[1],
                    "Description": program[2],
                    "Enrollment Date": program[3],
                    "Path": program[4],
                    "Activity ID": program[5],
                    "Window Name": program[6],
                    "Additional Info": program[7],
                    "Start Time": program[8],
                    "End Time": program[9],
                    "Duration": program[10],
                })

            return programs_data
    except Exception as e:
        log_to_console(f"Error fetching programs data: {str(e)}")

def get_activity_data(start_date, end_date, count):
        """
        Get all activities data within specified time range.
        
        :param: start_date: datetime, start date of the range
        :param: end_date: datetime, end date of the range
        :param: count: int, not implemented
        """
        try:
            start_of_day = datetime(start_date.year(), start_date.month(), start_date.day(), 0, 0, 0)
            end_of_day = datetime(end_date.year(), end_date.month(), end_date.day(), 23, 59, 59)

            with Session(engine) as session:
                activities = session.query(
                    ApplicationActivity.id.label("Activity ID"),
                    ApplicationActivity.application_id.label("Application ID"),
                    ApplicationActivity.window_name.label("Window Name"),
                    ApplicationActivity.additional_info.label("Additional Info"),
                    ApplicationActivity.session_start.label("Start Time"),
                    ApplicationActivity.session_end.label("End Time"),
                    ApplicationActivity.duration.label("Duration"),
                    Application.name.label("Program Name"),
                    Application.desc.label("Program Description"),
                    Application.enrollment_date.label("Enrollment Date"),
                    Application.path.label("Program Path")
                ).join(
                    Application, Application.id == ApplicationActivity.application_id
                ).filter(
                    ApplicationActivity.session_start >= start_of_day,
                    ApplicationActivity.session_end <= end_of_day
                ).all()

                activity_data = []
                for activity in activities:
                    activity_data.append({
                        "Activity ID": activity[0],
                        "Application ID": activity[1],
                        "Window Name": activity[2],
                        "Additional Info": activity[3],
                        "Start Time": activity[4],
                        "End Time": activity[5],
                        "Duration": activity[6],
                        "Program Name": activity[7],
                        "Program Description": activity[8],
                        "Enrollment Date": activity[9],
                        "Program Path": activity[10]
                    })

                return activity_data
        except Exception as e:
            log_to_console(f"Error fetching activity data: {str(e)}")
            return []

def get_computer_usage_data(start_date, end_date):
    """
    Get all user sessions data within specified time range.
    
    :param: start_date: datetime, start date of the range
    :param: end_date: datetime, end date of the range
    """
    try:
        start_of_day = datetime(start_date.year(), start_date.month(), start_date.day(), 0, 0, 0)
        end_of_day = datetime(end_date.year(), end_date.month(), end_date.day(), 23, 59, 59)

        with Session(engine) as session:
            user_sessions = session.query(UserSession, UserSessionType.name).join(
                UserSessionType, UserSession.user_session_type_id == UserSessionType.id
            ).filter(
                UserSession.session_start >= start_of_day,
                UserSession.session_end <= end_of_day
            ).all()

            if user_sessions:
                user_sessions_data = []
                for session, session_type_name in user_sessions:
                    session_data = {
                        "Session id": session.id,
                        "Session type name": session_type_name,
                        "Start Time": session.session_start,
                        "End Time": session.session_end,
                        "Duration": session.duration
                    }
                    user_sessions_data.append(session_data)
            else:
                log_to_console("No user sessions found.")

        return user_sessions_data
    except Exception as e:
        log_to_console(f"Error accessing database: {str(e)}")