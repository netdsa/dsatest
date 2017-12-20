
import unittest

from dsatest.bench import Bridge, Interface, bench

class TestSanity(unittest.TestCase):

    def test_sanity_bench_variable_exists(self):
        """
        Test that the bench global variable, exposed by dsatest module, exists.
        """
        self.assertTrue(bench is not None)

    def test_sanity_bench_is_setup(self):
        """
        Verify that the bench is actually set up.
        """
        self.assertTrue(bench.is_setup)

    def test_sanity_links_is_iterable(self):
        """
        Verify that bench has a "links" attribute that is an iterable.
        """
        self.assertTrue(iter(bench.links))

    def test_sanity_link_check_attributes(self):
        """
        Verify that element of bench.links contains attributes "host_if" and
        "target_if", and that they are instances of the Interface class.
        """
        for link in bench.links:
            self.assertIsInstance(link.host_if, Interface)
            self.assertIsInstance(link.target_if, Interface)

    def test_sanity_interface_check_attributes(self):
        """
        Verify that each interface on the target which belongs to a valid link
        (ie. are listed in bench.links) have name and port_id attributes.
        """
        for link in bench.links:
            interface = link.target_if
            self.assertIsInstance(interface.name, str)
            self.assertIsInstance(interface.port_id, str)

    def test_sanity_interface_check_name_is_set(self):
        """
        Check that both interfaces belonging to a link have a "name" attribute,
        that it's a string and that it contains a non-empty string.
        """
        for link in bench.links:
            host = link.host_if.name
            target = link.target_if.name
            self.assertIsInstance(host, str)
            self.assertIsInstance(target, str)
            self.assertTrue(host)
            self.assertTrue(target)

    def test_sanity_interface_api(self):
        """
        Check that all interfaces have a set of attributes. Here we check that
        they have some methods like "up", "down", "add_address", etc.
        """
        for link in bench.links:
            ifs = [link.host_if, link.target_if]
            for interface in ifs:
                self.assertTrue(hasattr(interface, "up"))
                self.assertTrue(hasattr(interface, "down"))
                self.assertTrue(hasattr(interface, "add_address"))
                self.assertTrue(hasattr(interface, "del_address"))

    def test_sanity_machine_api(self):
        """
        Check that all machines have a set of attributes. Here we check that
        they have some methods like "up", "down", "add_address", etc.
        """
        machs = [bench.host, bench.target]
        for mach in machs:
            self.assertTrue(hasattr(mach, "up"))
            self.assertTrue(hasattr(mach, "down"))
            self.assertTrue(hasattr(mach, "add_address"))
            self.assertTrue(hasattr(mach, "del_address"))
            self.assertTrue(hasattr(mach, "add_bridge"))
            self.assertTrue(hasattr(mach, "del_bridge"))
            self.assertTrue(hasattr(mach, "ping"))

    def test_sanity_bridge_api(self):
        """
        Check that bridges have a set of attributes. Here we check that
        they have some methods like "up", "down", "add_address", etc.
        """
        bridge = Bridge("br0", None)
        self.assertTrue(hasattr(bridge, "add_interface"))
        self.assertTrue(hasattr(bridge, "del_interface"))
        # it should also have the same functions as regular Interface
        self.assertTrue(hasattr(bridge, "up"))
        self.assertTrue(hasattr(bridge, "down"))
        self.assertTrue(hasattr(bridge, "add_address"))
        self.assertTrue(hasattr(bridge, "del_address"))

    @unittest.skipIf(bench.dry_run, "Not available in dry-run mode")
    def test_sanity_machine_target_echo(self):
        """
        Verify that we can successfully execute the "echo" command on the
        target and get back its outpout.
        """
        _, stdout, stderr = bench.target.execute("echo -n 'Hello World'")
        self.assertEqual(stdout.strip(), "Hello World")
        self.assertEqual(stderr.strip(), "")

    @unittest.skipIf(bench.dry_run, "Not available in dry-run mode")
    def test_sanity_machine_target_echo_stderr(self):
        """
        Verify that we can successfully execute the "echo" command on the
        target and get back its outpout (from stderr).
        """
        _, stdout, stderr = bench.target.execute("echo -n 'Hello World' >&2")
        self.assertEqual(stdout.strip(), "")
        self.assertEqual(stderr.strip(), "Hello World")

    def test_sanity_machine_host_echo(self):
        """
        Verify that we can successfully execute the "echo" command on the
        host and get back its outpout.
        """
        _, stdout, stderr = bench.host.execute("echo -n 'Hello World'")
        self.assertEqual(stdout.strip(), "Hello World")
        self.assertEqual(stderr.strip(), "")

    def test_sanity_machine_host_echo_stderr(self):
        """
        Verify that we can successfully execute the "echo" command on the
        host and get back its outpout (from stderr).
        """
        _, stdout, stderr = bench.host.execute("echo -n 'Hello World' >&2")
        self.assertEqual(stdout.strip(), "")
        self.assertEqual(stderr.strip(), "Hello World")
