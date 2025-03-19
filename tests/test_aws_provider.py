import unittest
from cloud.provider_factory import CloudProviderFactory

class TestAWSProvider(unittest.TestCase):
    def test_provider_creation(self):
        provider = CloudProviderFactory.get_provider("aws")
        self.assertIsInstance(provider, CloudProviderFactory.get_provider("aws").__class__)

    def test_cluster_creation(self):
        provider = CloudProviderFactory.get_provider("aws")
        connection = provider.connect({})
        self.assertEqual(connection["status"], "connected")
        
        cluster = provider.create_cluster({})
        self.assertIn("cluster_id", cluster)
