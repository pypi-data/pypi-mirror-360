import copy
import logging
from typing import Any, Generator, List, Optional, Tuple, cast

import micro_language
from nqs_pycore import TokenMetadata, Wallet

from nqs_sdk.state import StateCERC20
from nqs_sdk.utils.pickable_generator import PickableGenerator, StatefulGenerator
from nqs_sdk_extension.agent.abc_agent import ABCAgent
from nqs_sdk_extension.agent.agent_action import AgentAction, CustomVariable
from nqs_sdk_extension.agent.transaction_helper import TransactionHelper
from nqs_sdk_extension.legacy_workaround import USE_LEGACY_QIS
from nqs_sdk_extension.mappings import ALLOWED_NUMERICAL_ARGS
from nqs_sdk_extension.protocol import ABCProtocol
from nqs_sdk_extension.run_configuration.parameters import CommonParameters

if USE_LEGACY_QIS:
    from legacy_qis.shared_kernel.message_dispatcher import MessageDispatcher, MessageProducer


class BasicAgent(ABCAgent, MessageProducer if USE_LEGACY_QIS else object):  # type: ignore
    def __init__(
        self,
        name: str,
        wallet: Wallet | None = None,
        policy: list[AgentAction] | None = None,
        agent_config: dict | None = None,
        tokens_metadata: list[TokenMetadata | StateCERC20] | None = None,
    ):
        if wallet is None:
            wallet = Wallet(agent_name=name, holdings={}, tokens_metadata={}, erc721_tokens=[])
        self._validate(wallet, policy, agent_config, tokens_metadata)
        if wallet.agent_name != name:
            logging.warning(
                f'User "{name}": The agent\'s name is not the same as the name of the wallet. The name of the wallet '
                f"will be set to {name}."
            )
            wallet.agent_name = name
        super().__init__(wallet, policy if policy is not None else [])
        super(ABCAgent, self).__init__(name)
        self._name = name
        self._agent_config = agent_config
        self._tokens_metadata = tokens_metadata if tokens_metadata is not None else []
        self._custom_variables = self._instantiate_custom_variables()
        self.transaction_helper = TransactionHelper()

    def _validate(
        self,
        wallet: Wallet,
        policy: list[AgentAction] | None,
        agent_config: dict | None,
        tokens_metadata: list[TokenMetadata | StateCERC20] | None,
    ) -> None:
        """Validate the initialization of the agent"""
        if not (
            (not wallet.is_empty() and policy is not None and agent_config is None and tokens_metadata is None)
            or (wallet.is_empty() and policy is None and agent_config is not None and tokens_metadata is not None)
        ):
            raise ValueError(
                "An agent must be initialized either with a wallet and a policy or with a  "
                "configuration dictionary and a list of tokens meta data."
            )
        if agent_config is not None and tokens_metadata is not None:
            metadata_symbols = {metadata.symbol for metadata in tokens_metadata}
            if not set(agent_config["wallet"].keys()).issubset(metadata_symbols):
                raise ValueError(
                    f"The wallet contains unknown symbols: " f"{set(agent_config['wallet'].keys()) - metadata_symbols}"
                )

    def _instantiate_custom_variables(self) -> dict[str, CustomVariable]:
        if self._agent_config is None:
            return {}
        else:
            custom_variables = {
                dic["name"]: CustomVariable(name=dic["name"], value=dic["value"])
                for dic in self._agent_config.get("strategy", {}).get("custom_variables", [])
            }
            return custom_variables

    @property
    def custom_variables(self) -> dict[str, CustomVariable]:
        return self._custom_variables

    def generate_agent_action_from_user_params(
        self, action: dict[str, Any], block_number: int, protocol: ABCProtocol
    ) -> AgentAction:
        args_tx: dict[str, Any] = copy.deepcopy(action["args"])
        args_tx["action_type"] = action["name"]
        args_tx["block_number"] = block_number
        args_tx["protocol_id"] = action["protocol_id"]
        args_tx["protocol"] = protocol
        condition_str: str | None = action.get("condition", None)
        condition_str = None if condition_str == "None" else condition_str
        transactions = self.transaction_helper.generate_transactions_from_user_params(
            args_tx=args_tx, sender_wallet=self._wallet, action_name=action["action_name"]
        )
        custom_variables = [
            CustomVariable(name=dic["name"], value=dic["value"]) for dic in action.get("custom_variables", [])
        ]
        # Here the transaction objects still have the UX fields
        agent_name = self._wallet.agent_name
        return AgentAction(
            transactions=transactions,
            condition_str=condition_str,
            custom_variables=custom_variables,
            block_number=block_number,
            protocol_id=action["protocol_id"],
            agent_name=agent_name,
        )

    def _instantiate_policy(
        self, env_protocols: dict[str, ABCProtocol], env_common_parameters: CommonParameters
    ) -> None:
        if self._agent_config is None:
            return

        self._wallet = Wallet(
            agent_name=self._name,
            holdings=self._agent_config["wallet"],
            erc721_tokens=[],
            tokens_metadata={token_metadata.symbol: token_metadata for token_metadata in self._tokens_metadata},
        )

        self._policy = []
        for event in self._agent_config.get("strategy", {}).get("timed_events", []):
            for action in event["actions"]:
                block_number = self.extract_block_number_from_event(event, env_common_parameters=env_common_parameters)
                agent_action = self.generate_agent_action_from_user_params(
                    action, block_number, env_protocols[action["protocol_id"]]
                )
                self._policy.append(agent_action)

        for event in self._agent_config.get("strategy", {}).get("continuous_events", []):
            for action in event["actions"]:
                if "block_number" in event:
                    # block mode
                    make_txn_on_blocks = [
                        event["block_number"] + i * event["frequency"]
                        for i in range(
                            int((env_common_parameters.block_number_end - event["block_number"]) // event["frequency"])
                            + 1
                        )
                    ]
                elif "timestamp" in event:
                    # timestamp mode
                    make_txn_on_timestamps = [
                        event["timestamp"] + i * event["frequency"]
                        for i in range(
                            int((env_common_parameters.timestamp_end - event["timestamp"]) // event["frequency"]) + 1
                        )
                    ]
                    make_txn_on_blocks = list(
                        self.get_block_number_from_timestamp(
                            make_txn_on_timestamps, env_common_parameters=env_common_parameters
                        )
                    )
                else:
                    raise ValueError("Provide either a block_number or a timestamp for the agent event...")
                for block_number in make_txn_on_blocks:
                    agent_action = self.generate_agent_action_from_user_params(
                        action, block_number, env_protocols[action["protocol_id"]]
                    )
                    self._policy.append(agent_action)

        # filter transactions based on simulation block range
        self._policy = list(
            filter(
                lambda x: env_common_parameters.block_number_start
                <= x.block_number
                <= env_common_parameters.block_number_end,
                self._policy,
            )
        )

        # order the agent's policy
        self._policy = sorted(self._policy, key=lambda x: x.block_number)

    def get_list_tokens_wallet(self) -> list[TokenMetadata | StateCERC20]:
        tokens = self._wallet.tokens_metadata
        return [tokens[token] for token in self._wallet.get_list_tokens()]

    def get_wallet(self) -> Wallet:
        return self._wallet

    if USE_LEGACY_QIS:

        def set_environment(  # type: ignore
            self,
            env_tokens: list[TokenMetadata],
            env_protocols: dict[str, ABCProtocol],
            env_message_dispatcher: MessageDispatcher,
            env_params_microlanguage: Optional[Any],
            env_common_parameters: CommonParameters,
        ) -> None:
            """
            Use the set_environment method to check validity of the tokens in wallet
            and of the protocols the agent operates on
            Set agent transactions block timestamps
            """
            self._set_environment(env_tokens, env_protocols, env_params_microlanguage, env_common_parameters)

            # register as message producer
            self._message_dispatcher = env_message_dispatcher
            self._message_dispatcher.register_producer(self, "TRANSACTIONS")
    else:

        def set_environment(  # type: ignore
            self,
            env_tokens: list[TokenMetadata],
            env_protocols: dict[str, ABCProtocol],
            env_params_microlanguage: Optional[Any],
            env_common_parameters: CommonParameters,
        ) -> None:
            """
            Use the set_environment method to check validity of the tokens in wallet
            and of the protocols the agent operates on
            Set agent transactions block timestamps
            """
            self._set_environment(env_tokens, env_protocols, env_params_microlanguage, env_common_parameters)

    def _set_environment(
        self,
        env_tokens: list[TokenMetadata],
        env_protocols: dict[str, ABCProtocol],
        env_params_microlanguage: Optional[Any],
        env_common_parameters: CommonParameters,
    ) -> None:
        """
        Use the set_environment method to check validity of the tokens in wallet
        and of the protocols the agent operates on
        Set agent transactions block timestamps
        """
        # promote custom variables at initialisation
        self._promote_custom_variables(env_params_microlanguage)

        # instantiate agent's policy
        self._instantiate_policy(env_protocols, env_common_parameters=env_common_parameters)

        # promote agent's conditions
        self._promote_agent_conditions(env_params_microlanguage)

        # promote agent's action arguments
        self._promote_agent_action_arguments(env_params_microlanguage)

        logging.info(f'Agent\'s policy of user "{self._name}" has been created...')

        protected_pairs = {
            "WETH": "ETH",
            "WBTC": "BTC",
        }
        env_token_symbols = {token.symbol for token in env_tokens}
        # check tokens
        tokens_in_wallet: list[TokenMetadata | StateCERC20] = self.get_list_tokens_wallet()
        for token in tokens_in_wallet:
            if token.symbol in protected_pairs and protected_pairs[token.symbol] in env_token_symbols:
                continue
            if token.symbol not in env_token_symbols:
                logging.warning(
                    f'User "{self._name}": Token {token.symbol} is not simulated in the environment. It will be '
                    f"dropped from agent's wallet. "
                )
                self._wallet.drop_token(token.symbol)

        logging.info(f'\nWallet of user "{self._name}" in the environment is: ')
        logging.info(self._wallet)

        # check protocols
        for agent_action in self._policy:
            assert agent_action.protocol_id in env_protocols, (
                f"Agent has an action on protocol {agent_action.protocol_id} " f"that is not part of the environment."
            )

    def _promote_custom_variables(self, env_params_microlanguage: Optional[Any]) -> None:
        for var in self._custom_variables.values():
            if isinstance(var.value, str):
                try:
                    var.value = micro_language.Expression(var.value, env_params_microlanguage)
                except Exception as e:
                    raise ValueError(f"{e} + for expression {var.value}")

    def update_custom_variables(self, custom_variables: list[CustomVariable] | None) -> None:
        if custom_variables is None:
            return
        for var in custom_variables:
            self._custom_variables[var.name] = CustomVariable(name=var.name, value=var.value)

    def produce_next_message(self, **kwargs: Any) -> PickableGenerator:
        policy: list[AgentAction] = self.get_policy()

        def update(
            state: Tuple[BasicAgent, List[AgentAction], int],
        ) -> Tuple[Tuple[BasicAgent, List[AgentAction], int], None]:
            object, policy, index = state
            if index < len(policy):
                agent_action = policy[index]
                object._message_dispatcher.post(
                    producer_id=self.get_producer_id(),
                    topic="TRANSACTIONS",
                    message=agent_action,  # type: ignore
                )
                index += 1
                return (object, policy, index), None
            else:
                raise StopIteration

        return StatefulGenerator((self, policy, 0), update)

    def _promote_agent_conditions(self, env_params_microlanguage: Optional[Any]) -> None:
        """
        Promote agent's conditions_str to micro-language condition objects
        """
        for action in self.get_policy():
            if action.condition_str:
                try:
                    action.condition = micro_language.Condition(action.condition_str, env_params_microlanguage)
                except Exception as e:
                    raise ValueError(f"{e} + for condition {action.condition_str}")
            else:
                action.condition = None

    def _promote_agent_action_arguments(self, env_params_microlanguage: Optional[Any]) -> None:  # noqa #TODO: refactor this function
        """
        Promote agent's action arguments to micro-language expression objects
        """
        for action in self.get_policy():
            for transaction in action.transactions:
                for key, value in transaction.__dict__.items():
                    if key in ALLOWED_NUMERICAL_ARGS and isinstance(value, str):
                        try:
                            transaction.__dict__[key] = micro_language.Expression(value, env_params_microlanguage)
                        except Exception as e:
                            raise ValueError(f"{e} + for expression {value}")
                    elif key in ALLOWED_NUMERICAL_ARGS and isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if isinstance(sub_value, str):
                                try:
                                    transaction.__dict__[key][sub_key] = micro_language.Expression(
                                        sub_value, env_params_microlanguage
                                    )
                                except Exception as e:
                                    raise ValueError(f"{e} + for expression {sub_value}")
            # promote custom variables
            if action.custom_variables:
                for var in action.custom_variables:
                    if isinstance(var.value, str):
                        try:
                            var.value = micro_language.Expression(var.value, env_params_microlanguage)
                        except Exception as e:
                            raise ValueError(f"{e} + for expression {var.value}")

    @staticmethod
    def extract_block_number_from_event(event: dict, env_common_parameters: CommonParameters) -> int:
        if "block_number" in event:
            return cast(int, event["block_number"])
        elif "timestamp" in event:
            timestamp_event = event["timestamp"]
            # then retrieve block number from mapping
            # 1. check that timestamp is in range
            timestamp_min = env_common_parameters.timestamp_start
            timestamp_max = env_common_parameters.timestamp_end
            assert timestamp_min <= timestamp_event <= timestamp_max, (
                f"Event {event['name']} is planned for timestamp {timestamp_event} event, "
                f"outside of the simulation time range ({timestamp_min} to {timestamp_max})..."
            )
            # 2. find the closest block that would contain this timestamp
            closest_block: int = env_common_parameters.block_number_start
            for block_number, block_timestamp in env_common_parameters.mapping_block_number_timestamp.items():
                closest_block = block_number
                if block_timestamp > timestamp_event:
                    break
            return closest_block
        else:
            raise ValueError(f"Agent event {event} has no block_number nor timestamp attribute...")

    @staticmethod
    def get_block_number_from_timestamp(timestamps: list[int], env_common_parameters: CommonParameters) -> Generator:
        timestamp_min = env_common_parameters.timestamp_start
        timestamp_max = env_common_parameters.timestamp_end
        closest_block: int = env_common_parameters.block_number_start
        starting_index: int = 0
        mapping_kv_items = list(env_common_parameters.mapping_block_number_timestamp.items())
        for timestamp in timestamps:
            # 1. check that timestamp is in range
            assert (
                timestamp_min <= timestamp <= timestamp_max
            ), f"Timestamp {timestamp} outside of simulation time range..."
            # 2. find the closest block that would contain this timestamp
            for block_number, block_timestamp in mapping_kv_items[starting_index:]:
                closest_block = block_number
                if block_timestamp > timestamp:
                    break
                starting_index += 1
            yield closest_block
