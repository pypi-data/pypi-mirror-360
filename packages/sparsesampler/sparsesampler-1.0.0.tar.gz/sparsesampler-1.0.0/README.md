# sParseSampler
A python package for fast sampling with applications on flow cytometry and scRNA-seq data focusing on retaining rare cell populations.

# Sparse Sampler Visualization

This project demonstrates a step-by-step sparse sampling process using toy data and PCA binning.

## Animated Sampling Process

The following animation shows how points are selected from a 2D toy dataset using PCA binning. Points are selected category by category (cells with 1 point, 2 points, etc.), and the process is visualized step by step:

- All points start as skyblue.
- When a category is considered, the cells are highlighted in yellow and the points in those cells are shown in gray for visibility.
- Selected points turn red and remain red in all subsequent frames.
- The process continues until the target number of points is reached.

![Sampling Process Animation](./sampling_process.gif)

## Usage

To generate the animation, run:

```bash
python -m sparsesampler.visualization
```

The animation will be saved as `sampling_process.gif` in the project directory.
