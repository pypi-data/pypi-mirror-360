import unittest
import numpy as np
from sparsesampler.sampling import sample as sf  # Adjust the import based on your structure

class TestSparseSampling(unittest.TestCase):

    def setUp(self):
        # Create a sample dataset with random data
        np.random.seed(42)
        self.data = np.random.rand(100000, 2000)  # 1000 cells, 20 features

    def test_sample_function(self):
        # Test the sampling function with valid input
        size = 100  # Desired number of samples
        samples, elapsed_time = sf(X=self.data, size=size, p=100)

        # Test if the number of samples returned is as expected
        self.assertEqual(len(samples), size, f"Expected {size} samples, got {len(samples)}")
        
        # Check if the samples are valid indices of the input data
        self.assertTrue(all(sample in range(self.data.shape[0]) for sample in samples),
                        "Some samples are not valid indices of the input data.")

        # Optional: Validate the elapsed time is reasonable (e.g., less than 5 seconds)
        self.assertLess(elapsed_time, 5, "Elapsed time exceeds expected duration.")

    def test_sample_function_no_input(self):
        # Test the sampling function with no input data
        with self.assertRaises(ValueError) as context:
            sf(size=100)
        self.assertEqual(str(context.exception), "X must be provided.")

    def test_sample_with_random_projection(self):
        # Test the sampling function with random projection enabled
        size = 500
        p = 100  # Reduced dimensions
        samples, elapsed_time = sf(X=self.data, size=size, p=p, random_projection=True)

        # Test if the number of samples returned is as expected
        self.assertEqual(len(samples), size, f"Expected {size} samples, got {len(samples)}")

        # Check if the samples are valid indices of the input data
        self.assertTrue(all(sample in range(self.data.shape[0]) for sample in samples),
                        "Some samples are not valid indices of the input data.")

        # Optional: Validate the elapsed time is reasonable (e.g., less than 5 seconds)
        self.assertLess(elapsed_time, 20, "Elapsed time exceeds expected duration.")

if __name__ == '__main__':
    unittest.main()
