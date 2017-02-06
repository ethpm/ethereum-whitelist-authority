import pytest

import itertools

from web3.utils.abi import function_signature_to_4byte_selector
from web3.utils.encoding import decode_hex


@pytest.fixture()
def authority(chain, accounts):
    authority_owner = accounts[5]
    _authority, _ = chain.store.provider.get_or_deploy_contract(
        'WhitelistAuthority',
        deploy_transaction={'from': authority_owner},
    )
    assert _authority.call().authority() == authority_owner
    return _authority


@pytest.fixture()
def authorize_call(chain, authority):
    def _authorize_call(caller_address, code_address, function_signature, can_call):
        sig = decode_hex(function_signature_to_4byte_selector(function_signature))
        chain.wait.for_receipt(authority.transact({
            'from': authority.call().authority(),
        }).setCanCall(
            callerAddress=caller_address,
            codeAddress=code_address,
            sig=sig,
            can=can_call,
        ))
        assert authority.call().canCall(
            callerAddress=caller_address,
            codeAddress=code_address,
            sig=sig,
        ) is can_call
    return _authorize_call


@pytest.fixture()
def whitelist_call(chain, authority):
    def _whitelist_call(code_address, function_signature, can_call):
        sig = decode_hex(function_signature_to_4byte_selector(function_signature))
        chain.wait.for_receipt(authority.transact({
            'from': authority.call().authority(),
        }).setAnyoneCanCall(
            codeAddress=code_address,
            sig=sig,
            can=can_call,
        ))
        assert authority.call().canCall(
            '0x0000000000000000000000000000000000000000',
            codeAddress=code_address,
            sig=sig,
        ) is can_call
    return _whitelist_call


@pytest.fixture()
def topics_to_abi(project):
    from web3.utils.abi import (
        filter_by_type,
        event_abi_to_log_topic,
    )
    all_events_abi = filter_by_type('event', itertools.chain.from_iterable(
        contract['abi'] for contract in project.compiled_contract_data.values()
    ))
    _topic_to_abi = {
        event_abi_to_log_topic(abi): abi
        for abi in all_events_abi
    }
    return _topic_to_abi


@pytest.fixture()
def get_all_event_data(topics_to_abi):
    from web3.utils.events import (
        get_event_data,
    )

    def _get_all_event_data(log_entries):
        all_event_data = [
            get_event_data(topics_to_abi[log_entry['topics'][0]], log_entry)
            for log_entry in log_entries
            if log_entry['topics'] and log_entry['topics'][0] in topics_to_abi
        ]
        return all_event_data
    return _get_all_event_data


@pytest.fixture()
def extract_event_logs(chain, web3, get_all_event_data):
    def _extract_event_logs(event_name, contract, txn_hash, return_single=True):
        txn_receipt = chain.wait.for_receipt(txn_hash)
        filter = contract.pastEvents(event_name, {
            'fromBlock': txn_receipt['blockNumber'],
            'toBlock': txn_receipt['blockNumber'],
        })
        log_entries = filter.get()

        if len(log_entries) == 0:
            all_event_logs = get_all_event_data(txn_receipt['logs'])
            if all_event_logs:
                raise AssertionError(
                    "Something went wrong.  The following events were found in"
                    "the logs for the given transaction hash:\n"
                    "{0}".format('\n'.join([
                        event_log['event'] for event_log in all_event_logs
                    ]))
                )
            raise AssertionError(
                "Something went wrong.  No '{0}' log entries found".format(event_name)
            )
        if return_single:
            event_data = log_entries[0]
            return event_data
        else:
            return log_entries
    return _extract_event_logs
