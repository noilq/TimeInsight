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
from time_insight.log import log_to_console

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_active_window_info():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return None, None, None
    
    length = user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title, length + 1)
    
    processID = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(processID))
    
    process_path = get_process_filename(processID.value) if processID.value else "Unknown"
    process_name = process_path.split("\\")[-1] if process_path != "Unknown" else "Unknown"

    return title.value, process_name, process_path

def get_process_filename(processID):
    process_flag = win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ
    h_process = kernel32.OpenProcess(process_flag, 0, processID)

    if not h_process:
        return None

    try:
        filename_buffer_size = ctypes.wintypes.DWORD(4096)
        filename = ctypes.create_unicode_buffer(filename_buffer_size.value)
        kernel32.QueryFullProcessImageNameW(h_process, 0, ctypes.byref(filename), ctypes.byref(filename_buffer_size))
        return filename.value
    finally:
        kernel32.CloseHandle(h_process)

def make_timezone_aware(dt):
    """Ensure that a datetime object is timezone-aware in UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def record_active_window(engine, event_type="Active"):
    with Session(engine) as session:
        while True:
            title, process_name, process_path = get_active_window_info()
            if title and process_name and process_path:
                
                    current_time = datetime.now(timezone.utc)

                    application = session.query(Application).filter_by(name=process_name).first()
                    
                    if not application:
                        application = Application(
                            name=process_name,
                            desc="",
                            path=process_path,
                            enrollment_date=current_time
                        )
                        session.add(application)
                        session.commit()

                    last_activity = session.query(ApplicationActivity).order_by(desc(ApplicationActivity.session_start)).first()

                    if last_activity:
                        last_activity.session_start = make_timezone_aware(last_activity.session_start)

                    if last_activity and last_activity.window_name == title and last_activity.session_end is None:
                        continue

                    if last_activity and last_activity.session_end is None:
                        last_activity.session_end = current_time
                        last_activity.duration = round((last_activity.session_end - last_activity.session_start).total_seconds(), 3)
                        session.commit()

                    new_activity = ApplicationActivity(
                        application_id=application.id,
                        window_name=title,
                        additional_info=event_type,
                        session_start=current_time
                    )
                    session.add(new_activity)
                    session.commit()

            time.sleep(1)



def init_tracker(): 
    on_start()
    atexit.register(on_end)

    threading.Thread(target=record_active_window, args=(engine,), daemon=True, name="ActiveWindowRecorder").start()


if __name__ == '__main__':
    init_tracker()


def on_start():
    with Session(engine) as session:
        try:
            current_time = datetime.now(timezone.utc)

            new_session = UserSession(
                user_session_type_id=1,
                session_start=current_time
            )

            last_session = session.query(UserSession).order_by(UserSession.id.desc()).first()
            if last_session and last_session.session_end is None:
                last_session.session_end = current_time
                last_session.duration = round((make_timezone_aware(last_session.session_end) -
                                             make_timezone_aware(last_session.session_start)).total_seconds(), 3)

            session.add(new_session)
            session.commit()
        except Exception as e:
            print(f"Error in on_start: {e}")
            session.rollback()

def on_end():
    with Session(engine) as session:
        try:
            current_time = datetime.now(timezone.utc)

            last_activity = session.query(ApplicationActivity).order_by(ApplicationActivity.id.desc()).first()
            if last_activity and last_activity.session_end is None:
                last_activity.session_end = current_time
                last_activity.duration = round((make_timezone_aware(last_activity.session_end) -
                                              make_timezone_aware(last_activity.session_start)).total_seconds(), 3)

            new_session = UserSession(
                user_session_type_id=2,
                session_start=current_time
            )

            last_session = session.query(UserSession).order_by(UserSession.id.desc()).first()
            if last_session and last_session.session_end is None:
                last_session.session_end = current_time
                last_session.duration = round((make_timezone_aware(last_session.session_end) -
                                             make_timezone_aware(last_session.session_start)).total_seconds(), 3)

            session.add(new_session)

            session.commit()
        except Exception as e:
            print(f"Error in on_end: {e}")
            session.rollback()