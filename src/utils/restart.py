
import os
import signal
class Restart:

    def run(self) -> None:
        try:
            os.kill(os.getpid(),signal.SIGKILL)
        except Exception as err:
            return err