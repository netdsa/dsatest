# Configuration Files

## Introduction

To have a complete test setup, multiple files have to be populated. The point is
to be able to cope with the different environments with enough flexibility to
let users write the tests they want.

Remember that users may run different distributions on their hardware (resulting
in network interfaces having different names), connect different interfaces to
the host machine, and so on.

## Switch Configurations

Switch configurations are under `conf/switch/`. Here, we store a few
information related to the switch
*TODO: to be enhanced once we really make use of it*

## Board Configurations

Board configurations are under `conf/board`. They describe the hardware of the
board being tested. For instance, consider the following situation:

     Switch Chip                       External Interfaces
    +-----------+                              |
    |     port0 |----> to CPU                  |
    |     port1 |-----------------------[ Connector LAN0 ]
    |     port2 |----> Non connected           |
    |     port3 |-----------------------[ Connector LAN1 ]
    +-----------+                              |

Only port1 and port3 can be connected to the test machine, but we still want to
get sensible error reporting if errors occur on one of the two LAN connectors.
The board configuration introduces a first abstraction by mapping connectors to
ports:

board-example.cfg
```
[switch0]
port1 = if0
port3 = if1
```

## Environment Configurations

Environment configurations are under `conf/env`. They describe the test
environment: how machine are connected and what are the names of the interfaces

environment-example.cfg
```
[host]
if0 = enp0s31f6

[machine]
ssh = 192.168.0.116
board = board-example ; refer to the board configuration file
if0 = eth8            ; Because the board is running Buildroot, it
                      ; could be named enp0xxx with another distro
if1 = eth9
```

Here, the machine and the host are connected with one cable.

     board                             host
 +------------+                 +---------------+
 |            |      cable      |               |
 |    eth8 [ if0 ]<--------->[ if0 ] enp0s31f6  |
 |            |                 |               |
 |    eth9 [ if1 ]              |               |
 |            |                 |               |
 +------------+                 +---------------+

To control both ends of the link, we know that it's named `eth8` on the board
and `enp0s31f6` on the host, and for error reporting we know that `eth8` is the
`port1` of `switch0` through the board config file.
