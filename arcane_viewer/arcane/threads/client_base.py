"""
    Arcane - A secure remote desktop application for Windows with the
    particularity of having a server entirely written in PowerShell and
    a cross-platform client (Python/QT6).

    Author: Jean-Pierre LESUEUR (@DarkCoderSc)
    License: Apache License 2.0
    https://github.com/PhrozenIO
    https://github.com/DarkCoderSc
    https://twitter.com/DarkCoderSc
    www.phrozen.io
"""

import logging
from abc import abstractmethod

from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

import arcane_viewer.arcane as arcane

logger = logging.getLogger(__name__)


class ClientBaseThread(QThread):
    """ Base class for all client threads """
    thread_finished = pyqtSignal(bool)

    """`Destruction is a form of creation. So the fact they burn the money is ironic. They just want to see what happens
     when they tear the world apart. They want to change things.`, Donnie Darko"""
    def __init__(self, session: arcane.Session, worker_kind: arcane.WorkerKind):
        super().__init__()

        self._running = True
        self._connected = False
        self.session = session
        self.client = None
        self.worker_kind = worker_kind

    def run(self):
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
                on_error = True
        finally:
            if self.client is not None:
                self.client.close()

            self.thread_finished.emit(on_error)

    @abstractmethod
    def client_execute(self):
        pass

    @pyqtSlot()
    def stop(self):
        self._running = False

        if self.client is not None:
            self.client.close()
