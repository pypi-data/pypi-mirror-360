"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
from threading import Event
from abc import ABCMeta, abstractmethod
import signal
from avesterra import avial as av, av_log

from avesterra.avesterra import AvAuthorization
from avesterra.avial import AvValue, NULL_ENTITY
from avesterra.taxonomy import AvTag

SLEEP_ON_ERROR_SECONDS = 5

MAX_CONNECTION_RETRIES_BEFORE_FAILING = 5


class Adapter:
    """
    Helper class to create an AvesTerra adapter.
    Takes care of some boilerplate, as well as standardizing how we create
    adapters
    """

    __metaclass__ = ABCMeta

    def __init__(
        self,
        server: str,
        directory: str,
        auth: AvAuthorization,
        socket_count: int,
        adapting_threads: int = 1,
    ):
        if not os.path.exists(directory):
            raise IOError(
                f"The given certificate directory '{directory}' doesn't exist"
            )

        self._stop = Event()

        self.auth = auth
        self.avt_server = server
        self.avt_directory = directory
        self._socket_count = socket_count
        self._thread_count = adapting_threads

        self.outlet = NULL_ENTITY

        def signal_handler(sig, frame):
            del sig, frame
            av_log.fatal("Adapter: Received SIGTERM. Stopping.")
            self.shutdown()

        try:
            signal.signal(signal.SIGTERM, signal_handler)

            num_initial_connection_errors = 0
            while True:
                try:
                    av.initialize(
                        server=self.avt_server,
                        directory=self.avt_directory,
                        socket_count=self._socket_count,
                    )
                    break
                except Exception as e:
                    av_log.error(
                        f"Adapter: Error during initialization. Retrying in {SLEEP_ON_ERROR_SECONDS} seconds: {repr(e)}"
                    )
                    num_initial_connection_errors += 1

                    if (
                        num_initial_connection_errors
                        >= MAX_CONNECTION_RETRIES_BEFORE_FAILING
                    ):
                        raise ValueError(
                            f"The maximum number of retries {MAX_CONNECTION_RETRIES_BEFORE_FAILING} to establish an initial connection to AvesTerra server {self.avt_server} has been reached"
                        )

                    if self._stop.wait(SLEEP_ON_ERROR_SECONDS):
                        return

            av_log.success("Connected to AvesTerra")
            self.on_init()
        except BaseException as e:
            av_log.fatal(f"Adapter: Received {repr(e)}. Stopping.")
            self.shutdown()

    @abstractmethod
    def invoke_callback(self, args: av.InvokeArgs) -> AvValue:
        """
        This is the callback that will be invoked by the adapter.
        This is the method that should be implemented by the subclass.
        """
        pass

    @abstractmethod
    def on_init(self):
        """
        This method is called between the av.initialize() and av.adapt_outlet()
        Any exception raised in this method will prevent the adapter from
        starting and will cleanly shutdown.
        This method should set self.outlet to the outlet that will be adapted.
        """
        pass

    @abstractmethod
    def on_shutdown(self):
        """
        This method is called when the adapter is shutting down. right before
        we call av.finalize().
        Typically, you want to call dao.stop(), close connection to db, etc.
        This is the method that should be implemented by the subclass.
        This method is called even if `on_init` raised an exception.
        This method is called before waiting for all the invoke threads
        to return.
        Any exception raised in this method will be ignored.
        """
        pass

    def shutdown(self):
        """
        Stop the adapter, or prevent it from starting if it hasn't started yet
        """
        if self._stop.is_set():
            return

        self._stop.set()
        try:
            self.on_shutdown()
        finally:
            av.finalize()

    def run(self, *args, **kwargs):
        """
        This method will block until the adapter is stopped.
        There are seveal ways to stop the adapter:
        - Send a SIGTERM to the process
        - Call `shutdown()` from another thread
        - Call `av.finalize()` from another thread
        - Raise a `BaseException` from the callback
        """
        del args, kwargs
        assert (
            not self._stop.is_set()
        ), "Adapter: Cannot run an adapter that has been stopped"

        if self.outlet == NULL_ENTITY:
            av_log.fatal("Adapter: No outlet was set before calling `run()`. Aborting.")
            self.shutdown()
            return

        threads = []
        try:
            executor = ThreadPoolExecutor(max_workers=self._thread_count)
            av_log.info(f"Adapter: Running with {self._thread_count} thread(s)...")
            for _ in range(self._thread_count):
                threads.append(executor.submit(self._thread))

            done, _ = futures.wait(threads, return_when=futures.FIRST_EXCEPTION)
            for f in done:
                # Propagate exception to the main thread, if any.
                f.result()
                # If no exception was raised, we are guaranteed that at
                # this point, every single thread has exited without error.

        except KeyboardInterrupt:
            av_log.fatal("Adapter: Received KeyboardInterrupt. Stopping.")
            self.shutdown()
        except BaseException as e:
            av_log.fatal(f"Adapter: Received {repr(e)}. Stopping.")
            self.shutdown()
            futures.wait(threads)
            raise
        finally:
            futures.wait(threads)

    def _thread(self):
        while not self._stop.is_set():
            try:
                av.adapt_outlet(
                    outlet=self.outlet,
                    authorization=self.auth,
                    callback=self._raw_callback,
                )
            except Exception as e:
                if self._stop.is_set():
                    break
                av_log.error(
                    f"Adapter: adapt error, Retrying in {SLEEP_ON_ERROR_SECONDS} seconds: {repr(e)}"
                )
                self._stop.wait(SLEEP_ON_ERROR_SECONDS)

    def _raw_callback(self, args: av.InvokeArgs):
        if self._stop.is_set():
            return AvValue(AvTag.NULL, b"")

        return self.invoke_callback(args)
