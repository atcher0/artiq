import builtins
import linecache
import re
import os

from artiq import __artiq_dir__ as artiq_dir
from artiq.coredevice.runtime import source_loader


ZeroDivisionError = builtins.ZeroDivisionError
ValueError = builtins.ValueError
IndexError = builtins.IndexError


class CoreException:
    """Information about an exception raised or passed through the core device."""

    def __init__(self, name, message, params, traceback):
        if ':' in name:
            exn_id, self.name = name.split(':', 2)
            self.id = int(exn_id)
        else:
            self.id, self.name = 0, name
        self.message, self.params = message, params
        self.traceback = list(traceback)

    def __str__(self):
        lines = []
        lines.append("Core Device Traceback (most recent call last):")
        last_address = 0
        for (filename, line, column, function, address) in self.traceback:
            stub_globals = {"__name__": filename, "__loader__": source_loader}
            source_line = linecache.getline(filename, line, stub_globals)
            indentation = re.search(r"^\s*", source_line).end()

            if address is None:
                formatted_address = ""
            elif address == last_address:
                formatted_address = " (inlined)"
            else:
                formatted_address = " (RA=+0x{:x})".format(address)
            last_address = address

            filename = filename.replace(artiq_dir, "<artiq>")
            if column == -1:
                lines.append("  File \"{file}\", line {line}, in {function}{address}".
                             format(file=filename, line=line, function=function,
                                    address=formatted_address))
                lines.append("    {}".format(source_line.strip() if source_line else "<unknown>"))
            else:
                lines.append("  File \"{file}\", line {line}, column {column},"
                             " in {function}{address}".
                             format(file=filename, line=line, column=column + 1,
                                    function=function, address=formatted_address))
                lines.append("    {}".format(source_line.strip() if source_line else "<unknown>"))
                lines.append("    {}^".format(" " * (column - indentation)))

        lines.append("{}({}): {}".format(self.name, self.id,
                                         self.message.format(*self.params)))
        return "\n".join(lines)


class InternalError(Exception):
    """Raised when the runtime encounters an internal error condition."""
    artiq_builtin = True


class CacheError(Exception):
    """Raised when putting a value into a cache row would violate memory safety."""
    artiq_builtin = True


class RTIOUnderflow(Exception):
    """Raised when the CPU fails to submit a RTIO event early enough
    (with respect to the event's timestamp).

    The offending event is discarded and the RTIO core keeps operating.
    """
    artiq_builtin = True

class RTIOSequenceError(Exception):
    """Raised when an event is submitted on a given channel with a timestamp
    not larger than the previous one.

    The offending event is discarded and the RTIO core keeps operating.
    """
    artiq_builtin = True

class RTIOCollision(Exception):
    """Raised when an event is submitted on a given channel with the same
    coarse timestamp as the previous one but with a different fine timestamp.

    Coarse timestamps correspond to the RTIO system clock (typically around
    125MHz) whereas fine timestamps correspond to the RTIO SERDES clock
    (typically around 1GHz).

    The offending event is discarded and the RTIO core keeps operating.
    """
    artiq_builtin = True

class RTIOBusy(Exception):
    """Raised when at least one output event could not be executed because
    the given channel was already busy executing a previous event.

    This exception is raised late: after the error condition occurred. More
    specifically it is raised on submitting an event on the same channel after
    the execution of the faulty event was attempted.

    The offending event was discarded.
    """
    artiq_builtin = True

class RTIOOverflow(Exception):
    """Raised when at least one event could not be registered into the RTIO
    input FIFO because it was full (CPU not reading fast enough).

    This does not interrupt operations further than cancelling the current
    read attempt and discarding some events. Reading can be reattempted after
    the exception is caught, and events will be partially retrieved.
    """
    artiq_builtin = True

class DDSError(Exception):
    """Raised when attempting to start a DDS batch while already in a batch,
    when too many commands are batched, and when DDS channel settings are
    incorrect.
    """

class WatchdogExpired(Exception):
    """Raised when a watchdog expires."""

class ClockFailure(Exception):
    """Raised when RTIO PLL has lost lock."""
