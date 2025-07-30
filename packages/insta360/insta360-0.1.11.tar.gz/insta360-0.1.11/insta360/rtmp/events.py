from typing import Optional, Coroutine

import asyncio
import logging
import threading
from collections import defaultdict
from uuid import uuid4


class EventManager:
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
    ):
        self.logger = logger or logging.getLogger(__name__)

        self._registry = defaultdict(dict)
        self._event_loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(
            target=self._run_event_loop,
            daemon=True,
        )
        self._started = False

    def _run_event_loop(self):
        # Set the loop for the current thread
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_forever()

    def _ensure_started(self):
        if self._started:
            return

        self._loop_thread.start()
        self._started = True

    def register_handler(
        self,
        event_name: str,
        handler: Coroutine,
        uid: Optional[str] = None,
        wait: bool = False,
    ):
        """
        Registers a coroutine handler to be called when an event with
        `event_name` is emitted. `uid` may be explicitly provided, otherwise
        will be randomly generated.

        Parameters:
            event_name: Event that the handler will be called upon
            handler: Handler that will be called upon an event
            uid: A unique identifier for a signal receiver in cases where
                 duplicate handlers may be registered.
            wait: If `True`, the event loop will wait until the handler is
                  executed when invoked.

        Returns:
            None
        """
        if not uid:
            uid = "{}-{}".format(handler.__name__, uuid4())

        # Delay thread start until the first event is registered, as there is no
        # point running a thread until it's actually needed
        self._ensure_started()

        self._registry[event_name][uid] = (handler, wait)
        return uid

    def unregister_handler(self, event_name: str, uid: str):
        handler = self._registry[event_name].pop(uid, None)
        removed_handler = handler is not None
        return removed_handler

    def process_event(self, event_name: str, **kwargs):
        handlers = self._registry.get(event_name, {})
        if not handlers:
            return False

        for uid, (event_handler, should_wait) in handlers.items():
            try:
                coro = event_handler(**kwargs)
            except TypeError:
                self.logger.exception(
                    'Error creating a handler coroutine "{}" for event "{}"'.format(
                        event_handler.__name__,
                        event_name,
                    ),
                )
                continue

            future = None
            try:
                future = asyncio.run_coroutine_threadsafe(
                    coro,
                    self._event_loop,
                )
            except Exception as e:
                self.logger.exception(
                    'Error handling event "{}", handler UID={}'.format(
                        event_name,
                        uid,
                    ),
                )

            if should_wait and future is not None:
                try:
                    future.result()
                except:
                    self.logger.exception(
                        "Error occurred while waiting for handler to finish "
                        '("{}") for event "{}"'.format(
                            event_handler.__name__,
                            event_name,
                        ),
                    )
                    pass

        return True
