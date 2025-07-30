from queue import Empty, Queue
from threading import Thread
from typing import Dict, Iterator, Optional

from dateutil.parser import parse as parse_date

from toolforge_weld.kubernetes import K8sClient
from toolforge_weld.logs.source import LogEntry, LogSource

KUBERNETES_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class KubernetesSource(LogSource):
    def __init__(self, *, client: K8sClient) -> None:
        super().__init__()
        self.client = client

    def _get_pod_logs(
        self,
        *,
        pod_name: str,
        container_name: str,
        follow: bool,
        lines: Optional[int],
    ) -> Iterator[LogEntry]:
        params = {
            "container": container_name,
            "follow": follow,
            "pretty": True,
            "timestamps": True,
        }
        if lines:
            params["tailLines"] = lines

        for line in self.client.get_raw_lines(
            "pods",
            name=pod_name,
            subpath="/log",
            params=params,
            version=K8sClient.VERSIONS["pods"],
            timeout=None if follow else self.client.timeout,
        ):
            datetime, message = line.split(" ", 1)
            yield LogEntry(
                pod=pod_name,
                container=container_name,
                datetime=parse_date(datetime),
                message=message,
            )

    def _queue_log_entries(self, queue: Queue[LogEntry], *args, **kwargs) -> None:
        for entry in self._get_pod_logs(*args, **kwargs):
            queue.put(entry)

    def query(
        self, *, selector: Dict[str, str], follow: bool, lines: Optional[int]
    ) -> Iterator[LogEntry]:
        # FIXME: in follow mode, might want to periodically query
        # if there are new pods
        pods = self.client.get_objects(
            "pods",
            label_selector=selector,
        )

        log_queue: Queue[LogEntry] = Queue()
        threads = []

        for pod in pods:
            pod_name = pod["metadata"]["name"]
            for container in pod["spec"]["containers"]:
                container_name = container["name"]
                thread = Thread(
                    target=self._queue_log_entries,
                    kwargs={
                        "pod_name": pod_name,
                        "container_name": container_name,
                        "follow": follow,
                        "lines": lines,
                        "queue": log_queue,
                    },
                    daemon=True,
                )
                thread.start()
                threads.append(thread)

        while (
            follow
            or any(thread.is_alive() for thread in threads)
            or not log_queue.empty()
        ):
            try:
                yield log_queue.get(timeout=0.1)
            except Empty:
                if not follow and not any(thread.is_alive() for thread in threads):
                    break

        if not follow:
            for thread in threads:
                thread.join()
