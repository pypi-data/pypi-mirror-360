#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import code
import datetime
import gc
import logging
import os
import threading
import time
import weakref
import typing as t

import klovve


class _Memory:

    def __init__(self):
        self.__lock = threading.RLock()
        self.__current_counters = {}
        self.__since_startup_counters = {}

    def __change_counter(self, kind: str, by: int) -> None:
        with self.__lock:
            self.__current_counters[kind] = self.__current_counters.get(kind, 0) + by
            self.__since_startup_counters[kind] = self.__since_startup_counters.get(kind, 0) + max(0, by)

    def __increment_counter(self, kind: str) -> None:
        self.__change_counter(kind, 1)

    def __decrement_counter(self, kind: str) -> None:
        self.__change_counter(kind, -1)

    @property
    def current_counters(self):
        with self.__lock:
            return dict(self.__current_counters)

    @property
    def since_startup_counters(self):
        with self.__lock:
            return dict(self.__since_startup_counters)

    def currently_existing_count(self, kind: t.Union[type, str]) -> int:
        if isinstance(kind, type):
            kind = kind.__name__
        return self.current_counters.get(kind, 0)

    def created_since_startup_count(self, kind: t.Union[type, str]) -> int:
        if isinstance(kind, type):
            kind = kind.__name__
        return self.since_startup_counters.get(kind, 0)

    def new_object_created(self, kind: t.Union[type, str], obj):
        if isinstance(kind, type):
            kind = kind.__name__
        self.__increment_counter(kind)
        weakref.finalize(obj, lambda: self.__decrement_counter(kind))

    def cleanup(self):
        gc.collect()

    def __str__(self):
        return (f"/-- In memory ----------------------\n"
                f"{self.__str__body(self.__str__counters(memory.current_counters))}"
                f"+-- Created since startup ----------\n"
                f"{self.__str__body(self.__str__counters(memory.since_startup_counters))}"
                f"\\-----------------------------------\n")

    def __str__counters(self, counters: dict) -> str:
        return "\n".join(f"Number of {kind!r}s: {counters[kind]}" for kind in sorted(counters.keys()))

    def __str__body(self, s: str) -> str:
        return "".join([f"| {line}\n" for line in s.rstrip().split("\n")])


memory = _Memory()


class PrintDebugOverviewThread(threading.Thread):

    def __init__(self):
        super().__init__(daemon=True)
        self.__stopping = False

    def stop(self):
        self.__stopping = True

    def run(self):
        while not self.__stopping:
            memory.cleanup()
            print(f"\n{datetime.datetime.now()}\n{memory}")
            time.sleep(2*60)


_print_debug_overview_thread = None


def start_regularly_dumping_debug_overview():
    global _print_debug_overview_thread

    if not _print_debug_overview_thread:
        _print_debug_overview_thread = PrintDebugOverviewThread()
        _print_debug_overview_thread.start()


def stop_regularly_dumping_debug_overview() -> None:
    global _print_debug_overview_thread

    if _print_debug_overview_thread:
        _print_debug_overview_thread.stop()
        _print_debug_overview_thread = None


def _logger(*, also_to_file: bool = False):
    logger = logging.getLogger(klovve.__name__)
    logger.setLevel(logging.DEBUG if (b"KLOVVE_DEBUG" in os.environb) else logging.INFO)

    handlers = [logging.StreamHandler()]
    if also_to_file:
        handlers.append(logging.FileHandler("/tmp/klovve.log"))

    for handler in handlers:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
        logger.addHandler(handler)

    return logger


log = _logger(also_to_file=False)


def _memory_profiler():
    from guppy import hpy

    def repl():
        code.interact(local={"hpy": hpy, "h": hpy()})

    threading.Thread(target=repl, daemon=True).start()
