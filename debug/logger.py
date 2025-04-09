import os

class Logger:
    def __init__(self, pipe_path: str = "/tmp/kitty_debug"):
        self.pipe_path = pipe_path
        if not os.path.exists(self.pipe_path):
            os.mkfifo(self.pipe_path)
        self.clear()
        self.log("Logger initialized\n")



    def log(self, msg: str):
        try:
            fd = os.open(self.pipe_path, os.O_WRONLY | os.O_NONBLOCK)
            with os.fdopen(fd, "w") as pipe:
                pipe.write(msg)
                pipe.flush()
        except OSError as e:
            print(f"Could not write to pipe. Error: {e}")

    def inspect(self, obj: object):
        attributes = {}
        for attr in dir(obj):
            if attr.startswith('_'):
                continue
            try:
                value = getattr(obj, attr)
                attributes[attr] = type(value).__name__
            except Exception as e:
                attributes[attr] = f"<error: {e}>"
    
        formatted = "{\n" + "".join(f"    {k}: {v},\n" for k, v in attributes.items()) + "}"
        self.log(formatted)

    def clear(self):
        self.log("\033[2J\033[H") #tput clear
        self.log("\033[3J\033[0;0H") #resets cursor

# Example usage:
logger = Logger("/tmp/kitty_debug")
logger.inspect(logger)
logger.clear()
logger.inspect(logger)
