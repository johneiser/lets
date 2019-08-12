from lets.module import Module

# Imports required to execute this module
import hashlib


class Hash(Module):
    """
    Assert that the data has the correct hash before passing it
    through.
    """

    def usage(self) -> object:
        """
        Configure an ArgumentParser object with options relevant
        to the module.

        :return: ArgumentParser object
        """
        parser = super().usage()

        # Specify hash algorithm
        parser.add_argument("-a", "--algorithm",
            help="hash algorithm to use",
            type=str,
            choices=hashlib.algorithms_guaranteed,
            default="md5")

        # Specify assertion requirements
        parser.add_argument("value",
            help="expected hash value",
            type=str,
            nargs="+")

        return parser

    def do(self, data:bytes=None, options:dict=None) -> bytes:
        """
        Main functionality.

        Module.do updates self.options with options.

        :param data: Data to be used by module, in bytes
        :param options: Dict of options to be used by module
        :return: Generator containing results of module execution,
            in bytes
        """
        super().do(data, options)
        
        algorithm = self.options.get("algorithm")

        # Validate input
        try:
            assert data, "Expecting data"
            assert algorithm and algorithm in hashlib.algorithms_guaranteed, "Invalid algorithm: %s (%s)" % (algorithm, hashlib.algorithms_guaranteed)
        except AssertionError as e:
            self.throw(e)

        # Configure algorithm
        h = hashlib.new(algorithm)
        h.update(data)

        # Produce hex digest
        try:
            digest = h.hexdigest()
        except TypeError:
            digest = h.hexdigest(len(data))

        # Assert value is correct
        if digest not in self.options.get("value"):
            self.throw(AssertionError("Hash does not match: %s" % digest))

        # Assertion successful, pass along data
        self.info("Assertion passed: %s" % digest)
        yield data

    def test(self):
        """
        Perform unit tests to verify this module's functionality.
        """
        # Test each algorithm
        data = bytes(range(0,256))
        hashes = {
            "sha3_384": "e834031d7bab82ac00905187335595e020c5bd3220924f4f551d7485931d2cb9efe90b6574fc46b63265314781de017a",
            "sha3_224": "bd34c1faa03a01db5e0c3a3d5e0440d6e5e361060f3dc9d149a26812",
            "shake_256": "336c8aa7f2b08bda6bd7402cd2ea89760b7728a8b31802b80524756361165366ff8159f2f4568a2bfa286db6387895629938c2868a6421c37f988455763a75e4b9259e0a939aaa68295119ccea72c9f0ca7d048aa70eeeb4534c6bd08ecc6163217c790f33b84a89623f8e5538b734967e9490a48b7d0658afb4565364e8b234dfe6a2bceb12ce2130eec00bf2113615a276819d7815f5891d07600275f4d8fbc87b056f44bc2b141ca5ed9e4cb6e9a7bf71f520971dca1c8da6140e2af31faef5502e84991a2d9e9a80183c174cc105ef178d5f6fa45b0f284eb7bced20a47c3f584aca27eac5558da517af7569fe2e843461b4b65f81f819bf81aae6dfaa3b",
            "sha512": "1e7b80bc8edc552c8feeb2780e111477e5bc70465fac1a77b29b35980c3f0ce4a036a6c9462036824bd56801e62af7e9feba5c22ed8a5af877bf7de117dcac6d",
            "sha1": "4916d6bdb7f78e6803698cab32d1586ea457dfc8",
            "sha3_512": "3a843af1f872928f0bbbb513207a1a8e14e3d911269fff521292d07dbd5e2e520d6c2634292801184ffa54fd5f1e992ccfdaff8162f5c5f6d1ea79dbcae97e1d",
            "md5": "e2c865db4162bed963bfaa9ef6ac18f0",
            "sha3_256": "9b04c091da96b997afb8f2585d608aebe9c4a904f7d52c8f28c7e4d2dd9fba5f",
            "sha224": "88702e63237824c4eb0d0fcfe41469a462493e8beb2a75bbe5981734",
            "blake2b": "1ecc896f34d3f9cac484c73f75f6a5fb58ee6784be41b35f46067b9c65c63a6794d3d744112c653f73dd7deb6666204c5a9bfa5b46081fc10fdbe7884fa5cbf8",
            "shake_128": "9d32ba2aa8f40b0cdf108376d77abfd5c97f149e6ba0c9efe3499c7b3c039b0afac641a978ef435b3d83b9712da8ea826bb38078899b3efaec77d44a0460b220225d1b0b11a1d1c5cb0acb5aca92c6fb95f64a992eee6b6de24434aae4fba9d496bd8bd90624391f79c0db7d20eef1ddbfe8d771b4123e97ad7664012188590eb0b43c7073b7a9ab8af27229bc7246296ac0e172fca7314b8f100dc247d51c949bc4977c345d7c1d5536c96825f3650b7f80b5981b252ce4a858e54f9833cceaf38c12a91a8c6b341e197eb894553ca6f100f731f00f43b854098aace7a4e0ed8252782523f561dd994c291229eaf70185c98ed0026be1bd39c17dd817424009",
            "blake2s": "5fdeb59f681d975f52c8e69c5502e02a12a3afcc5836ba58f42784c439228781",
            "sha384": "ffdaebff65ed05cf400f0221c4ccfb4b2104fb6a51f87e40be6c4309386bfdec2892e9179b34632331a59592737db5c5",
            "sha256": "40aff2e9d2d8922e47afd4648e6967497158785fbd1da870e7110266bf944880",
        }
        for algorithm in hashlib.algorithms_guaranteed:

            # Ensure full coverage
            self.assertTrue(
                algorithm in hashes.keys(),
                "Missing algorithm: %s" % algorithm)

            # Ensure accurate calculation
            self.assertEqual(
                b"".join(self.do(data, {"algorithm" : algorithm, "value" : hashes.get(algorithm)})),
                data,
                "Algorithm produced inaccurate results: %s" % algorithm)
