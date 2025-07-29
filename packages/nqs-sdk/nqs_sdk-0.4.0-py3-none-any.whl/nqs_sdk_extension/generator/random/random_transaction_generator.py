from abc import abstractmethod
from typing import Any, Optional, Tuple

from nqs_sdk.utils.pickable_generator import PickableGenerator, StatefulGenerator
from nqs_sdk_extension.generator.abc_generator import ABCSoloGenerator
from nqs_sdk_extension.generator.random.random_generator import RandomGenerator
from nqs_sdk_extension.legacy_workaround import USE_LEGACY_QIS
from nqs_sdk_extension.observer.abc_observer import ABCObserver
from nqs_sdk_extension.state import ABCProtocolState
from nqs_sdk_extension.transaction.abc_transaction import ABCTransaction

if USE_LEGACY_QIS:
    from legacy_qis.shared_kernel.message_dispatcher import MessageDispatcher


class RandomTransactionGenerator(ABCSoloGenerator):
    """
    A class that generates random transactions for a given block range.

    Args:
        id (int): The ID of the generator.
        name (str): The name of the generator.
        random_generation_parameters (dict): The parameters for random transaction generation.
        random_generator (RandomGenerator): The random number generator.
        additional_parameters (dict, optional): Additional parameters for the generator that are protocol specific.

    Attributes:
        random_generation_parameters (dict): The parameters for random transaction generation.
        random_generator (RandomGenerator): The random number generator.
        additional_parameters (dict): Additional parameters for the generator.
        _protocol_id (str): The protocol ID that maps the generator to a protocol in the environment.

    """

    def __init__(
        self,
        id: int,
        name: str,
        type: str,
        random_generation_parameters: dict[str, Any],
        random_generator: RandomGenerator,
        mapping_block_timestamps: dict[int, int],
        additional_params: Optional[dict] = None,
    ):
        super().__init__(id, name)
        self.type = type
        self.random_generation_parameters = random_generation_parameters
        self.random_generator = random_generator
        # the mapping dictionary is needed for generators with seasonality components
        self.mapping_block_timestamps = mapping_block_timestamps
        self._protocol_id: str

    def set_seed(self, seed: int, use_antithetic_variates: bool) -> None:
        """
        Set the seed of the RandomGenerator.
        """
        self.random_generator.set_seed(seed, use_antithetic_variates)

    @property
    @abstractmethod
    def transaction_types(self) -> list[str]:
        """
        Get the list of transaction types.

        Returns:
            list[str]: The list of transaction types.

        """
        pass

    @abstractmethod
    def generate_transaction_at_block(self, transaction_type: str, **kwargs: Any) -> ABCTransaction:
        """
        Get the mapping of transaction types to functions.

        Returns:
            ABCTransaction: The generated transaction.

        """
        pass

    if USE_LEGACY_QIS:

        def set_environment(  # type: ignore[override]
            self, env_protocol_id: str, env_message_dispatcher: MessageDispatcher, env_observer: ABCObserver
        ) -> None:
            """
            Sets the environment mapping from block number to timestamp and the protocol id that the gen maps to
            """
            self._protocol_id = env_protocol_id
            self._message_dispatcher = env_message_dispatcher
            self._message_dispatcher.register_producer(self, "TRANSACTIONS")
            self._observer = env_observer
            self.validate_observer()

    @abstractmethod
    def validate_observer(self) -> None:
        """
        This function should be used in protocol transaction generators
        to validate that the observer is of the correct type.
        """
        pass

    def generate_transactions_at_block_by_type(self, block_number: int, transaction_type: str) -> ABCTransaction:
        """
        Generate transactions of a specific type at a given block number.

        Args:
            block_number (int): The block number.
            transaction_type (str): The transaction type.

        Returns:
            ABCTransaction: The generated transaction.

        """
        value_dict = self.generate_transactions_values(transaction_type)
        transaction = self.generate_transaction_at_block(
            transaction_type, block_number=block_number, value_dict=value_dict
        )
        return transaction

    def generate_transactions_between_blocks(
        self, block_number_from: int, block_number_to: int
    ) -> list[ABCTransaction]:
        raise NotImplementedError("This method is no longer implemented for random generators")

    def generate_transactions_at_block(self, block_number: int) -> list[ABCTransaction]:
        raise NotImplementedError("This method should not be implemented for RandomTransactionGenerator")

    def generate_state_at_block(self, block_number: int) -> ABCProtocolState:
        raise NotImplementedError("This method should not be implemented for RandomTransactionGenerator")

    def compare_two_states(self, state_left: ABCProtocolState, state_right: ABCProtocolState) -> None:
        raise NotImplementedError("This method should not be implemented for RandomTransactionGenerator")

    def get_frequency_params_per_transaction_type(
        self, random_generation_parameters: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Get the frequency parameters for each transaction type.
        """
        frequency_params_per_transaction_type = {}
        for transaction_type in self.transaction_types:
            transaction_type_parameters = random_generation_parameters.get(transaction_type, {})
            if not transaction_type_parameters:
                continue
            frequency = transaction_type_parameters["frequency"]

            if len(list(frequency.items())) != 1:
                raise ValueError(
                    f"""Frequency dictionary should have only one item of the form
                    {"my_process: {param1: value1, param2: value2}"}, but got {frequency} instead."""
                )

            frequency_process, frequency_params = list(frequency.items())[0]

            if not isinstance(frequency_params, dict) or not isinstance(frequency_process, str):
                raise ValueError(
                    f"""Frequency dictionary should be of the form
                        {"my_process: {param1: value1, param2: value2}"}, but got {frequency} instead."""
                )
            frequency_params_per_transaction_type[transaction_type] = (frequency_process, frequency_params)

        return frequency_params_per_transaction_type

    if USE_LEGACY_QIS:

        def produce_next_message(self, **kwargs: Any) -> PickableGenerator:
            """
            Sends the next generated transaction to the message dispatcher.

            Args:
                **kwargs (Any): Additional keyword arguments.

            Yields:
                Generator: The generated transactions.

            """
            block_number_from = kwargs["block_number_from"]
            block_number_to = kwargs["block_number_to"]
            total_block_number = block_number_to - block_number_from
            frequency_params_per_transaction_type = self.get_frequency_params_per_transaction_type(
                self.random_generation_parameters
            )
            next_block_by_transaction_type = {
                transaction_type: block_number_from - 1 for transaction_type in self.transaction_types
            }
            pending_transactions_by_block: dict[int, list[ABCTransaction]] = {}
            nb_of_pending_txn: int = 0
            remaining_transaction_types = len(self.transaction_types)

            def update(
                state: Tuple[
                    RandomTransactionGenerator, int, dict[str, int], int, dict[int, list[ABCTransaction]], int, int
                ],
            ) -> Tuple[
                Tuple[RandomTransactionGenerator, int, dict[str, int], int, dict[int, list[ABCTransaction]], int, int],
                None,
            ]:
                (
                    transaction_generator,
                    current_block_number,
                    next_block_by_transaction_type,
                    transaction_type_index,
                    pending_transactions_by_block,
                    nb_of_pending_txn,
                    remaining_transaction_types,
                ) = state
                # iterate over all blocks
                while current_block_number < block_number_to:
                    # iterate over all transaction types
                    while transaction_type_index < len(transaction_generator.transaction_types):
                        transaction_type = transaction_generator.transaction_types[transaction_type_index]
                        # Check if there is already a transaction pending for this transaction type
                        # if so, there is no need to generate a new one
                        if current_block_number < next_block_by_transaction_type[transaction_type]:
                            transaction_type_index += 1
                            continue

                        frequency_process, frequency_params = frequency_params_per_transaction_type[transaction_type]
                        number_of_blocks_until_next_transaction = self.generate_next_transaction_time(
                            frequency_process, frequency_params, total_block_number
                        )

                        # if there are transactions due for the same block as the current one
                        # we need to generate them while the next one is not until another block
                        while number_of_blocks_until_next_transaction < 1:
                            next_transaction_block = current_block_number
                            (
                                pending_transactions_by_block,
                                next_block_by_transaction_type,
                                nb_of_pending_txn,
                            ) = self.generate_and_store_transaction(
                                next_transaction_block,
                                transaction_type,
                                pending_transactions_by_block,
                                next_block_by_transaction_type,
                                nb_of_pending_txn,
                            )
                            number_of_blocks_until_next_transaction += self.generate_next_transaction_time(
                                frequency_process, frequency_params, total_block_number
                            )

                        next_transaction_block = current_block_number + round(number_of_blocks_until_next_transaction)
                        # if the next transaction block is after the last block,
                        #   we need to stop for this transaction type
                        if next_transaction_block > block_number_to:
                            next_block_by_transaction_type[transaction_type] = block_number_to
                            transaction_type_index += 1
                            remaining_transaction_types -= 1
                            continue

                        (
                            pending_transactions_by_block,
                            next_block_by_transaction_type,
                            nb_of_pending_txn,
                        ) = self.generate_and_store_transaction(
                            next_transaction_block,
                            transaction_type,
                            pending_transactions_by_block,
                            next_block_by_transaction_type,
                            nb_of_pending_txn,
                        )

                        transaction_type_index += 1

                    # If there are at least as many pending transactions as there are transaction types
                    # Then we are sure that there is at least one transaction for each transaction type
                    # this latter condition is harder to check on its own because transaction objects
                    # are not self aware of their type currently.
                    if nb_of_pending_txn >= max(remaining_transaction_types, 1):
                        pending_transactions_by_block, nb_of_pending_txn = _send_transaction(
                            transaction_generator, pending_transactions_by_block, nb_of_pending_txn
                        )
                        return (
                            transaction_generator,
                            current_block_number,
                            next_block_by_transaction_type,
                            transaction_type_index,
                            pending_transactions_by_block,
                            nb_of_pending_txn,
                            remaining_transaction_types,
                        ), None

                    current_block_number = min(next_block_by_transaction_type.values())
                    if current_block_number == block_number_to:
                        # if we are at the last block, we need to send the remaining transactions
                        while nb_of_pending_txn > 0:
                            pending_transactions_by_block, nb_of_pending_txn = _send_transaction(
                                transaction_generator, pending_transactions_by_block, nb_of_pending_txn
                            )
                        return (
                            transaction_generator,
                            current_block_number,
                            next_block_by_transaction_type,
                            transaction_type_index,
                            pending_transactions_by_block,
                            nb_of_pending_txn,
                            remaining_transaction_types,
                        ), None

                    transaction_type_index = 0
                raise StopIteration

            return StatefulGenerator(
                (
                    self,
                    block_number_from,
                    next_block_by_transaction_type,
                    0,
                    pending_transactions_by_block,
                    nb_of_pending_txn,
                    remaining_transaction_types,
                ),
                update,
            )

    def generate_and_store_transaction(
        self,
        next_transaction_block: int,
        transaction_type: str,
        pending_transactions_by_block: dict[int, list[ABCTransaction]],
        next_block_by_transaction_type: dict[str, int],
        nb_of_pending_txn: int,
    ) -> Tuple[dict[int, list[ABCTransaction]], dict[str, int], int]:
        """
        Generate a transaction and store it in the pending transactions by block dictionary.
        """
        transaction = self.generate_transactions_at_block_by_type(next_transaction_block, transaction_type)
        pending_transactions_by_block.setdefault(next_transaction_block, []).append(transaction)
        next_block_by_transaction_type[transaction_type] = next_transaction_block
        nb_of_pending_txn += 1
        return pending_transactions_by_block, next_block_by_transaction_type, nb_of_pending_txn

    def generate_transactions_values(self, transaction_type: str) -> dict[str, float]:
        """
        Generate transaction values for a given transaction type. The values are generated using
        various random processes and parameters that are specified in parameters file.

        Args:
            transaction_type (str): The transaction type.

        Returns:
            dict[str, float]: The dictionary mapping values to their corresponding generated values.

        """
        value_dict = {}
        for value_type in self.random_generation_parameters[transaction_type].get("values", {}).keys():
            value = self.random_generation_parameters[transaction_type]["values"][value_type]
            value_process, value_params = list(value.items())[0]
            value_dict[value_type] = next(self.random_generator.process_dict[value_process].draw_single(**value_params))
        return value_dict

    def generate_next_transaction_time(
        self, frequency_process: str, frequency_params: dict, simulation_length_in_blocks: int
    ) -> Any:
        """
        Generate the next transaction time using a random process and its parameters.

        Args:
            frequency_params (dict): The parameters for the random process.
            simulation_length_in_blocks (int): The length of the block.

        Returns:
            int: The next transaction time.

        """
        return next(
            self.random_generator.process_dict[frequency_process].draw_single(
                **frequency_params, simulation_length_in_blocks=simulation_length_in_blocks
            )
        )


if USE_LEGACY_QIS:

    def _send_transaction(
        transaction_generator: RandomTransactionGenerator,
        pending_transactions_by_block: dict[int, list[ABCTransaction]],
        nb_of_pending_txn: int = 0,
    ) -> Tuple[dict[int, list[ABCTransaction]], int]:
        """
        Send the next transaction to the message dispatcher,
        remove it from the pending transactions by block dictionary and
        decrement the number of pending transactions.
        """
        next_transaction_block = min(pending_transactions_by_block.keys())
        next_transaction = pending_transactions_by_block[next_transaction_block].pop(0)
        if len(pending_transactions_by_block[next_transaction_block]) == 0:
            pending_transactions_by_block.pop(next_transaction_block)
        transaction_generator._message_dispatcher.post(
            producer_id=transaction_generator.get_producer_id(),
            topic="TRANSACTIONS",
            message=next_transaction,  # type: ignore
        )
        nb_of_pending_txn -= 1
        return pending_transactions_by_block, nb_of_pending_txn
