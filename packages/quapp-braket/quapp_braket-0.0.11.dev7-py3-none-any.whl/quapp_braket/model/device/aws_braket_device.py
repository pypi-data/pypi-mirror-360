#  Quapp Platform Project
#  aws_braket_device.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from dateutil.parser import parse
from quapp_common.config.logging_config import logger
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.enum.status.job_status import JobStatus
from quapp_common.model.device.custom_device import CustomDevice
from quapp_common.model.provider.provider import Provider
import time

from quapp_braket.constant.job_result_const import CREATED_AT, ENDED_AT, SHOTS, TASK_METADATA

logger = logger.bind(context='AwsBraketDevice')


class AwsBraketDevice(CustomDevice):

    def __init__(self, provider: Provider,
                 device_specification: str,
                 s3_bucket_name: str,
                 s3_prefix: str):
        super().__init__(provider, device_specification)
        self.s3_folder = (s3_bucket_name, s3_prefix)

    def _produce_histogram_data(self, job_result) -> dict | None:
        logger.debug("_produce_histogram_data()")

        return dict(job_result.measurement_counts)

    def _get_provider_job_id(self, job) -> str:
        logger.debug("_get_provider_job_id()")

        return job.id

    def _get_job_status(self, job) -> str:
        logger.debug("_get_job_status()")

        job_state = job.state()
        logger.debug(f"job status: {job_state}")

        if JobStatus.COMPLETED.value.__eq__(job_state):
            job_state = JobStatus.DONE.value
        return job_state

    def _calculate_execution_time(self, job_result):
        logger.debug("_calculate_execution_time()")

        if TASK_METADATA not in job_result:
            return

        task_metadata = job_result[TASK_METADATA]

        if task_metadata is None \
                or not bool(task_metadata) \
                or CREATED_AT not in task_metadata \
                or ENDED_AT not in task_metadata:
            return

        created_at = task_metadata[CREATED_AT]
        ended_at = task_metadata[ENDED_AT]

        if created_at is None or ended_at is None:
            return

        created_at = parse(created_at.replace("T", " ").replace("Z", ""))
        ended_at = parse(ended_at.replace("T", " ").replace("Z", ""))

        offset = ended_at - created_at

        self.execution_time = offset.total_seconds()

        logger.debug(f"Execution time calculation was: {self.execution_time} seconds")

    def _get_job_result(self, job):
        logger.debug("_get_job_result()")

        while job.state() not in ['COMPLETED', 'FAILED', 'CANCELLED']:
            logger.debug(f"Job status1: {job.state()}")
            time.sleep(2)

        logger.debug(f"Job status1: {job.state()}")

        return job.result()

    def _create_job(self, circuit, options: CircuitRunningOption):
        logger.debug("_create_job()")

        job = self.device.run(task_specification=circuit,
                              s3_destination_folder=self.s3_folder,
                              shots=options.shots)
        return job

    def _is_simulator(self) -> bool:
        logger.debug("_is_simulator()")

        return True

    def _get_shots(self, job_result) -> int | None:
        """
        Retrieve the number of shots from the job result's task metadata.

        This method checks if the job result contains task metadata and
        retrieves the number of shots if available. If task metadata
        does not exist or does not contain the shots attribute,
        the method returns None.

        Args:
            job_result: An object representing the result of a job, which
                        may contain task metadata with the number of shots.

        Returns:
            int | None: The number of shots if available; otherwise, None.
        """
        logger.debug("_get_shots()")

        return job_result.task_metadata.shots if hasattr(job_result, TASK_METADATA) and hasattr(
            job_result.task_metadata, SHOTS) else None
