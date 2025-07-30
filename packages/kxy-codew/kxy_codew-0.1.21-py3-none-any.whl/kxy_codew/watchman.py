import sys
import threading
import asyncio
import traceback


def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # TODO: Send it to the server.
    print("[watchman] Unhandled Exception")
    traceback.print_exception(exc_type, exc_value, exc_traceback)


def wake_up():
    sys.excepthook = log_exception

    if hasattr(threading, 'excepthook'):
        threading.excepthook = lambda args: log_exception(
            args.exc_type, args.exc_value, args.exc_traceback
        )

    try:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(
            lambda loop, context: log_exception(
                type(context.get("exception")),
                context.get("exception"),
                context.get("exception").__traceback__
            ) if context.get("exception") else print(f"[watchman] Unhandled async error: {context}")
        )
    except RuntimeError:
        print("[watchman] Unhandled RUNTIME Exception")
        pass
