# complex_jacobian

**Jacobian calculation of complex-valued matrix functions using PyTorch.**

This package implements automatic differentiation (AD) for complex-valued
functions using PyTorch, with a focus on computing Jacobians of functions
mapping complex matrices to complex matrices. It is particularly useful
in domains like quantum computing and manifold optimization, where complex
gradients must be handled with care.


## Features

- ✅ Compute complex-valued Jacobians ∂f/∂z and ∂f/∂𝑧̄ (Wirtinger derivatives)
  using real-valued PyTorch autograd.
- ✅ Specialized support for **unitary matrix input** — ideal for applications
  in quantum physics and geometric optimization.

## Installation

```bash
pip install complex_jacobian
```

## Motivation

PyTorch's autograd system is designed for real-valued functions. However,
many applications in science and engineering require differentiation
of complex-valued functions, particularly over complex matrices or unitary
groups. This package bridges that gap by:

- Representing complex tensors as real + imaginary parts.
- Computing real-valued Jacobians using PyTorch.
- Reconstructing complex derivatives, including Wirtinger derivatives ∂f/∂z
  and ∂f/∂𝑧̄.

## Core Functions

- `complex_jacobian(func, z)`:
  Computes the Jacobian of a complex-valued function func evaluated at complex
  input z, and returns Wirtinger derivatives:
  - ∂f/∂z (holomorphic part)
  - ∂f/∂𝑧̄ (antiholomorphic part)

- `unitary_input_jacobian(func, z)`:
  Computes the Jacobian of func(z) under the constraint that z is unitary.
