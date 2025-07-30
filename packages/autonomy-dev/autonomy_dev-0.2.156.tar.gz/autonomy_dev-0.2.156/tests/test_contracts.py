"""Test the contracts module."""

import json
import shutil
from pathlib import Path

import pytest
import responses

from auto_dev.constants import DEFAULT_ENCODING, Network
from auto_dev.exceptions import APIError
from auto_dev.commands.scaffold import BlockExplorer, ContractScaffolder
from auto_dev.contracts.param_type import ParamType
from auto_dev.contracts.utils import PARAM_TO_STR_MAPPING


KNOWN_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # checksum address
BLOCK_EXPLORER_URL = "https://abidata.net"
NETWORK = Network.BASE

DUMMY_ABI = json.loads((Path() / "tests" / "data" / "dummy_abi.json").read_text(DEFAULT_ENCODING))


@pytest.fixture
def block_explorer():
    """Block explorer fixture."""
    return BlockExplorer(BLOCK_EXPLORER_URL, network=NETWORK)


@responses.activate
def test_block_explorer(block_explorer):
    """Test the block explorer."""
    expected_url = f"{BLOCK_EXPLORER_URL}/{KNOWN_ADDRESS}?network={NETWORK.value}"

    responses.add(
        responses.GET,
        expected_url,
        json={"ok": True, "abi": DUMMY_ABI},
    )
    block_explorer = BlockExplorer(BLOCK_EXPLORER_URL, network=NETWORK)
    abi = block_explorer.get_abi(KNOWN_ADDRESS)
    assert abi is not None, "ABI should not be None"
    assert abi == DUMMY_ABI


@responses.activate
def test_block_explorer_error_handling(block_explorer):
    """Test the block explorer handles errors gracefully."""
    expected_url = f"{BLOCK_EXPLORER_URL}/{KNOWN_ADDRESS}?network={NETWORK.value}"

    # Test case 1: API returns error
    responses.add(responses.GET, expected_url, json={"ok": False, "error": "Not found"}, status=404)
    with pytest.raises(APIError):
        block_explorer.get_abi(KNOWN_ADDRESS)

    # Reset responses
    responses.reset()

    # Test case 2: API returns invalid response
    responses.add(
        responses.GET,
        expected_url,
        json={"ok": True},  # Missing ABI
    )
    with pytest.raises(ValueError):
        block_explorer.get_abi(KNOWN_ADDRESS)


@responses.activate
def test_block_explorer_invalid_network():
    """Test the block explorer with an invalid network."""
    with pytest.raises(TypeError) as exc_info:
        BlockExplorer(BLOCK_EXPLORER_URL, network="invalid")
    assert "network must be an instance of Network enum" in str(exc_info.value)


@responses.activate
def test_block_explorer_non_enum_network():
    """Test the block explorer with a network that's not in the Network enum."""
    non_enum_network = "unknown_network"

    with pytest.raises(TypeError) as exc_info:
        BlockExplorer(BLOCK_EXPLORER_URL, network=non_enum_network)
    assert "network must be an instance of Network enum" in str(exc_info.value)


# we now test the scaffolder
@pytest.fixture
def scaffolder(block_explorer):
    """Scaffolder fixture."""
    return ContractScaffolder(block_explorer, "eightballer")


@responses.activate
def test_scaffolder_generate(scaffolder):
    """Test the scaffolder."""
    responses.add(
        responses.GET,
        f"{BLOCK_EXPLORER_URL}/{KNOWN_ADDRESS}?network={NETWORK.value}",
        json={"ok": True, "abi": DUMMY_ABI},
    )
    new_contract = scaffolder.from_block_explorer(KNOWN_ADDRESS, "new_contract")
    assert new_contract
    assert new_contract.abi
    assert new_contract.address == KNOWN_ADDRESS
    assert new_contract.name == "new_contract"
    assert new_contract.author == "eightballer"


@responses.activate
def test_scaffolder_generate_openaea_contract(scaffolder, test_packages_filesystem):
    """Test the scaffolder."""
    del test_packages_filesystem
    responses.add(
        responses.GET,
        f"{BLOCK_EXPLORER_URL}/{KNOWN_ADDRESS}?network={NETWORK.value}",
        json={"ok": True, "abi": DUMMY_ABI},
    )
    new_contract = scaffolder.from_block_explorer(KNOWN_ADDRESS, "new_contract")
    contract_path = scaffolder.generate_openaea_contract(new_contract)
    assert contract_path
    assert contract_path.exists()
    assert contract_path.name == "new_contract"
    assert contract_path.parent.name == "contracts"
    shutil.rmtree(contract_path.parent)
    assert not contract_path.exists()


def test_scaffolder_from_abi(scaffolder, test_filesystem):
    """Test the scaffolder using an ABI file."""
    assert test_filesystem
    path = Path() / "tests" / "data" / "dummy_abi.json"
    new_contract = scaffolder.from_abi(str(path), KNOWN_ADDRESS, "new_contract")
    assert new_contract
    assert new_contract.abi
    assert new_contract.address == KNOWN_ADDRESS
    assert new_contract.name == "new_contract"
    assert new_contract.author == "eightballer"


def test_scaffolder_extracts_events(scaffolder, test_filesystem):
    """Test the scaffolder extracts events."""
    assert test_filesystem
    path = Path() / "tests" / "data" / "dummy_abi.json"
    new_contract = scaffolder.from_abi(str(path), KNOWN_ADDRESS, "new_contract")
    new_contract.parse_events()
    assert new_contract.events


def test_all_param_types_mapped():
    """Test that all ParamType values are mapped to strings."""
    for param_type in ParamType:
        assert param_type in PARAM_TO_STR_MAPPING, f"ParamType {param_type} is not mapped"
        assert isinstance(PARAM_TO_STR_MAPPING[param_type], str), f"Mapping for {param_type} is not a string"