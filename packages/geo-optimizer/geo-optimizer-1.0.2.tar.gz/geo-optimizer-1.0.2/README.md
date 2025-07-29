# GEO-OPTIMIZER
**Genetic & Evolutionary Optimizer for Neural Networks**

> A minimal, fully-customizable, mutation-based neural network optimizer inspired by evolutionary algorithms. No gradient descent. Just evolution.

---

## What is GEO-OPTIMIZER?

**GEO (Genetic and Evolutionary Optimizer)** is a lightweight PyTorch-based framework for training neural networks using **evolutionary strategies** instead of traditional backpropagation.

- **No gradients**
- **No backward()**
- Works with any activation/loss functions
- Optimizes with mutation, selection, and survival of the fittest

---

## How It Works

At each generation:
1. A **population** of mutated neural networks is generated.
2. Each network is evaluated using a **loss function**.
3. The **top 2 performers** are selected.
4. New weights are **blended and passed** to the next generation.

---

## Installation

```bash
pip install geo-optimizer
