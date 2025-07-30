import torch
import pytest

from complex_jacobian import complex_jacobian, unitary_input_jacobian


def f_holomorphic(z):
    return z @ z + torch.eye(z.shape[-1], dtype=z.dtype, device=z.device)


def f_nonholomorphic(z):
    # z.adjoint() = conjugate transpose
    return z @ z + z.adjoint() @ z


@pytest.fixture
def unitary_matrix():
    # Simple unitary matrix:
    U = torch.matrix_exp(1j * torch.eye(3, dtype=torch.cdouble))
    return U


def test_holomorphic_jacobian(unitary_matrix):
    J = complex_jacobian(f_holomorphic, unitary_matrix, holomorphic=True)
    assert J.shape == unitary_matrix.shape + unitary_matrix.shape
    assert torch.norm(J).item() > 0


def test_nonholomorphic_jacobian(unitary_matrix):
    J, J_bar = complex_jacobian(f_nonholomorphic, unitary_matrix, holomorphic=False)
    assert J.shape == unitary_matrix.shape + unitary_matrix.shape
    assert J_bar.shape == unitary_matrix.shape + unitary_matrix.shape
    assert torch.norm(J).item() > 0
    assert torch.norm(J_bar).item() > 0

def test_unitary_input_jacobian(unitary_matrix):
    J_u = unitary_input_jacobian(f_nonholomorphic, unitary_matrix)
    J = complex_jacobian(f_holomorphic, unitary_matrix, holomorphic=True)
    assert (J_u - J).abs().sum() == 0


if __name__ == "__main__":
    pytest.main([__file__])
