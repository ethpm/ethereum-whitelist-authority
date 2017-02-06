pragma solidity ^0.4.0;


import {DSAuthEvents as AuthEvents} from "ds-auth/contracts/DSAuthEvents.sol";
import {DSAuthority as Authority} from "ds-auth/contracts/DSAuthority.sol";


contract WhitelistAuthority is Authority {
    mapping (address =>
             mapping (address =>
                      mapping (bytes4 => bool))) _canCall;
    mapping (address => mapping (bytes4 => bool)) _anyoneCanCall;

    event SetCanCall(address indexed callerAddress,
                     address indexed codeAddress,
                     bytes4 indexed sig,
                     bool can);

    event SetAnyoneCanCall(address indexed codeAddress,
                           bytes4 indexed sig,
                           bool can);

    modifier disallow_null_sig(bytes4 sig) {
      if (sig == 0x0) {
        throw;
      } else {
        _;
      }
    }

    function canCall(address callerAddress,
                     address codeAddress,
                     bytes4 sig) constant returns (bool) {
        if (_anyoneCanCall[codeAddress][sig]) {
          return true;
        } else {
          return _canCall[callerAddress][codeAddress][sig];
        }
    }

    function setCanCall(address callerAddress,
                        address codeAddress,
                        bytes4 sig,
                        bool can) auth public disallow_null_sig(sig) returns (bool) {
        _canCall[callerAddress][codeAddress][sig] = can;
        SetCanCall(callerAddress, codeAddress, sig, can);
        return true;
    }

    function setAnyoneCanCall(address codeAddress,
                              bytes4 sig,
                              bool can) auth public disallow_null_sig(sig) returns (bool) {
        _anyoneCanCall[codeAddress][sig] = can;
        SetAnyoneCanCall(codeAddress, sig, can);
        return true;
    }
}
