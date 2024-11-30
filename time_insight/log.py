import datetime

def log_to_console(*args):
    """
    Universal function for console logging.
    
    :param args: Message or data.
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages = " ".join(map(str, args))
    print(f"[{current_time}] {messages}")