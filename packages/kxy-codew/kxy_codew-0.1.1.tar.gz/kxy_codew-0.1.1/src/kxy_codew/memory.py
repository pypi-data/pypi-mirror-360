

def mem_profile(func):
    def wrapper(*args, **kwargs):
        global kxy_enabled
        if kxy_enabled == "1":
            # TODO: Implement memory reporting
            print("Memory profiling is not implemented yet.. we're working on it.")
            result = func(*args, **kwargs)
            return result
        else:
            return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

