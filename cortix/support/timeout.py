import signal

class Timeout:
    def __init__(self, seconds=1, error_message='Timeout Error'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        if self.seconds==None:
            return
        try:
            signal.signal(signal.SIGALRM, self.handle_timeout)
        except AttributeError as e:
            print('Timeout function currently not available on Windows OS')
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        try:
            signal.alarm(0)
        except:
            pass
