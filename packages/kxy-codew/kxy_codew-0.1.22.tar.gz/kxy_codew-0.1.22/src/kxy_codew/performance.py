import cProfile
import tempfile
import requests
import threading
import atexit
import time

from .config import CODEW_API_URL

kxy_enabled = "not_initialized"
LICENSE_ID = "Wu0dah3e"
__profiler = cProfile.Profile()


def loop():
    while True:
        time.sleep(2)
        check_token(LICENSE_ID)


def check_token(license_id):
    global kxy_enabled
    base_url = CODEW_API_URL + "/kxy/"
    try:
        response = requests.get(base_url + license_id, timeout=1)
        response.raise_for_status()
        kxy_enabled = response.text.strip()
    except requests.RequestException as e:
        kxy_enabled = "erorred"
        return None


def create_link(response):
    return CODEW_API_URL + "/profile_g2dot/" + response.json().get("id")


def push_results(profiler):
    try:
        upload_url = CODEW_API_URL + "/upload"
        with tempfile.NamedTemporaryFile(suffix=".prof") as tmp:
            profiler.dump_stats(tmp.name)
            tmp.seek(0)
            files = {"file": ("profile.prof", tmp, "application/octet-stream")}
            response = requests.post(upload_url, data={}, files=files)
            print(f"Profile report available at: {create_link(response)}")
            return response.json().get("id")
    except:
        print("Error connecting to 7176")
        ...


def log_traceback(data):
    upload_url = CODEW_API_URL + "/traceback"
    print("I'll upload a traceback.")


def profile(func):
    def wrapper(*args, **kwargs):
        global kxy_enabled
        if kxy_enabled == "1":
            _profiler = cProfile.Profile()
            _profiler.enable()
            try:
                result = func(*args, **kwargs)
                _profiler.disable()
            except Exception as e:
                _profiler.disable()
                raise e
            finally:
                push_results(_profiler)
            return result
        else:
            return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def end_kxy(_time=None):
    global __profiler

    if _time:
        time.sleep(_time)
    print("ending profiling..")
    __profiler.disable()
    push_results(__profiler)


def init_kxy(_time=None):
    global __profiler
    __profiler.enable()
    if _time:
        end_thread = threading.Thread(target=end_kxy, args=(_time,), daemon=True)
        end_thread.start()
    atexit.register(end_kxy, None)


print("Initializing kxy-codew")
check_token(LICENSE_ID)
thread = threading.Thread(target=loop, daemon=True)
thread.start()
