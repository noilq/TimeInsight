import win32con
import sys
import ctypes
import ctypes.wintypes
import threading
import time
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timezone
from time_insight.data.database import engine
from time_insight.data.models import Application, ApplicationActivity

sys.stdout.reconfigure(encoding='utf-8')

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32 #???
kernel32 = ctypes.windll.kernel32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    ctypes.wintypes.HANDLE,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.HWND,
    ctypes.wintypes.LONG,
    ctypes.wintypes.LONG,
    ctypes.wintypes.DWORD,
    ctypes.wintypes.DWORD
)

# http://msdn.microsoft.com/en-us/library/windows/desktop/dd318066(v=vs.85).aspx
eventTypes = {
    win32con.EVENT_SYSTEM_FOREGROUND: "Foreground",
    win32con.EVENT_OBJECT_NAMECHANGE: "NameChange"
}

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
    while True:
        title, process_name, process_path = get_active_window_info()
        if title and process_name and process_path:
            with Session(engine) as session:
                # Проверка существующего приложения в базе данных
                application = session.query(Application).filter_by(name=process_name).first()
                
                if not application:
                    application = Application(
                        name=process_name,
                        desc="",
                        path=process_path,
                        enrollment_date=datetime.now(timezone.utc)  # Timezone-aware
                    )
                    session.add(application)
                    session.commit()

                # Получение самой последней записи активности из таблицы ApplicationActivity
                last_activity = session.query(ApplicationActivity).order_by(desc(ApplicationActivity.session_start)).first()

                current_time = datetime.now(timezone.utc)  # Timezone-aware

                if last_activity:
                    # Убедимся, что `session_start` последней активности имеет правильный временной пояс
                    last_activity.session_start = make_timezone_aware(last_activity.session_start)

                # Проверка, является ли последняя активность такой же, как текущая
                if last_activity and last_activity.window_name == title and last_activity.session_end is None:
                    # Если последняя активность та же самая и не завершена, пропускаем запись
                    continue

                # Если последняя активность отличается или была завершена, завершаем её и записываем новую
                if last_activity and last_activity.session_end is None:
                    # Завершаем предыдущую активность, если она была не завершена
                    last_activity.session_end = current_time  # Timezone-aware
                    last_activity.duration = (last_activity.session_end - last_activity.session_start).total_seconds()
                    session.commit()

                # Добавляем новую активность
                new_activity = ApplicationActivity(
                    application_id=application.id,
                    window_name=title,
                    additional_info=event_type,
                    session_start=current_time  # Timezone-aware
                )
                session.add(new_activity)
                session.commit()

        time.sleep(1)


def start_tracker_thread():
    tracker_thread = threading.Thread(target=init_tracker, daemon=True)
    tracker_thread.start()
    return tracker_thread

def init_tracker():
    record_active_window(engine)

if __name__ == '__main__':
    init_tracker()