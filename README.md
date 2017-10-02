# SquiDSA

A tool to run tests on a DSA test bench.


## Usage

```sh
# run all tests containing "ping" in their test method names
./bench.sh -t ping -B bench.cfg.example

# run all tests defined in sanity.py, using bench.cfg.example for configuration
# --dry-run will skip the SSH connection step. This is used for self-testing.
./bench.sh --dry-run -t sanity.py -B bench.cfg.example
```


## Configuration files

Three kind of files need to be populated in order to run tests on the bench.
From a bottom-up approach:

 * Switch: describe a switch and how its kernel driver exposes some
           information. This file can be shared and used in several test
           benches.
 * Board: describe a board, the switches that are on it, and the interfaces
          that the test bench will be able to use. This file can also be shared.
 * Bench: describe how the host machine and the System under Test (SUT) are
          connected to one another. This file is specific to each bench.

### Switch

*TODO: Not used yet*

### Board

They are located in `conf/target`. They describe the hardware of the
machine being tested. For instance, consider the following situation:

```
  +--------------------------------------------------+
  |                           Board (aka SUT)        |
  |  +----------------+                              |
  |  |          port0 |----> to CPU                  |
  |  | Switch0  port1 |--------------------------[ link0 ] <-+
  |  |          port2 |----> Non connected           |       |- connectors
  |  |          port3 |--------------------------[ link1 ] <-+   (eg. RJ45)
  |  +----------------+                              |
  +--------------------------------------------------+
```

Only port1 and port3 of switch0 are connected to front-facing connectors.
Obviously the bench can only used these two ports to run tests.

Describing the internals of the board (which switch port is connected to what
front-facing connector) allows to get sensible error reporting if errors occur.
Moreover, these files can be shared by people using the same hardware.

```
conf/target/target-example.cfg
----------------------------

[switch0]
name = wag200g
port1 = link0
port3 = link1
```

### Bench

Describe the test bench, ie. how the controlling machine (aka host), running
squidsa, is connect to the SUT.

For instance, let's create a test bench with the board defined in the previous
section. Host and SUT are connected with only one cable:

```
  +-------------+                        +---------------+
  |             |         cable          |               |
  |          [ eth8 ]<------------>[ enp0s31f6 ]         |
  |    SUT      |         link0          |               |
  |          [ eth9 ]                    |      HOST     |
  |             |                        |               |
  +-------------+                        +---------------+
```

Bench configuration file defines that link0 is eth8 on SUT side, and enp0s31f6
on host side. eth9 is left disconnected. Names of interfaces is defined at the
bench level because interfaces may have different names depending on the OS
running on it, so it may vary from one test bench to another.


```
bench.cfg
---------

[host]
link0 = enp0s31f6

[sut]
ssh = 192.168.0.116
board = target-example  ; refer to target configuration file
link0 = eth8            ; Because the target is running Buildroot, it
                        ; could be named enp0xxx with a distribution running
                        ; systemd
link1 = eth9            ; can be filled in. squidsa will warn that it is
                        ; connected to only one end and will run tests only
                        ; using link0
```

When a link is defined under both the host and the sut section, squidsa will
register that link and the corresponding interfaces so that tests will be able
to use them. Links connected to only one end will be ignored.

### Out-of-tree configuration

One can use out-of-tree configuration files by using the `-C` or `--conf-dir`
flags and specifying a directory that has the same layout as the `conf/`
directory. Files found in this alternate directory will have precedence over the
ones found in squidsa's `conf` directory.


## Tests

Tests are written using unittest, and must respect rules defined by this module.
They can access the test bench instance through the following import:

```python
from squidsa.bench import bench
```

API is self-documented in `test/sanity.py`. More documentation welcome!
