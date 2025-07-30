# Created by Javad Komijani, 5/July/2025

r"""
This module implements complex-valued automatic differentiation (AD)
using PyTorch, with a focus on Jacobians for functions mapping complex
matrices to complex matrices.

PyTorch's autograd is designed for real-valued functions. To support
AD for complex functions, we represent complex tensors by separating real
and imaginary parts. We compute real-valued Jacobians using PyTorch and
reconstruct complex derivatives, including Wirtinger gradients.

This module provides:
  - A function to compute complex Jacobians ∂f/∂z and ∂f/∂𝑧̄ via real AD.
  - A Jacobian respecting unitary constraints, useful in quantum
    physics and geometric optimization.

Applications
------------
Useful in quantum computing, signal processing, and manifold optimization,
where functions operate on complex or unitary matrices and require accurate
and structure-aware gradients.

Functions
---------
- complex_jacobian:
    Computes ∂f/∂z and ∂f/∂z̄ for complex-valued tensor functions.

- unitary_input_jacobian:
    Computes ∂f/∂z for f(z) under the constraint that z is unitary.
"""

import numpy as np
import torch


def complex_jacobian(f_complex, z, holomorphic=False):
    r"""
    Computes the complex Jacobian ∂f/∂z (or both ∂f/∂z and ∂f/∂𝑧̄) of a complex
    function f: ℂ^{shape} → ℂ^{shape} using PyTorch autograd on the real-valued
    representation of complex tensors.

    This implementation treats the complex function as a function of two real
    variables (real and imaginary parts), computes the real Jacobian, and
    reconstructs the Wirtinger derivatives:
      - ∂f/∂z (holomorphic part)
      - ∂f/∂𝑧̄ (antiholomorphic part)

    Args:
        f_complex (Callable): Function mapping complex tensor z.
        z (torch.Tensor): Complex-valued input tensor.
        holomorphic (bool, optional): If True, f_complex is treated holomorphic
        and return only ∂f/∂z. If False (default), return both ∂f/∂z and ∂f/∂𝑧̄.

    Returns:
        torch.Tensor | Tuple[torch.Tensor, torch.Tensor]:
        - If `holomorphic=True`: returns ∂f/∂z.
        - If `holomorphic=False`: returns tuple (∂f/∂z, ∂f/∂𝑧̄).

    Notes:

    - Jacobian Interpretation (PyTorch Convention):

        For f: ℂⁿˣᵐ → ℂⁿˣᵐ, the input and output are viewed as real-valued
        tensors with shape (n, m, 2) and (n, m, 2), where the last dimension
        holds real and imaginary parts. The real-valued Jacobian has shape:

            jac = torch.autograd.functional.jacobian(f, X)  # (n, m, n, m)

        interpreted as:

            jac[i, j, k, l] = ∂f[i, j] / ∂X[k, l]

        This gives the derivative of output (i, j) w.r.t. input (k, l),
        matching PyTorch’s convention for matrix-valued functions.

    - Gradient of Complex-Valued Matrix Outputs:

        If f: ℂⁿˣᵐ → ℂⁿˣᵐ and Z = X + iY, then each element f[i, j] is complex
        and differentiable w.r.t. Z.

        The differential is:

            df[i, j] = Tr( (∂f[i, j]/∂X)^\top dX + (∂f[i, j]/∂Y)^\top dY )

        Using Wirtinger derivatives:

            ∂f[i, j]/∂z = ½ (∂f[i, j]/∂X - i ∂f[i, j]/∂Y)
            ∂f[i, j]/∂z̄ = ½ (∂f[i, j]/∂X + i ∂f[i, j]/∂Y)

        we write:

            df[i, j] = Tr( (∂f[i, j]/∂z)^\top dZ + (∂f[i, j]/∂z̄)^\top dZ*)

        The full Jacobian ∂f/∂z has shape (n, m, n, m).
    """
    assert torch.is_complex(z), "Input tensor z must be complex."

    # Enable gradient tracking
    z = z.detach().requires_grad_(True)

    # Convert complex tensor to real view: shape (..., 2)
    z_as_real = torch.view_as_real(z)

    def wrapped_func(z_as_real):
        """Wrap f_complex to operate on real-view input"""
        z = torch.view_as_complex(z_as_real)
        w = f_complex(z)
        return torch.view_as_real(w)

    # Compute Jacobian of real-valued function (2m × 2n)
    jacobian_as_real = torch.autograd.functional.jacobian(
        wrapped_func, z_as_real, create_graph=False
    )

    # Flatten to 2D representation
    n_complex = np.prod(z.shape)
    jacobian_as_real = jacobian_as_real.reshape(-1, 2, n_complex, 2)

    # Extract block derivatives of real/imag output w.r.t. real/imag input
    jac00 = jacobian_as_real[:, 0, :, 0]  # ∂Re(f) / ∂Re(z)
    jac01 = jacobian_as_real[:, 0, :, 1]  # ∂Re(f) / ∂Im(z)
    jac10 = jacobian_as_real[:, 1, :, 0]  # ∂Im(f) / ∂Re(z)
    jac11 = jacobian_as_real[:, 1, :, 1]  # ∂Im(f) / ∂Im(z)

    # Define ∂f / ∂x and ∂f / ∂y
    df_dx = jac00 + 1j * jac10  # ∂f / ∂x = (\overline X)^* in AD
    df_dy = jac01 + 1j * jac11  # ∂f / ∂y = (\overline Y)^* in AD

    # Compute Wirtinger derivatives
    df_dz = 0.5 * (df_dx - 1j * df_dy)  # ∂f / ∂z
    df_dzstar = 0.5 * (df_dx + 1j * df_dy)  # ∂f / ∂z*

    # Reshape to match original input/output dimensions
    shape = (*z.shape, *z.shape)
    df_dz = df_dz.reshape(*shape)
    df_dzstar = df_dzstar.reshape(*shape)

    return df_dz if holomorphic else (df_dz, df_dzstar)


def unitary_input_jacobian(f_complex, z_unitary):
    r"""
    Computes the complex Jacobian ∂f/∂z of a complex
    function f: ℂ^{shape} → ℂ^{shape}, under the assumption that the input z
    is unitary along its outermost two dimensions.

    Args:
        f_complex (Callable): Function mapping unitary complex tensor z.
        z_unitary (torch.Tensor): Complex-valued unitary matrix..

    Returns:
        torch.Tensor: Adjusted Jacobian ∂f/∂z under the unitary constraint.

    Notes:

    - Differentiation Under Unitary Constraints:

        If U is unitary (U U† = I), the variation of U† is:

            dU† = -U† dU U†

        Substituting into the expression for df[i, j] yields, which is

            df[i, j] = Tr( (∂f[i, j]/∂z)^\top dZ + (∂f[i, j]/∂z̄)^\top dZ*)

        we obtain

            df[i, j] = Tr( (∂f[i, j]/∂z)^\top dU )
                     - Tr( U† (∂f[i, j]/∂z̄) U† dU )

        This implies a geometry-aware gradient:

            ∂f[i, j]/∂U = (∂f[i, j]/∂z) - (U† (∂f[i, j]/∂z̄) U†)^\top

        This structure respects the unitary constraint in gradient-based 
        optimization and manifold-aware learning.

    """
    # Compute standard complex Jacobian
    df_dz, df_dzstar = complex_jacobian(f_complex, z_unitary)

    # Apply unitary constraint correction
    z_conj = z_unitary.conj()
    df_dzunitary = df_dz - (z_conj @ df_dzstar.transpose(-2, -1) @ z_conj)

    return df_dzunitary
