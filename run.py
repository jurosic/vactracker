import threading
from Data.vactracker import VACTracker

th = threading.Thread(target=VACTracker.checker)
th2 = threading.Thread(target=VACTracker.console)
th.start()
th2.start()
