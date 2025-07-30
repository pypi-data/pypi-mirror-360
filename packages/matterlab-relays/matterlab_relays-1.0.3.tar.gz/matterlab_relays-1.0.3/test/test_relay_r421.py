from pathlib import Path
from matterlab_relays import R421B16Relay, JYdaqRelay

relay = R421B16Relay(comm_port="COM6", address = 1, channel=1)

print(relay.on)

relay.on = True

print(relay.on)

relay.on = False

