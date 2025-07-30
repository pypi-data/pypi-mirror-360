#  Quapp Platform Project
#  invocation_handler.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from quapp_common.config.logging_config import logger
from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.handler.handler import Handler

from ..component.backend.braket_invocation import BraketInvocation

logger = logger.bind(context='InvocationHandler')


class InvocationHandler(Handler):

    def __init__(self, request_data: dict,
                 circuit_preparation_fn,
                 post_processing_fn):
        super().__init__(request_data, post_processing_fn)
        self.circuit_preparation_fn = circuit_preparation_fn

    def handle(self):
        logger.debug(f"Creating InvocationRequest with data: {self.request_data.keys()}")
        invocation_request = InvocationRequest(self.request_data)

        logger.debug("Initializing BraketInvocation backend")
        backend = BraketInvocation(invocation_request)

        logger.debug(f"Submitting job with circuit_preparation_fn={self.circuit_preparation_fn}, "
                     f"post_processing_fn={self.post_processing_fn}")
        backend.submit_job(circuit_preparation_fn=self.circuit_preparation_fn,
                           post_processing_fn=self.post_processing_fn)
