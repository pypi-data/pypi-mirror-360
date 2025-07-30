"""
    QApp Platform Project ibm_cloud_device.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  oqc_cloud_device.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from abc import ABC
from time import time

from qcaas_client.client import CompilerConfig, QPUTask
from qiskit.qasm2 import dumps
from quapp_common.config.logging_config import logger
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.enum.status.job_status import JobStatus
from quapp_common.model.device.custom_device import CustomDevice
from quapp_common.model.provider.provider import Provider

from quapp_braket.constant.job_result_const import MEAS
from quapp_braket.constant.job_status_const import COMPLETED, FAILED
from quapp_braket.util.circuit_convert_utils import braket_to_qiskit

logger = logger.bind(context='OqcCloudDevice')


class OqcCloudDevice(CustomDevice, ABC):

    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)

        self.device_specification = device_specification

    def _create_job(self, circuit, options: CircuitRunningOption):
        logger.debug(f"_create_job() with {options.shots} shots")

        start_time = time()

        qiskit_circuit = braket_to_qiskit(circuit)
        qiskit_circuit.measure_all()
        qasm_str = dumps(qiskit_circuit)
        circuit_submit_options = CompilerConfig(repeats=options.shots)

        task = QPUTask(program=qasm_str, config=circuit_submit_options)
        job = self.device.execute_tasks(task, qpu_id=self.device_specification)

        self.execution_time = time() - start_time

        return job

    def _is_simulator(self) -> bool:
        logger.debug("_is_simulator()")

        return True

    def _produce_histogram_data(self, job_result) -> dict | None:
        logger.debug("_produce_histogram_data()")

        return next(iter(job_result.values()))

    def _get_provider_job_id(self, job) -> str:
        logger.debug("_get_provider_job_id()")

        return job[0].id

    def _get_job_status(self, job) -> str:
        logger.debug("_get_job_status()")

        oqc_status = self.device.get_task_status(task_id=job[0].id,
                                                 qpu_id=self.device_specification)
        logger.debug(f"job status: {oqc_status}")

        if FAILED.__eq__(oqc_status):
            return JobStatus.ERROR.value
        elif COMPLETED.__eq__(oqc_status):
            return JobStatus.DONE.value

        return oqc_status

    def _calculate_execution_time(self, job_result):
        logger.debug("_calculate_execution_time()")

        logger.debug(f"Execution time calculation was: {self.execution_time} seconds"
                     )

    def _get_job_result(self, job):
        logger.debug("_get_job_result()")

        return job[0].result

    def _get_shots(self, job_result) -> int | None:
        """
        Retrieve the total number of measurement shots from the job result.

        This method checks if the job result contains measurement data
        and calculates the total number of shots based on the measurement
        results. If the measurement data is not available, the method
        returns None.

        Args:
            job_result: An object representing the result of a job, which
                        may contain measurement results under the 'result'
                        attribute.

        Returns:
            int | None: The total number of shots if measurement data is
                         available; otherwise, None.
        """
        logger.debug("_get_shots()")
        result_meas = getattr(job_result, MEAS, {})
        return sum(result_meas.values()) if result_meas else None
