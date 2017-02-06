def test_adding_a_whitelist_entry(chain, authority, extract_event_logs, accounts):
    sig = '\x01\x02\x03\x04'
    txn_receipt = chain.wait.for_receipt(authority.transact({
        'from': authority.call().authority(),
    }).setAnyoneCanCall(
        codeAddress=accounts[3],
        sig=sig,
        can=True,
    ))

    event_data = extract_event_logs('SetAnyoneCanCall', authority, txn_receipt['transactionHash'])
    assert event_data['args']['codeAddress'] == accounts[3]
    assert event_data['args']['sig'] == sig
    assert event_data['args']['can'] is True

    assert authority.call().canCall(
        callerAddress=accounts[0],
        codeAddress=accounts[3],
        sig=sig,
    )
    assert authority.call().canCall(
        callerAddress='0x0000000000000000000000000000000000000000',
        codeAddress=accounts[3],
        sig=sig,
    )


def test_removing_a_whitelist_entry(chain, authority, extract_event_logs, accounts):
    sig = '\x01\x02\x03\x04'
    chain.wait.for_receipt(authority.transact({
        'from': authority.call().authority(),
    }).setAnyoneCanCall(
        codeAddress=accounts[3],
        sig=sig,
        can=True,
    ))

    assert authority.call().canCall(
        callerAddress=accounts[0],
        codeAddress=accounts[3],
        sig=sig,
    ) is True
    assert authority.call().canCall(
        callerAddress='0x0000000000000000000000000000000000000000',
        codeAddress=accounts[3],
        sig=sig,
    ) is True

    txn_receipt = chain.wait.for_receipt(authority.transact({
        'from': authority.call().authority(),
    }).setAnyoneCanCall(
        codeAddress=accounts[3],
        sig=sig,
        can=False,
    ))

    event_data = extract_event_logs('SetAnyoneCanCall', authority, txn_receipt['transactionHash'])
    assert event_data['args']['codeAddress'] == accounts[3]
    assert event_data['args']['sig'] == sig
    assert event_data['args']['can'] is False

    assert authority.call().canCall(
        callerAddress=accounts[0],
        codeAddress=accounts[3],
        sig=sig,
    ) is False
    assert authority.call().canCall(
        callerAddress='0x0000000000000000000000000000000000000000',
        codeAddress=accounts[3],
        sig=sig,
    ) is False
