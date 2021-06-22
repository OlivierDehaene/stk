import unittest

from absl.testing import parameterized
import stk
import torch


@parameterized.parameters((8, 16, 0.0, 1))
class ConversionTest(parameterized.TestCase):

    def testConversion_DenseToSparse(self, rows, cols, sparsity, blocking):
        mask = stk.random.dense_mask(rows, cols, sparsity, blocking)
        x = (torch.randn(rows, cols) * mask).type(torch.float16)

        # Convert the matrix to sparse format.
        sparse_x = stk.ops.to_sparse(x, blocking)

        # Validate the matrix.
        sparse_x.validate()
        
        # Validate the shape.
        self.assertEqual(sparse_x.dim(), 2)
        self.assertEqual(sparse_x.size()[0], rows)
        self.assertEqual(sparse_x.size()[1], cols)

        # Validate the sparsity.
        numblocks = rows // blocking * cols // blocking
        nnz = round(numblocks * (1 - sparsity))
        self.assertEqual(sparse_x.nnz, nnz)

        # Convert back to dense format.
        dense_x = stk.ops.to_dense(sparse_x)

        # Validate the shape.
        self.assertEqual(dense_x.dim(), 2)
        self.assertEqual(dense_x.size()[0], rows)
        self.assertEqual(dense_x.size()[1], cols)

        # Validate the sparsity
        self.assertEqual(torch.count_nonzero(dense_x).item(), nnz)

        self.assertTrue(torch.all(torch.eq(x, dense_x)))

        
if __name__ == '__main__':
    unittest.main()