# Basic Working Mininet

## How to use
- Define prefixes for hosts and their corresponding port and MAC address in `trie.py`. The ports start from 1.
- In `topology.json`, the IP and MAC needs to match. For the commands, the gateway IP address must be in the host IP's address range, and the MAC address can be anything. Make sure everything matches!
- Run `make run` to start everything up.
- You can also start up Wireshark to inspect packets to confirm everything is appearing as expected.

## Useful commanands (all in mininet)
- Ping all hosts: `pingall`
- Set up a host to receive packets: `<host> python receive.py`
- Send packet: `<host> python send.py <dest_host> <msg>`
