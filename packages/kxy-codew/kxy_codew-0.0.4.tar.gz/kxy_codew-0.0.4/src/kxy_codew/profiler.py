import cProfile
import tempfile
import requests
import threading
import time

kxy_enabled = "not_initialized"
LICENSE_ID = "Wu0dah3e"

# https://codew.es/kxy/Wu0dah3e

def loop():
    while True:
        time.sleep(2)
        fetch_lic(LICENSE_ID)


def fetch_lic(license_id):
    global kxy_enabled
    base_url = "https://codew.es/kxy/"
    try:
        response = requests.get(base_url + license_id, timeout=1)
        response.raise_for_status()
        kxy_enabled = response.text.strip()
    except requests.RequestException as e:
        kxy_enabled = "erorred"
        return None


def create_link(response):
    return "https://7176.codew.es/profile_g2dot/" + response.json().get("id")


def push_results(profiler):
    upload_url = "https://7176.codew.es/upload"
    with tempfile.NamedTemporaryFile(suffix=".prof") as tmp:
        profiler.dump_stats(tmp.name)
        tmp.seek(0)
        files = {"file": ("profile.prof", tmp, "application/octet-stream")}
        response = requests.post(upload_url, files=files)
        print(f"Profile generated: {create_link(response)}")


def cprofile(func):
    def wrapper(*args, **kwargs):
        global kxy_enabled
        if kxy_enabled == "1":
            profiler = cProfile.Profile()
            profiler.enable()
            try:
                result = func(*args, **kwargs)
            finally:
                profiler.disable()
                push_results(profiler)
            return result
        else:
            return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


print("Initializing kxy-codew")

fetch_lic(LICENSE_ID)
thread = threading.Thread(target=loop, daemon=True)
thread.start()
