import win32con

import sys
import ctypes
import ctypes.wintypes

from datetime import datetime
#from data.database import SessionLocal
#from data.models import ApplicationActivity
#from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
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

# store last event time for displaying time between events
lastTime = 0

def log(msg):
    print(msg)

def logError(msg):
    sys.stdout.write(msg + '\n')


def getProcessID(hwnd):
    processID = ctypes.wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(processID))
    return processID.value

def getProcessFilename(processID):
    processFlag = win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ
    hProcess = kernel32.OpenProcess(processFlag, 0, processID)
    if not hProcess:
        print(f"OpenProcess({processID}) failed: {ctypes.WinError()}")
        return None

    try:
        filenameBufferSize = ctypes.wintypes.DWORD(4096)
        filename = ctypes.create_unicode_buffer(filenameBufferSize.value)
        kernel32.QueryFullProcessImageNameW(hProcess, 0, ctypes.byref(filename), ctypes.byref(filenameBufferSize))

        return filename.value
    finally:
        kernel32.CloseHandle(hProcess)

"""
def record_window_activity(process_name, window_name):
    session = SessionLocal()
    try:
        session_start = datetime.now(timezone.utc)
        activity = ApplicationActivity(
            application_id=1, 
            window_name=window_name,
            additional_info=process_name,
            session_start=session_start,
            duration=0
        )
        session.add(activity)
        session.commit()
    finally:
        session.close()"""

def callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
    if idObject != win32con.OBJID_WINDOW or idChild != 0:
        return

    active_hwnd = user32.GetForegroundWindow()

    if event == win32con.EVENT_OBJECT_NAMECHANGE and hwnd != active_hwnd:
        return

    length = user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title, length + 1)

    processID = getProcessID(hwnd)
    process_name = getProcessFilename(processID) if processID else "Unknown"

    eventType = eventTypes.get(event, "Unknown Event")
    print(f"{datetime.now()} {eventType}: Window Title: '{title.value}', Process: {process_name}")

def setHook(WinEventProc):
    return user32.SetWinEventHook(
        win32con.EVENT_SYSTEM_FOREGROUND,
        win32con.EVENT_OBJECT_NAMECHANGE,
        0,
        WinEventProc,
        0,
        0,
        win32con.WINEVENT_OUTOFCONTEXT
    )

def init_tracker():
    ole32.CoInitialize(0)

    WinEventProc = WinEventProcType(callback)
    user32.SetWinEventHook.restype = ctypes.wintypes.HANDLE

    hookID = setHook(WinEventProc)
    if not hookID:
        print('SetWinEventHook failed')
        sys.exit(1)

    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

    user32.UnhookWinEvent(hookID)
    ole32.CoUninitialize()

if __name__ == '__main__':
    init_tracker()
