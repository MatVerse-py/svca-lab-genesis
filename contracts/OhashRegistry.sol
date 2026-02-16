// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract OhashRegistry {
    struct Record {
        string ohash;
        string pufId;
        uint256 timestamp;
        address owner;
    }

    mapping(string => Record) public records;
    string[] public allOhashes;

    event OhashRegistered(string ohash, string pufId, address owner);

    function register(string memory _ohash, string memory _pufId) public {
        require(records[_ohash].timestamp == 0, "Ohash already registered");
        
        records[_ohash] = Record({
            ohash: _ohash,
            pufId: _pufId,
            timestamp: block.timestamp,
            owner: msg.sender
        });
        
        allOhashes.push(_ohash);
        emit OhashRegistered(_ohash, _pufId, msg.sender);
    }

    function getRecord(string memory _ohash) public view returns (Record memory) {
        return records[_ohash];
    }

    function totalRecords() public view returns (uint256) {
        return allOhashes.length;
    }
}
