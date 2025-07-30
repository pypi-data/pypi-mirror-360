from pathlib import Path
from matterlab_relays import R421B16Relay, JYdaqRelay

relay = JYdaqRelay(com_port="COM6", channel=1)

print(relay.on)

relay.on = True

print(relay.on)

relay.on = False

