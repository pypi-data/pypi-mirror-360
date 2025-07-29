# type: ignore

import copy
import unittest

import pytest
from nqs_pycore import TokenMetadata, Wallet

from nqs_sdk_extension.protocol import Comptroller
from nqs_sdk_extension.state.compoundv2 import (
    BorrowSnapshot,
    StateCompoundMarket,
    StateComptroller,
    StateInterestRateModel,
)
from nqs_sdk_extension.transaction.compoundv2 import TransactionHelperCompoundv2

tran_helper = TransactionHelperCompoundv2()


def dummy_metadata(id: int, decimal: int):
    return TokenMetadata(f"token{id}", f"USD{id}", decimal)


class TestComptrollerMethods(unittest.TestCase):
    holdings = {"ETH": 10, "USDT": 10_000, "cETH": 30_000, "cUSDC": 5_000}
    tokens_metadata = {
        "ETH": dummy_metadata(1, 18),
        "USDC": dummy_metadata(2, 6),
        "cETH": dummy_metadata(3, 8),
        "cUSDC": dummy_metadata(4, 8),
    }
    my_address = "UserWallet"

    market_1_state = StateCompoundMarket(
        id=0,
        name="Compound market 1",
        block_number=0,
        block_timestamp=0,
        symbol="cUSDC",
        address="0x1",
        underlying="USDC",
        underlying_address="0x01",
        underlying_decimals=6,
        interest_rate_model=StateInterestRateModel(
            multiplier_per_block=20_000_000_000,
            base_rate_per_block=0,
            jump_multiplier_per_block=500_000_000_000,
            kink=800_000_000_000_000_000,
        ),
        decimals=8,
        initial_exchange_rate_mantissa=200_000_000_000_000,
        accrual_block_number=2,
        reserve_factor_mantissa=450_000_000_000_000_000,
        borrow_index=101,
        total_borrows=120_000_000_000_000,
        total_supply=int(6.8e17),
        total_reserves=16_000_000_000_000,
        collateral_factor=500_000_000_000_000_000,
        borrow_cap=0,
        account_borrows={
            "UserWallet": BorrowSnapshot(principal=100 * 10**6, interest_index=100),
            "remaining": BorrowSnapshot(principal=10000 * 10**6, interest_index=100),
        },
        total_cash=32_000_000_000_000,
    )

    market_2_state = StateCompoundMarket(
        id=2,
        name="Compound market 2",
        block_number=0,
        block_timestamp=0,
        symbol="cETH",
        address="0x2",
        underlying="ETH",
        underlying_address="0x02",
        underlying_decimals=18,
        interest_rate_model=StateInterestRateModel(
            multiplier_per_block=85_000_000_000,
            base_rate_per_block=7_000_000_000,
            jump_multiplier_per_block=18_000_000_000_000,
            kink=800_000_000_000_000_000,
        ),
        decimals=8,
        initial_exchange_rate_mantissa=200_000_000_000_000,
        accrual_block_number=2,
        reserve_factor_mantissa=200_000_000_000_000_000,
        borrow_index=101,
        total_borrows=6_000_000_000_000_000_000_000,
        total_supply=1_025_900_000_000_000,
        total_reserves=820_000_000_000_000_000_000,
        collateral_factor=800_000_000_000_000_000,
        borrow_cap=100_000_000_000_000_000_000_000,
        account_borrows={
            "UserWallet": BorrowSnapshot(principal=10**18, interest_index=100),
            "remaining": BorrowSnapshot(principal=100 * 10**18, interest_index=100),
        },
        total_cash=200_000_000_000_000_000_000_000,
    )

    comptroller_state = StateComptroller(
        id=3,
        name="comptroller",
        block_number=0,
        block_timestamp=0,
        close_factor_mantissa=500_000_000_000_000_000,
        liquidation_incentive_mantissa=1_080_000_000_000_000_000,
        max_assets=20,
        market_states={"cUSDC": market_1_state, "cETH": market_2_state},
    )

    def test_hypothetical_account_liquidity(self):
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )

        liquidity_no_act, _ = comptroller.get_hypothetical_account_liquidity(
            wallet1, "cUSDC", 0, 0, comptroller._stored_spot
        )
        liquidity, shortfall = comptroller.get_hypothetical_account_liquidity(
            wallet1, "cUSDC", 5 * 10**8, 0, comptroller._stored_spot
        )
        assert shortfall == 0
        assert liquidity == 427940000000000000000
        assert liquidity_no_act == 427990000000000000000

        liquidity_borrow, shortfall_borrow = comptroller.get_hypothetical_account_liquidity(
            wallet1, "cUSDC", 0, 500 * 10**6, comptroller._stored_spot
        )
        assert shortfall_borrow == 72010000000000000000
        assert liquidity_borrow == 0

    def test_redeem_allowed(self):
        # same setting as before
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )

        is_allowed, _ = comptroller.redeem_allowed("cUSDC", wallet1, 5 * 10**8)
        assert is_allowed

        is_allowed, message = comptroller.redeem_allowed("cUSDC", wallet1, 50000 * 10**8)
        assert not is_allowed

        wallet1.drop_token("cUSDC")
        is_allowed, message = comptroller.redeem_allowed("cUSDC", wallet1, 50000 * 10**8)
        assert is_allowed

    def test_borrow_allowed(self):
        # same setting as before
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )

        is_allowed, message = comptroller.borrow_allowed("cUSDC", wallet1, 500 * 10**6)
        assert not is_allowed

    def test_borrow_cap_check(self):
        comptroller = Comptroller(state=self.comptroller_state)
        is_allowed, message = comptroller.borrow_cap_check(
            "cETH", self.comptroller_state.market_states["cETH"].borrow_cap
        )
        assert not is_allowed
        assert message == "Impossible to borrow 100000.0ETH. The borrow cap (100000.0ETH) would be breached."

    def test_liquidate_allowed(self):
        # same setting as before
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )

        is_allowed, message = comptroller.liquidate_borrow_allowed("cETH", wallet1, 10)
        assert not is_allowed
        assert (
            message == "Liquidation failed because of insufficient shortfall. The account has a positive balance "
            "of 427.99 USDC"
        )

        # underwater wallet
        wallet1 = Wallet(
            holdings={"ETH": 10, "USDT": 10_000, "cETH": 3_000, "cUSDC": 5_000},
            tokens_metadata=self.tokens_metadata,
            erc721_tokens=[],
            agent_name=self.my_address,
        )
        is_allowed, _ = comptroller.liquidate_borrow_allowed("cUSDC", wallet1, 50 * 10**6)
        assert is_allowed

        wallet1 = Wallet(
            holdings={"ETH": 10, "USDT": 10_000, "cETH": 3_000, "cUSDC": 5_000},
            tokens_metadata=self.tokens_metadata,
            agent_name=self.my_address,
            erc721_tokens=[],
        )
        is_allowed, message = comptroller.liquidate_borrow_allowed("cUSDC", wallet1, 55.1 * 10**6)
        assert not is_allowed
        assert (
            message == "It is not possible to liquidate more than what is specified by the close factor. "
            "Trying to repay 55.1USDC, while the maximum amount is 50.5"
        )

    def test_liquidate_calculate_seize_token(self):
        # same setting as before
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        liquidate_amount = 10 * 10**18
        seize_tokens = comptroller.liquidate_calculate_seize_token(
            "cETH", "cUSDC", liquidate_amount, comptroller._stored_spot
        )
        assert seize_tokens * 0.02 / 10**8 - liquidate_amount * comptroller.liquidation_incentive_mantissa / 10**36 == 0


class TestCTokenMethods(unittest.TestCase):
    holdings = {"ETH": 10, "USDT": 10_000, "cETH": 30_000, "cUSDC": 5_000}
    underwater_holdings = {"cETH": 2_000, "cUSDC": 5_000}
    tokens_metadata = {
        "ETH": dummy_metadata(1, 18),
        "USDC": dummy_metadata(2, 6),
        "cETH": dummy_metadata(3, 8),
        "cUSDC": dummy_metadata(4, 8),
    }
    my_address = "UserWallet"

    market_1_state = StateCompoundMarket(
        id=0,
        name="Compound market 1",
        block_number=0,
        block_timestamp=0,
        symbol="cUSDC",
        address="0x1",
        underlying="USDC",
        underlying_address="0x01",
        underlying_decimals=6,
        interest_rate_model=StateInterestRateModel(
            multiplier_per_block=20_000_000_000,
            base_rate_per_block=0,
            jump_multiplier_per_block=500_000_000_000,
            kink=800_000_000_000_000_000,
        ),
        decimals=8,
        initial_exchange_rate_mantissa=200_000_000_000_000,
        accrual_block_number=2,
        reserve_factor_mantissa=450_000_000_000_000_000,
        borrow_index=1_000_000_000_000_000_000,
        total_borrows=120_000_000_000_000,
        total_supply=int(6.8e17),
        total_reserves=16_000_000_000_000,
        collateral_factor=500_000_000_000_000_000,
        borrow_cap=0,
        account_borrows={
            "UserWallet": BorrowSnapshot(principal=100 * 10**6, interest_index=1_000_000_000_000_000_000),
            "remaining": BorrowSnapshot(principal=10000 * 10**6, interest_index=1_000_000_000_000_000_000),
        },
        total_cash=32_000_000_000_000,
    )

    market_2_state = StateCompoundMarket(
        id=2,
        name="Compound market 2",
        block_number=0,
        block_timestamp=0,
        symbol="cETH",
        address="0x2",
        underlying="ETH",
        underlying_address="0x02",
        underlying_decimals=18,
        interest_rate_model=StateInterestRateModel(
            multiplier_per_block=85_000_000_000,
            base_rate_per_block=7_000_000_000,
            jump_multiplier_per_block=18_000_000_000_000,
            kink=800_000_000_000_000_000,
        ),
        decimals=8,
        initial_exchange_rate_mantissa=200_000_000_000_000,
        accrual_block_number=2,
        reserve_factor_mantissa=200_000_000_000_000_000,
        borrow_index=1_000_000_000_000_000_000,
        total_borrows=49_795_000_000_000_000_000_000,
        total_supply=1_025_900_000_000_000,
        total_reserves=820_000_000_000_000_000_000,
        collateral_factor=800_000_000_000_000_000,
        borrow_cap=100_000_000_000_000_000_000_000,
        account_borrows={
            "UserWallet": BorrowSnapshot(principal=10**18, interest_index=1_000_000_000_000_000_000),
            "Underwater": BorrowSnapshot(principal=100 * 10**18, interest_index=1_000_000_000_000_000_000),
            "remaining": BorrowSnapshot(principal=100 * 10**18, interest_index=1_000_000_000_000_000_000),
        },
        total_cash=200_000_000_000_000_000_000_000,
    )

    comptroller_state = StateComptroller(
        id=3,
        name="comptroller",
        block_number=0,
        block_timestamp=0,
        close_factor_mantissa=500_000_000_000_000_000,
        liquidation_incentive_mantissa=1_080_000_000_000_000_000,
        max_assets=20,
        market_states={"cUSDC": market_1_state, "cETH": market_2_state},
    )

    def test_accrue_interest(self):
        # values are such that utilisation ration = 0.2
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        starting_accrual_block = ceth_market.accrual_block_number
        borrow_rate = ceth_market.interest_rate_model.get_borrow_rate(
            ceth_market.total_cash, ceth_market.total_borrows, ceth_market.total_reserves
        )
        ceth_market.accrue_interest(ceth_market.accrual_block_number + 1)

        assert ceth_market.accrual_block_number == starting_accrual_block + 1
        assert (
            borrow_rate
            == 0.2 * self.market_2_state.interest_rate_model.multiplier_per_block
            + self.market_2_state.interest_rate_model.base_rate_per_block
        )
        assert ceth_market.borrow_index == self.market_2_state.borrow_index + borrow_rate

    def test_borrow_balance_stored(self):
        # values are such that utilisation ration = 0.2
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        borrow_balance_init = ceth_market.borrow_balance_stored_internal(wallet1)
        assert borrow_balance_init == self.market_2_state.account_borrows["UserWallet"].principal

        ceth_market.accrue_interest(ceth_market.accrual_block_number + 1)
        borrow_balance_new = ceth_market.borrow_balance_stored_internal(wallet1)
        assert (
            borrow_balance_new
            == borrow_balance_init
            * ceth_market.borrow_index
            // self.market_2_state.account_borrows["UserWallet"].interest_index
        )

    def test_mint_wallet(self):
        # values are such that utilisation ration = 0.2
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        initial_balance_ceth = wallet1.get_balance_of_float("cETH")
        initial_balance_eth = wallet1.get_balance_of_float("ETH")
        mint_a = tran_helper.create_mint_transaction(
            sender_wallet=wallet1,
            mint_amount=5 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        exchange_rate = ceth_market.exchange_rate_stored_internal()
        ceth_market.process_single_transaction(mint_a)
        assert 5 * 10 ** (18 + 18 - 8) / exchange_rate == pytest.approx(
            wallet1.get_balance_of_float("cETH") - initial_balance_ceth, abs=1e-8
        )
        assert (
            ceth_market.total_supply
            == self.market_2_state.total_supply + wallet1.get_balance_of("cETH") - initial_balance_ceth * 10**8
        )
        assert -5 == wallet1.get_balance_of_float("ETH") - initial_balance_eth

    def test_get_virtual_position(self):
        # values are such that utilisation ration = 0.2
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        wallet = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        exchange_rate = ceth_market.exchange_rate_stored_internal()

        debt, collateral, _ = ceth_market.get_wallet_virtual_position(wallet)
        assert debt == 10**18
        assert collateral == wallet.holdings["cETH"] * exchange_rate // 10**18

    def test_mint_no_wallet(self):
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        mint_a = tran_helper.create_mint_transaction(
            mint_amount=5 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(mint_a)

        assert ceth_market.total_cash == self.market_2_state.total_cash + 5 * 10**ceth_market.underlying_decimals

    def test_redeem_wallet(self):
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        ceth_market = comptroller.markets["cETH"]

        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        initial_balance_ceth = wallet1.get_balance_of_float("cETH")
        initial_balance_eth = wallet1.get_balance_of_float("ETH")
        redeem_a = tran_helper.create_redeem_transaction(
            sender_wallet=wallet1,
            redeem_tokens_in=5 * 10**ceth_market.underlying_decimals,
            redeem_amount_in=10,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(redeem_a)
        assert initial_balance_ceth == wallet1.get_balance_of_float("cETH")
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH")

        exchange_rate = ceth_market.exchange_rate_stored_internal()
        redeem_b = tran_helper.create_redeem_transaction(
            sender_wallet=wallet1,
            redeem_tokens_in=5 * 10**8,
            redeem_amount_in=0,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(redeem_b)
        assert initial_balance_ceth == wallet1.get_balance_of_float("cETH") + 5
        assert 5 / 10 ** (18 + 18 - 8) * exchange_rate == pytest.approx(
            wallet1.get_balance_of_float("ETH") - initial_balance_eth, abs=1e-8
        )

        balance_ceth_t1 = wallet1.get_balance_of_float("cETH")
        balance_eth_t1 = wallet1.get_balance_of_float("ETH")
        exchange_rate = ceth_market.exchange_rate_stored_internal()
        redeem_c = tran_helper.create_redeem_transaction(
            sender_wallet=wallet1,
            redeem_tokens_in=0,
            redeem_amount_in=5 * 10**18,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(redeem_c)
        assert balance_eth_t1 == wallet1.get_balance_of_float("ETH") - 5
        assert balance_ceth_t1 == pytest.approx(
            wallet1.get_balance_of_float("cETH") + 5 * 10 ** (18 + 18 - 8) / exchange_rate, abs=1e-8
        )

    def test_redeem_no_wallet(self):
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        redeem_a = tran_helper.create_redeem_transaction(
            redeem_tokens_in=5 * 10**ceth_market.underlying_decimals,
            redeem_amount_in=10,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(redeem_a)
        assert ceth_market.total_supply == self.market_2_state.total_supply
        assert ceth_market.total_cash == self.market_2_state.total_cash

        exchange_rate = ceth_market.exchange_rate_stored_internal()
        redeem_b = tran_helper.create_redeem_transaction(
            sender_wallet=None,
            redeem_tokens_in=5 * 10**8,
            redeem_amount_in=0,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(redeem_b)
        assert self.market_2_state.total_supply == ceth_market.total_supply + 5 * 10**8
        assert 5 / 10 ** (18 + 18 - 8) * exchange_rate == pytest.approx(
            (-ceth_market.total_cash + self.market_2_state.total_cash) / 10**ceth_market.underlying_decimals, abs=1e-8
        )

        total_supply_t1 = ceth_market.total_supply
        total_cash_t1 = ceth_market.total_cash
        exchange_rate = ceth_market.exchange_rate_stored_internal()
        redeem_c = tran_helper.create_redeem_transaction(
            redeem_tokens_in=0,
            redeem_amount_in=5 * 10**18,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(redeem_c)
        assert total_cash_t1 == ceth_market.total_cash + 5 * 10**ceth_market.underlying_decimals
        assert total_supply_t1 == ceth_market.total_supply + 5 * 10 ** (18 + 18) // exchange_rate

    def test_borrow_wallet(self):
        # values are such that utilisation ration = 0.2
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        ceth_market = comptroller.markets["cETH"]

        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        initial_borrow = self.market_2_state.account_borrows[wallet1.agent_name].principal
        initial_balance_eth = wallet1.get_balance_of_float("ETH")
        borrow_a = tran_helper.create_borrow_transaction(
            sender_wallet=wallet1,
            borrow_amount=50 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )

        ceth_market.process_single_transaction(borrow_a)
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH") - 50
        assert ceth_market.total_cash == self.market_2_state.total_cash - 50 * 10**ceth_market.underlying_decimals
        assert ceth_market.total_borrows == self.market_2_state.total_borrows + 50 * 10**ceth_market.underlying_decimals
        assert (
            ceth_market.account_borrows[wallet1.agent_name].principal
            == initial_borrow + 50 * 10**ceth_market.underlying_decimals
        )

        borrow_b = tran_helper.create_borrow_transaction(
            sender_wallet=wallet1,
            borrow_amount=5000 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(borrow_b)
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH") - 50
        assert ceth_market.total_cash == self.market_2_state.total_cash - 50 * 10**ceth_market.underlying_decimals
        assert ceth_market.total_borrows == self.market_2_state.total_borrows + 50 * 10**ceth_market.underlying_decimals
        assert (
            ceth_market.account_borrows[wallet1.agent_name].principal
            == initial_borrow + 50 * 10**ceth_market.underlying_decimals
        )

    def test_borrow_no_wallet(self):
        # values are such that utilisation ration = 0.2
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        borrow_a = tran_helper.create_borrow_transaction(
            borrow_amount=50 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )

        ceth_market.process_single_transaction(borrow_a)
        assert self.market_2_state.total_cash == ceth_market.total_cash + 50 * 10**18
        assert ceth_market.total_borrows == self.market_2_state.total_borrows + 50 * 10**ceth_market.underlying_decimals

        borrow_b = tran_helper.create_borrow_transaction(
            borrow_amount=ceth_market.borrow_cap, block_number=ceth_market.accrual_block_number, ctoken="cETH"
        )
        ceth_market.process_single_transaction(borrow_b)
        assert ceth_market.total_cash == self.market_2_state.total_cash - 50 * 10**ceth_market.underlying_decimals
        assert ceth_market.total_borrows == self.market_2_state.total_borrows + 50 * 10**ceth_market.underlying_decimals

        borrow_c = tran_helper.create_borrow_transaction(
            borrow_amount=ceth_market.total_cash, block_number=ceth_market.accrual_block_number, ctoken="cETH"
        )
        ceth_market.process_single_transaction(borrow_c)
        assert ceth_market.total_cash == self.market_2_state.total_cash - 50 * 10**ceth_market.underlying_decimals
        assert ceth_market.total_borrows == self.market_2_state.total_borrows + 50 * 10**ceth_market.underlying_decimals

    def test_repay_wallet_is_borrower(self):
        # values are such that utilisation ration = 0.2
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        initial_borrow = self.market_2_state.account_borrows[wallet1.agent_name].principal
        initial_balance_eth = wallet1.get_balance_of_float("ETH")

        repay_a = tran_helper.create_repay_transaction(
            sender_wallet=wallet1,
            borrow_wallet=wallet1,
            repay_amount=50 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # not enough balance
        ceth_market.process_single_transaction(repay_a)
        assert initial_borrow == ceth_market.account_borrows[wallet1.agent_name].principal
        assert ceth_market.total_cash == self.market_2_state.total_cash
        assert ceth_market.total_borrows == self.market_2_state.total_borrows
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH")

        # too much repay
        repay_b = tran_helper.create_repay_transaction(
            sender_wallet=wallet1,
            borrow_wallet=wallet1,
            repay_amount=10 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(repay_b)
        assert initial_borrow == ceth_market.account_borrows[wallet1.agent_name].principal
        assert ceth_market.total_cash == self.market_2_state.total_cash
        assert ceth_market.total_borrows == self.market_2_state.total_borrows
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH")

        # repay half debt
        repay_c = tran_helper.create_repay_transaction(
            sender_wallet=wallet1,
            borrow_wallet=wallet1,
            repay_amount=initial_borrow // 2,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(repay_c)
        assert initial_borrow // 2 == ceth_market.account_borrows[wallet1.agent_name].principal
        assert ceth_market.total_cash == self.market_2_state.total_cash + initial_borrow // 2
        assert ceth_market.total_borrows == self.market_2_state.total_borrows - initial_borrow // 2
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH") + 0.5

        # repay total
        repay_d = tran_helper.create_repay_transaction(
            sender_wallet=wallet1,
            borrow_wallet=wallet1,
            repay_amount=-1,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # not enough balance
        ceth_market.process_single_transaction(repay_d)
        assert 0 == ceth_market.account_borrows[wallet1.agent_name].principal
        assert ceth_market.total_cash == self.market_2_state.total_cash + initial_borrow
        assert ceth_market.total_borrows == self.market_2_state.total_borrows - initial_borrow
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH") + 1

    def test_repay_wallet_behalf(self):
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        wallet2 = Wallet(
            holdings=copy.deepcopy(self.holdings),
            tokens_metadata=self.tokens_metadata,
            erc721_tokens=[],
            agent_name="repayer",
        )
        initial_borrow = self.market_2_state.account_borrows[wallet1.agent_name].principal
        initial_balance_eth = wallet1.get_balance_of_float("ETH")
        initial_balance_eth_repayer = wallet2.get_balance_of_float("ETH")

        repay_a = tran_helper.create_repay_transaction(
            sender_wallet=wallet2,
            borrow_wallet=wallet1,
            repay_amount=50 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # not enough balance
        ceth_market.process_single_transaction(repay_a)
        assert initial_borrow == ceth_market.account_borrows[wallet1.agent_name].principal
        assert ceth_market.total_cash == self.market_2_state.total_cash
        assert ceth_market.total_borrows == self.market_2_state.total_borrows
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH")
        assert initial_balance_eth_repayer == wallet2.get_balance_of_float("ETH")

        # too much repay
        repay_b = tran_helper.create_repay_transaction(
            sender_wallet=wallet2,
            borrow_wallet=wallet1,
            repay_amount=10 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # not enough balance
        ceth_market.process_single_transaction(repay_b)
        assert initial_borrow == ceth_market.account_borrows[wallet1.agent_name].principal
        assert ceth_market.total_cash == self.market_2_state.total_cash
        assert ceth_market.total_borrows == self.market_2_state.total_borrows
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH")
        assert initial_balance_eth_repayer == wallet2.get_balance_of_float("ETH")

        # repay half debt
        repay_c = tran_helper.create_repay_transaction(
            sender_wallet=wallet2,
            borrow_wallet=wallet1,
            repay_amount=initial_borrow // 2,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # not enough balance
        ceth_market.process_single_transaction(repay_c)
        assert initial_borrow // 2 == ceth_market.account_borrows[wallet1.agent_name].principal
        assert ceth_market.total_cash == self.market_2_state.total_cash + initial_borrow // 2
        assert ceth_market.total_borrows == self.market_2_state.total_borrows - initial_borrow // 2
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH")
        assert initial_balance_eth_repayer == wallet2.get_balance_of_float("ETH") + 0.5

        # repay total
        repay_d = tran_helper.create_repay_transaction(
            sender_wallet=wallet2,
            borrow_wallet=wallet1,
            repay_amount=-1,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # not enough balance
        ceth_market.process_single_transaction(repay_d)
        assert 0 == ceth_market.account_borrows[wallet1.agent_name].principal
        assert ceth_market.total_cash == self.market_2_state.total_cash + initial_borrow
        assert ceth_market.total_borrows == self.market_2_state.total_borrows - initial_borrow
        assert initial_balance_eth == wallet1.get_balance_of_float("ETH")
        assert initial_balance_eth_repayer == wallet2.get_balance_of_float("ETH") + 1

    def test_repay_wallet_no_wallets(self):
        # values are such that utilisation ration = 0.2
        comptroller = Comptroller(state=self.comptroller_state)
        ceth_market = comptroller.markets["cETH"]

        repay_a = tran_helper.create_repay_transaction(
            repay_amount=50 * 10**ceth_market.underlying_decimals,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(repay_a)
        assert ceth_market.total_cash == self.market_2_state.total_cash + 50 * 10**ceth_market.underlying_decimals
        assert ceth_market.total_borrows == self.market_2_state.total_borrows - 50 * 10**ceth_market.underlying_decimals

        repay_b = tran_helper.create_repay_transaction(
            repay_amount=-1, block_number=ceth_market.accrual_block_number, ctoken="cETH"
        )
        with pytest.raises(NotImplementedError) as excinfo:
            ceth_market.process_single_transaction(repay_b)
        assert (
            str(excinfo.value)
            == "it is not possible to know the exact amount to repay if the borrow wallet is not specified"
        )

    def test_transfer(self):
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        ceth_market = comptroller.markets["cETH"]

        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        wallet2 = Wallet(
            holdings=self.holdings.copy(), tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name="dst"
        )
        initial_balance_ceth = wallet1.get_balance_of("cETH")
        initial_balance_ceth_dst = wallet2.get_balance_of("cETH")

        transfer_a = tran_helper.create_transfer_transaction(
            sender_wallet=wallet1,
            dst_wallet=wallet2,
            amount=40_000 * 10**8,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # not enough balance
        ceth_market.process_single_transaction(transfer_a)
        assert initial_balance_ceth == wallet1.get_balance_of("cETH")
        assert initial_balance_ceth_dst == wallet2.get_balance_of("cETH")

        transfer_b = tran_helper.create_transfer_transaction(
            sender_wallet=wallet1,
            dst_wallet=wallet2,
            amount=29_000 * 10**8,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # would result undercollateralised
        ceth_market.process_single_transaction(transfer_b)
        assert initial_balance_ceth == wallet1.get_balance_of("cETH")
        assert initial_balance_ceth_dst == wallet2.get_balance_of("cETH")

        transfer_c = tran_helper.create_transfer_transaction(
            sender_wallet=wallet1,
            dst_wallet=wallet2,
            amount=2_000 * 10**8,
            block_number=ceth_market.accrual_block_number,
            ctoken="cETH",
        )
        # success
        ceth_market.process_single_transaction(transfer_c)
        assert initial_balance_ceth == wallet1.get_balance_of("cETH") + 2_000 * 10**8
        assert initial_balance_ceth_dst == wallet2.get_balance_of("cETH") - 2_000 * 10**8

    def test_liquidate_wallets(self):
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        ceth_market = comptroller.markets["cETH"]
        cusdc_market = comptroller.markets["cUSDC"]

        wallet1 = Wallet(
            holdings=self.holdings, tokens_metadata=self.tokens_metadata, erc721_tokens=[], agent_name=self.my_address
        )
        underwater = Wallet(
            holdings=self.underwater_holdings,
            tokens_metadata=self.tokens_metadata,
            erc721_tokens=[],
            agent_name="Underwater",
        )
        initial_balance_cusdc = underwater.get_balance_of("cUSDC")
        initial_balance_cusdc_liquidator = wallet1.get_balance_of("cUSDC")
        initial_balance_eth = underwater.get_balance_of("ETH")
        initial_balance_eth_liquidator = wallet1.get_balance_of("ETH")

        # too much repay
        liquidate_a = tran_helper.create_liquidate_transaction(
            sender_wallet=wallet1,
            borrower=underwater,
            repay_amount=51 * 10**18,
            block_number=ceth_market.accrual_block_number,
            ctoken_collateral="cUSDC",
            ctoken="cETH",
        )
        # liquidator == borrower
        liquidate_b = tran_helper.create_liquidate_transaction(
            sender_wallet=underwater,
            borrower=underwater,
            repay_amount=5 * 10**18,
            block_number=ceth_market.accrual_block_number,
            ctoken_collateral="cUSDC",
            ctoken="cETH",
        )
        # liquidate 0
        liquidate_c = tran_helper.create_liquidate_transaction(
            sender_wallet=wallet1,
            borrower=underwater,
            repay_amount=0,
            block_number=ceth_market.accrual_block_number,
            ctoken_collateral="cUSDC",
            ctoken="cETH",
        )
        # liquidate -1
        liquidate_d = tran_helper.create_liquidate_transaction(
            sender_wallet=wallet1,
            borrower=underwater,
            repay_amount=-1,
            block_number=ceth_market.accrual_block_number,
            ctoken_collateral="cUSDC",
            ctoken="cETH",
        )
        # liquidate healthy position
        liquidate_e = tran_helper.create_liquidate_transaction(
            sender_wallet=underwater,
            borrower=wallet1,
            repay_amount=int(0.5 * 10**18),
            block_number=ceth_market.accrual_block_number,
            ctoken_collateral="cUSDC",
            ctoken="cETH",
        )
        # liquidator does not have enough to repay what he tries to do
        liquidate_f = tran_helper.create_liquidate_transaction(
            sender_wallet=wallet1,
            borrower=underwater,
            repay_amount=int(20 * 10**18),
            block_number=ceth_market.accrual_block_number,
            ctoken_collateral="cUSDC",
            ctoken="cETH",
        )
        ceth_market.process_transactions([liquidate_a, liquidate_b, liquidate_c, liquidate_d, liquidate_e, liquidate_f])
        assert initial_balance_cusdc_liquidator == wallet1.get_balance_of("cUSDC")
        assert initial_balance_cusdc == underwater.get_balance_of("cUSDC")
        assert initial_balance_eth_liquidator == wallet1.get_balance_of("ETH")
        assert initial_balance_eth == underwater.get_balance_of("ETH")

        # success
        liquidate_g = tran_helper.create_liquidate_transaction(
            sender_wallet=wallet1,
            borrower=underwater,
            repay_amount=int(10 * 10**18),
            block_number=ceth_market.accrual_block_number,
            ctoken_collateral="cUSDC",
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(liquidate_g)
        assert (
            ceth_market.account_borrows["Underwater"].principal
            == self.market_2_state.account_borrows["Underwater"].principal - 10 * 10**18
        )
        assert wallet1.get_balance_of("ETH") == 0
        assert ceth_market.total_cash == self.market_2_state.total_cash + 10 * 10**18
        assert ceth_market.total_borrows == self.market_2_state.total_borrows - 10 * 10**18
        # exchange rate is 0.02 on the cUSDC market
        assert underwater.get_balance_of("cUSDC") == initial_balance_cusdc - 10 / 0.02 * 1.08 * 10**8
        assert (
            wallet1.get_balance_of("cUSDC") == initial_balance_cusdc_liquidator + 10 / 0.02 * 1.08 * (1 - 0.028) * 10**8
        )
        assert (
            cusdc_market.total_reserves
            == self.market_1_state.total_reserves + 10 * 1.08 * 0.028 * 10**cusdc_market.underlying_decimals
        )
        assert cusdc_market.total_supply == self.market_1_state.total_supply - 10 / 0.02 * 1.08 * 0.028 * 10**8

    def test_liquidate_no_wallets(self):
        comptroller = Comptroller(state=self.comptroller_state)
        comptroller._stored_spot = {("ETH", "USDC"): 1, ("USDC", "USDC"): 1}
        ceth_market = comptroller.markets["cETH"]
        cusdc_market = comptroller.markets["cUSDC"]
        # success
        liquidate = tran_helper.create_liquidate_transaction(
            repay_amount=int(10 * 10**18),
            block_number=ceth_market.accrual_block_number,
            ctoken_collateral="cUSDC",
            ctoken="cETH",
        )
        ceth_market.process_single_transaction(liquidate)

        assert ceth_market.total_cash == self.market_2_state.total_cash + 10 * 10**18
        assert ceth_market.total_borrows == self.market_2_state.total_borrows - 10 * 10**18
        # exchange rate is 0.02 on the cUSDC market
        assert (
            cusdc_market.total_reserves
            == self.market_1_state.total_reserves + 10 * 1.08 * 0.028 * 10**cusdc_market.underlying_decimals
        )
        assert cusdc_market.total_supply == self.market_1_state.total_supply - 10 / 0.02 * 1.08 * 0.028 * 10**8


if __name__ == "__main__":
    # unittest.main()test_collect_fee_one_lp_token0_in
    # Run only one test
    suite = unittest.TestSuite()
    suite.addTest(TestComptrollerMethods("test_comptroller_methods"))
    # suite.addTest(TestSwapMethods('test_swap_same_tick_interval'))
    # suite.addTest(TestSwapMethods('test_swap_multi_tick_intervals'))
    # suite.addTest(TestSwapMethods('test_swap_multi_tick_intervals_fees_collected'))
    runner = unittest.TextTestRunner()
    runner.run(suite)
