#  Quapp Platform Project
#  braket_circuit_export_task.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from braket.circuits import Circuit
from qiskit import QuantumCircuit
from quapp_common.async_tasks.export_circuit_task import CircuitExportTask
from quapp_common.config.logging_config import logger

from quapp_braket.util.circuit_convert_utils import braket_to_qiskit

logger = logger.bind(context='BraketCircuitExportTask')


class BraketCircuitExportTask(CircuitExportTask):

    def __init__(self, circuit_data_holder, backend_data_holder):
        super().__init__(circuit_data_holder, backend_data_holder)

    def _transpile_circuit(self) -> QuantumCircuit:
        """
        Transpiles the circuit held in the circuit_data_holder to a Qiskit quantum circuit.

        This method checks if the circuit is an instance of Braket's Circuit. If so, it
        converts it to a Qiskit QuantumCircuit using the braket_to_qiskit utility function.

        Returns:
            QuantumCircuit: Transpiled Qiskit quantum circuit.

        Raises:
            ValueError: If the circuit is not of type Circuit.
        """
        logger.info(f"Transpiling Braket circuit to Qiskit")
        circuit = self.circuit_data_holder.circuit
        if not circuit:
            logger.error(f"Circuit is None")
            raise ValueError("Circuit must not be None")

        if isinstance(circuit, Circuit):
            logger.debug(f"Converting Braket circuit")
            return braket_to_qiskit(circuit)

        logger.error(f"Invalid circuit type: {type(circuit)}")
        raise ValueError(f"Expected Braket Circuit, got {type(circuit)}")
