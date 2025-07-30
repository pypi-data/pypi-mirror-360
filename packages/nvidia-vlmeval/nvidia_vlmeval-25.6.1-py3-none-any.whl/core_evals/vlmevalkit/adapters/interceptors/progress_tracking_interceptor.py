import logging
import threading
from typing import final

import requests

from .types import AdapterResponse, ResponseInterceptor


@final
class ProgressTrackingInterceptor(ResponseInterceptor):
    def __init__(self, progress_tracking_url: str, progress_tracking_interval: int):
        self._progress_tracking_url = progress_tracking_url
        self._progress_tracking_interval = progress_tracking_interval
        self._samples_processed = 0
        self._count_lock = threading.Lock()

    @final
    def intercept_response(self, ar: AdapterResponse) -> AdapterResponse:
        curr_samples = 0
        with self._count_lock:
            self._samples_processed += 1
            curr_samples = self._samples_processed

        if (curr_samples % self._progress_tracking_interval) == 0:
            logging.debug(f"Sending request to {self._progress_tracking_url}: ")
            try:
                requests.post(
                    self._progress_tracking_url,
                    json={"samples_processed": curr_samples},
                )
            except requests.exceptions.RequestException as e:
                logging.error(
                    f"Failed to communicate with progress tracking server: {e}"
                )

        return ar
