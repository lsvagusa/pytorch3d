#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.
"""
This example demonstrates the most trivial, direct interface of the pulsar
sphere renderer. It renders and saves an image with 10 random spheres.
Output: basic.png.
"""
import math
from os import path

import imageio
import torch
from pytorch3d.renderer.points.pulsar import Renderer


torch.manual_seed(1)

n_points = 10
width = 1_000
height = 1_000
device = torch.device("cuda")
# The PyTorch3D system is right handed; in pulsar you can choose the handedness.
# For easy reproducibility we use a right handed coordinate system here.
renderer = Renderer(width, height, n_points, right_handed_system=True).to(device)
# Generate sample data.
vert_pos = torch.rand(n_points, 3, dtype=torch.float32, device=device) * 10.0
vert_pos[:, 2] += 25.0
vert_pos[:, :2] -= 5.0
vert_col = torch.rand(n_points, 3, dtype=torch.float32, device=device)
vert_rad = torch.rand(n_points, dtype=torch.float32, device=device)
cam_params = torch.tensor(
    [
        0.0,
        0.0,
        0.0,  # Position 0, 0, 0 (x, y, z).
        0.0,
        math.pi,  # Because of the right handed system, the camera must look 'back'.
        0.0,  # Rotation 0, 0, 0 (in axis-angle format).
        5.0,  # Focal length in world size.
        2.0,  # Sensor size in world size.
    ],
    dtype=torch.float32,
    device=device,
)
# Render.
image = renderer(
    vert_pos,
    vert_col,
    vert_rad,
    cam_params,
    1.0e-1,  # Renderer blending parameter gamma, in [1., 1e-5].
    45.0,  # Maximum depth.
)
print("Writing image to `%s`." % (path.abspath("basic.png")))
imageio.imsave("basic.png", (image.cpu().detach() * 255.0).to(torch.uint8).numpy())
