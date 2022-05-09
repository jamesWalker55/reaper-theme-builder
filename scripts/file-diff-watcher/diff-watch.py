#!/usr/bin/env python3

from diff_match_patch import diff_match_patch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import sys
import time
from os.path import abspath, dirname

import time


class DiffHandler(FileSystemEventHandler):
    def __init__(self, to_watch):
        self.differ = diff_match_patch()
        self.to_watch = to_watch
        with open(self.to_watch) as f:
            self.last_contents = f.read()

    def on_modified(self, event):
        if event.src_path == self.to_watch:
            time.sleep(0.5)
            with open(self.to_watch) as f:
                new_contents = f.read()
            patch = self.differ.patch_make(self.last_contents, new_contents)
            patch_text = self.differ.patch_toText(patch)
            print(patch_text)
            self.last_contents = new_contents


if len(sys.argv) > 1:
    to_watch = abspath(sys.argv[1])
else:
    print("Error: Select a file to watch.")
    sys.exit(1)

observer = Observer()
observer.schedule(DiffHandler(to_watch), dirname(to_watch))
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
