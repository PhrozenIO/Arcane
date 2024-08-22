"""
    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    More information about the LICENSE on the LICENSE file in the root directory of the project.
"""

import logging
import traceback
from abc import abstractmethod
from typing import Optional

from PyQt6.QtCore import QMutex, QThread, pyqtSignal, pyqtSlot

import arcane_viewer.arcane as arcane

logger = logging.getLogger(__name__)


class ClientBaseThread(QThread):
    """ Base class for all client threads """
    thread_finished = pyqtSignal(bool)

    """`Destruction is a form of creation. So the fact they burn the money is ironic. They just want to see what happens
     when they tear the world apart. They want to change things.`, Donnie Darko"""
    def __init__(self, session: arcane.Session, worker_kind: arcane.WorkerKind) -> None:
        super().__init__()

        self._running = True
        self._connected = False
        self._mutex = QMutex()

        self.session = session
        self.client: Optional[arcane.Client] = None
        self.worker_kind = worker_kind

    def run(self) -> None:
        on_error = False
        try:
            self.client = self.session.claim_client(self.worker_kind)

            self._connected = True

            # Implement me :-)
            self.client_execute()

            on_error = False

            logger.debug(f"`{self.__class__.__name__}` Thread gracefully ended.")
        except Exception as e:
            if self._running:
                logger.error(f"Thread `{self.__class__.__name__}` encountered an error: `{e}`")
                traceback.print_exc()
                on_error = True
        finally:
            self.stop()

            self.thread_finished.emit(on_error)

    @abstractmethod
    def client_execute(self) -> None:
        pass

    @pyqtSlot()
    def stop(self) -> None:
        self._mutex.lock()
        try:
            if self.client is not None:
                self.client.close()

            self._running = False
        finally:
            self._mutex.unlock()
