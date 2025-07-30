#  Quapp Platform Project
#  braket_job_fetching.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
from abc import ABC

import numpy as np
from botocore.exceptions import ClientError
from dateutil.parser import parse
from quapp_common.component.backend.job_fetcher import JobFetcher
from quapp_common.config.logging_config import logger
from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.enum.status.job_status import JobStatus

from quapp_braket.constant.authentication_const import REGION_NAME
from quapp_braket.constant.job_result_const import CREATED_AT, ENDED_AT, \
    MEASUREMENTS, METADATA, \
    OUTPUT_S3_BUCKET, OUTPUT_S3_DIRECTORY, RESULTS_JSON, SHOTS
from quapp_braket.constant.job_status_const import COMPLETED, FAILED, STATUS
from quapp_braket.factory.braket_provider_factory import create_provider
from quapp_braket.util.braket_utils import get_braket_client, read_s3_content
from quapp_braket.util.provider_job_utils import get_region, is_valid_job_arn, \
    is_valid_quantum_task_arn

logger = logger.bind(context='BraketJobFetching')


class BraketJobFetching(JobFetcher, ABC):

    def __init__(self, request_data: JobFetchingRequest):
        super().__init__(request_data)

    def _collect_provider(self):
        """
        Collects the provider by creating an AwsBraketProvider instance.

        This method sets the 'regionName' in the provider authentication,
        creates the provider using the BraketProviderFactory, and retrieves
        the provider instance.

        :return: The provider instance is collected from the provider
        """
        job_id = self.provider_job_id
        logger.info(f"[{job_id}] Collecting AWS Braket provider")

        # Get and update a region
        job_region = get_region(job_id)
        self.provider_authentication[REGION_NAME] = job_region
        logger.debug(f"[{job_id}] Using region: {job_region}")

        # Create and collect provider
        try:
            provider_spec = create_provider(
                    provider_type=ProviderTag.AWS_BRAKET,
                    sdk=Sdk.BRAKET,
                    authentication=self.provider_authentication
            )

            provider_instance = provider_spec.collect_provider()
            logger.info(
                    f"[{job_id}] Provider instance collected: {provider_instance}")
            return provider_instance
        except ClientError as e:
            logger.error(
                    f"[{job_id}] Failed to create/collect provider: {str(e)}")
            raise ValueError(f"Failed to create/collect provider: {str(e)}")

    def _retrieve_job(self, provider):
        """
        Retrieves a job from Braket given a provider_job_id.

        :param provider: The AWS Session to use for interacting with Braket
        :return: The retrieved job
        """
        job_id = self.provider_job_id
        logger.info(f'[{job_id}] _retrieve_job() started')

        braket_client = get_braket_client(session=provider)
        logger.debug(f'[{job_id}] Braket client obtained')

        # Define job type and validation/retrieval mappings
        job_configs = {
            "quantum-task": {
                "validator": is_valid_quantum_task_arn,
                "retriever": braket_client.get_quantum_task,
                "arn_key": "quantumTaskArn"
            },
            "job": {
                "validator": is_valid_job_arn,
                "retriever": braket_client.get_job,
                "arn_key": "jobArn"
            }
        }

        # Determine a job type and retrieve a job / task
        for job_type, config in job_configs.items():
            if job_type in job_id:
                if not config["validator"](job_id):
                    logger.error(f"[{job_id}] Invalid {job_type} ARN")
                    raise ValueError(f"Invalid {job_type} ARN: {job_id}")

                logger.info(f"[{job_id}] Retrieving {job_type} with ARN")
                job = config["retriever"](**{config["arn_key"]: job_id})
                logger.info(
                        f"[{job_id}] {job_type.capitalize()} retrieved successfully")
                return job

        # Handle an invalid job type
        logger.error(f"[{job_id}] No valid job type found")
        raise ValueError(
                f"No valid job type found for provider_job_id: {job_id}")

    def _get_job_status(self, job):
        """
        Retrieves the job status from the retrieved job object.

        Args:
            job: The job object retrieved from Braket

        Returns:
            str: The job status mapped to a job status
        """
        job_id = self.provider_job_id
        logger.info(f'[{job_id}] _get_job_status() started')

        # Use a mapping dictionary for status conversion
        status_mapping = {
            COMPLETED: JobStatus.DONE.name,
            FAILED: JobStatus.ERROR.name
        }

        # Retrieve the status using dict.get() and map it
        status = status_mapping.get(job.get(STATUS))

        logger.info(f'[{job_id}] _get_job_status() started')
        return status

    def _get_job_result(self, job):
        """
        Retrieves the job result from an S3 bucket.

        This function logs the retrieval process and fetches the result
        of the job specified in the input parameter from an S3 bucket.
        The result is stored in a JSON file located in the specified
        directory of the bucket.

        Args:
            job (dict): Dictionary containing job details, including
                        'outputS3Bucket' and 'outputS3Directory'.

        Returns:
            dict: The contents of the result JSON file retrieved from S3.
        """
        job_id = self.provider_job_id
        logger.info(f'[{job_id}] _get_job_result() started')

        if OUTPUT_S3_BUCKET not in job or OUTPUT_S3_DIRECTORY not in job:
            logger.error(
                    f'[{job_id}] {OUTPUT_S3_BUCKET} or {OUTPUT_S3_DIRECTORY} not found in job')
            raise ValueError(
                    f'{OUTPUT_S3_BUCKET} or {OUTPUT_S3_DIRECTORY} not found in job')

        logger.info(
                f'[{job_id}] Fetching job result from S3 bucket: {job[OUTPUT_S3_BUCKET]}')
        job_result = read_s3_content(
                authentication=self.provider_authentication,
                bucket_name=job[OUTPUT_S3_BUCKET],
                object_key=job[OUTPUT_S3_DIRECTORY] + '/' + RESULTS_JSON)

        logger.info(
                f'[{job_id}] Job result retrieved successfully with content: {job_result}')
        return job_result

    def _produce_histogram_data(self, job_result) -> dict | None:
        """
        Produces a histogram data given a job result.

        Args:
            job_result (dict): A dictionary containing the job result from Braket.

        Returns:
            dict | None: A dictionary containing the counts of values 0 and 1, or None
                         if an error occurred.
        """
        job_id = self.provider_job_id
        logger.info(f'[{job_id}] _produce_histogram_data() started')

        try:
            logger.debug(
                    f"[{job_id}] Job result measurements: {job_result.get(MEASUREMENTS)}")
            measurements = np.array(job_result.get(MEASUREMENTS, []))

            # Check if measurements is empty
            if measurements.size == 0:
                logger.debug(
                        '[{job_id}] Measurements array is empty, returning default histogram.')
                return {"0": 0, "1": 0}

            # Flatten the array if it is not one-dimensional
            if measurements.ndim > 1:
                logger.debug(
                        f'[{job_id}] Measurements array is multi-dimensional, flattening to: {measurements.flatten()}')
                measurements = measurements.flatten()

            # Count the occurrences of each value (0 and 1) in the sample
            counts = np.bincount(measurements, minlength=2)
            logger.debug(f'[{job_id}] Counts of 0 and 1: {counts}')

            # Return a dictionary with the counts of values 0 and 1
            histogram_data = {"0": int(counts[0]), "1": int(counts[1])}
            logger.info(
                    f'[{job_id}] _produce_histogram_data() completed successfully')
            return histogram_data

        except Exception as exception:
            logger.debug(
                    f"[{job_id}] Can't produce histogram with error: {exception}")
            return None

    def _get_execution_time(self, job_result):
        """
        Retrieves the execution time in seconds from a job result.

        :param job_result: A dictionary containing the job result from Braket.
        :return: The execution time in seconds, or None if it can't be retrieved.
        """
        job_id = self.provider_job_id
        logger.debug(
                f'[{job_id}] Getting execution time for job_result: {job_result}')

        metadata = job_result.get(METADATA)
        if not metadata:
            logger.debug(f"[{job_id}] '{METADATA}' not found in job_result.")
            return None

        created_at_str = metadata.get(CREATED_AT)
        ended_at_str = metadata.get(ENDED_AT)

        if not created_at_str or not ended_at_str:
            logger.debug(
                    f"[{job_id}] '{CREATED_AT}' or '{ENDED_AT}' not found in '{METADATA}'.")
            return None

        try:
            created_at = parse(
                    created_at_str.replace("T", " ").replace("Z", ""))
            ended_at = parse(ended_at_str.replace("T", " ").replace("Z", ""))
            offset = ended_at - created_at
            execution_time = offset.total_seconds()
            logger.info(
                    f'[{job_id}] Execution time calculated: {execution_time} seconds.')
            return execution_time
        except ValueError:
            logger.warning(
                    f"[{job_id}] Failed to parse timestamp: created_at='{created_at_str}', ended_at='{ended_at_str}'.")
            return None

    def _get_shots(self, job_result):
        """
        Retrieves the number of shots from the job result's task metadata.

        This method checks if the job result contains task metadata and
        retrieves the number of shots if available. If task metadata
        does not exist or does not contain the shot attribute,
        the method returns None.

        Args:
            job_result: A dictionary containing the job result from Braket.

        Returns:
            int | None: The number of shots if available; otherwise, None.
        """
        job_id = self.provider_job_id
        logger.info(
                f'[{job_id}] _get_shots() started with job_result: {job_result}')

        task_metadata = job_result.get(METADATA)
        if task_metadata:
            logger.debug(f'[{job_id}] Found task_metadata: {task_metadata}')
            shots = getattr(task_metadata, SHOTS, None)
            logger.debug(f'[{job_id}] Found shots: {shots}')
            logger.info(f'[{job_id}] _get_shots() completed successfully')
            return shots
        else:
            logger.debug(f'[{job_id}] "{METADATA}" not found in job_result.')

        logger.debug(f'[{job_id}] Returning None for shots.')
        return None
