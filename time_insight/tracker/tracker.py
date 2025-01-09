import win32con #type: ignore
import ctypes 
import ctypes.wintypes
import threading
import time
import atexit
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc
from datetime import datetime, timezone
from time_insight.data.database import engine
from time_insight.data.models import Application, ApplicationActivity, UserSession, UserSessionType
from apscheduler.schedulers.background import BackgroundScheduler  #scheduler for every half an hour event

from time_insight.logging.logger import logger

#init system libs
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


def get_active_window_info():
    """
    Retrieves the information about the currently active window.

    :return: A tuple containing the window title, process name, and process path.
             Returns (None, None, None) if the active window information cannot be retrieved.
    """
    try:
        hwnd = user32.GetForegroundWindow()     #get active window
        if not hwnd:                           
            return None, None, None, None

        length = user32.GetWindowTextLengthW(hwnd)          #get lenght of the title
        title = ctypes.create_unicode_buffer(length + 1)    #create buffer for window title 
        user32.GetWindowTextW(hwnd, title, length + 1)      #extract title text

        processID = ctypes.wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(processID))      #get id of the window process

        #get process path
        processID_value = processID.value
        process_path = get_process_filename(processID.value) if processID.value else "Unknown"
        process_name = process_path.split("\\")[-1] if process_path != "Unknown" else "Unknown"

        logger.info(f"Active window: {process_name}, PID: {processID}.")

        return title.value, process_name, process_path, processID_value
    except Exception as e:
        logger.error(f"Error in tracker.py - get_active_window_info: {e}")
        return None, None, None, None

def get_process_filename(processID):
    """
    Retrieves full file path of a process by given PID.

    :param processID: The ID of the process.
    :return: The full path to the process executable file, or None if the process cannot be accessed.
    """
    process_flag = win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ    #flags to access the process
    h_process = kernel32.OpenProcess(process_flag, 0, processID)                    #opens the process

    if not h_process:
        logger.warning(f"Failed to open process with ID {processID}.")
        return None

    try:
        filename_buffer_size = ctypes.wintypes.DWORD(4096)                      #set buffer size
        filename = ctypes.create_unicode_buffer(filename_buffer_size.value)     #create buffer 
        kernel32.QueryFullProcessImageNameW(h_process, 0, ctypes.byref(filename), ctypes.byref(filename_buffer_size))      #get process path
        return filename.value
    finally:
        kernel32.CloseHandle(h_process)     #always close process handle

def make_timezone_aware(dt):
    """
    Makes a datetime object timezone-aware, setting it to UTC if it's naive.

    :param dt: The datetime object to make timezone-aware.
    :return: A timezone-aware datetime object (in UTC).
    """
    try:
        if dt.tzinfo is None:                           #if there is no info about timezone
            return dt.replace(tzinfo=timezone.utc)      #set to utc
        return dt
    except Exception as e:
        logger.error(f"Error in tracker.py - make_timezone_aware: {e}")
        return dt

def record_active_window(engine, event_type="Active"):
    """
    Continuously tracks the active window and logs its information to the database.

    Runs in an infinite loop, periodically checking for the active window.

    :param engine: The SQLAlchemy engine used to interact with the database.
    :param event_type: The type of event being logged (default is "Active").
    """
    with Session(engine) as session:    #open session to work with db
        try:
            while True:                 
                title, process_name, process_path, processID = get_active_window_info()  #get active window info
                if title and process_name and process_path:     #check for the data
                    current_time = datetime.now(timezone.utc)   #curr time in utc
                    
                    #check if there is an app record in db
                    application = session.query(Application).filter_by(name=process_name).first()
                    if not application:
                        #create new app record
                        application = Application(
                            name=process_name,
                            desc="",
                            path=process_path,
                            enrollment_date=current_time
                        )
                        session.add(application)
                        session.commit()

                        logger.info(f"New application created: {process_name} {process_path}.")

                    #check last activity
                    #if last activity hasnt ended yet and has the same title -> skip
                    last_activity = session.query(ApplicationActivity).order_by(desc(ApplicationActivity.session_start)).first()
                    if last_activity and last_activity.window_name == title and last_activity.session_end is None:
                        time.sleep(1)
                        continue
                    
                    #close previous activity if hasnt yet been completed
                    if last_activity and last_activity.session_end is None:
                        update_last_activity(session, current_time)

                    #create new activity
                    new_activity = ApplicationActivity(
                        application_id=application.id,
                        window_name=title,
                        additional_info=f"{event_type}, PID: {processID}", 
                        session_start=current_time
                    )
                    session.add(new_activity)
                    session.commit()

                    logger.info(f"New activity created for application: {process_name}, window: {title}, PID: {processID}")

                time.sleep(1)
        except Exception as e:
            logger.error(f"Error in tracker.py - record_active_window: {e}")
            session.rollback()

def init_tracker():
    """
    Initializes activity tracker 

    Starts a background thread that continuously tracks the active window 

    :return: None
    """
    on_start()                  #action on start
    atexit.register(on_end)     #register action on end
    
    #start a thread for main tracker
    threading.Thread(target=record_active_window, args=(engine,), daemon=True, name="ActiveWindowRecorder").start()

    schedule_half_hour_tasks()  #schedule half an hour tasks

if __name__ == '__main__':
    init_tracker()

def update_last_session(session, end_time):
    """
    Ends last active session if its still ongoing and updates its duration.
    
    :param session: SQLAlchemy session object used for database interactions.
    :param end_time: The timestamp indicating the end of the session (timezone-aware).
    """
    last_session = session.query(UserSession).order_by(UserSession.id.desc()).first()   #get last session
    if last_session and last_session.session_end is None:   #end last session if still active
        last_session.session_end = end_time     
        last_session.duration = round((make_timezone_aware(last_session.session_end) -
                                       make_timezone_aware(last_session.session_start)).total_seconds(), 3)
        session.commit()    #save changes

        logger.info("Last session ended.")

def update_last_activity(session, end_time):
    """
    Ends last active activity if its still ongoing and updates its duration.
    
    :param session: SQLAlchemy session object used for database interactions.
    :param end_time: The timestamp indicating the end of the activity (timezone-aware).
    """
    last_activity = session.query(ApplicationActivity).order_by(ApplicationActivity.id.desc()).first()  #get last activity
    if last_activity and last_activity.session_end is None: #end last activity if still active
        last_activity.session_end = end_time
        last_activity.duration = round((make_timezone_aware(last_activity.session_end) -
                                        make_timezone_aware(last_activity.session_start)).total_seconds(), 3)
        session.commit()    #save changes

        logger.info("Last activity ended.")

def add_user_session(session, session_type_id, start_time):
    """
    Adds a new user session to the database.
    
    :param session: SQLAlchemy session object used for database interactions.
    :param session_type_id: Integer representing the type of session (1 for Active, 2 for Sleep).
    :param start_time: The timestamp indicating when the session started (timezone-aware).
    """
    new_session = UserSession(
        user_session_type_id=session_type_id,   #session type, 1 for Active, 2 for Sleep
        session_start=start_time
    )
    session.add(new_session)
    session.commit()

    logger.info("New user session added.")

def on_start():
    """
    This function is called when the program starts. It updates the last session, 
    ends the last active session if it is still ongoing, and adds a new session of 'Active' type.
    """
    logger.info("Application started. Ending last session and adding a new active.")
    with Session(engine) as session:
        try:
            current_time = datetime.now(timezone.utc)   #curr time
            update_last_session(session, current_time)  #end last session
            add_user_session(session, session_type_id=1, start_time=current_time)   #add new active session
        except Exception as e:
            logger.error(f"Error in tracker.py - on_end end: {e}")
            session.rollback()

def on_end():
    """
    This function is called when the program ends. It updates the last activity and session to mark them as ended, 
    calculates their durations, and adds a new session of 'Sleep' type.
    """ 
    logger.info("Application ended. Ending last session and activity, adding a new sleep session.")
    with Session(engine) as session:
        try:
            current_time = datetime.now(timezone.utc)   #curr time
            update_last_activity(session, current_time) #end last activity
            update_last_session(session, current_time)  #end last session
            add_user_session(session, session_type_id=2, start_time=current_time)   #add new sleep session
        except Exception as e:
            logger.error(f"Error in tracker.py - on_end end: {e}")
            session.rollback()

def schedule_half_hour_tasks():
    """
    Schedules a task to end active sessions every half hour.

    This function initializes a background scheduler that runs the end_active_sessions function
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(end_active_sessions, 'cron', minute='0,30')    #run every half an hour
    scheduler.start()

def end_active_sessions():
    """
    Ends the last active activity and session, updates their durations, and starts a new Active session.

    This function is scheduled to run every half an hour to ensure that sessions are properly ended and new sessions are started.
    """
    try:
        with Session(engine) as session:
            current_time = datetime.now(timezone.utc)

            logger.info(f"Executing half-hour sessions killer task at: {current_time}.")

            update_last_activity(session, current_time)
            update_last_session(session, current_time)
            add_user_session(session, session_type_id=1, start_time=current_time)

            session.commit()
            logger.info("Half-hour sessions killer task completed successfully.")

    except Exception as e:
        logger.error(f"Error during half-hour sessions killer task: {e}")


