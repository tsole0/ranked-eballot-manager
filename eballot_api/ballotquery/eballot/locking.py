"""
Generate a lock so that only one thread can create databases at a time
"""

from threading import Lock

db_lock = Lock()