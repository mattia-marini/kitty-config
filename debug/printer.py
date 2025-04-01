import os
import inspect


class Logger:
    def __init__(self, pipe_path: str = "/tmp/kitty_debug"):
        self.pipe_path = pipe_path
        if not os.path.exists(self.pipe_path):
            os.mkfifo(self.pipe_path)  # Ensure the named pipe exists

    def log(self, msg: str):
        with open(self.pipe_path, "w") as pipe:
            pipe.write(msg)
            pipe.flush()

    def inspect(self, obj: object):
        for key, value in vars(logger).items():
            self.log(f"{key}: {type(value).__name__}\n")

    def clear(self):
        self.log("\033[2J\033[H") #tput clear
        self.log("\033[3J\033[0;0H") #resets cursor



# Example usage:
logger = Logger("/tmp/kitty_debug")
# logger.log("Hello from Logger!\n")
logger.inspect(logger)
logger.clear()
logger.inspect(logger)


# for key, value in vars(logger).items():
#     print(f"{key}: {type(value).__name__}")

# print(dir(logger))
