#!/usr/bin/env python3
# Copyright (c) Facebook, Inc. and its affiliates. All rights reserved.
"""
This example demonstrates the most trivial use of the pulsar PyTorch3D
interface for sphere renderering. It renders and saves an image with
10 random spheres.
Output: basic-pt3d.png.
"""
from os import path

import imageio
import torch
from pytorch3d.renderer import PerspectiveCameras  # , look_at_view_transform
from pytorch3d.renderer import (
    PointsRasterizationSettings,
    PointsRasterizer,
    PulsarPointsRenderer,
)
from pytorch3d.structures import Pointclouds


torch.manual_seed(1)

n_points = 10
width = 1_000
height = 1_000
device = torch.device("cuda")

# Generate sample data.
vert_pos = torch.rand(n_points, 3, dtype=torch.float32, device=device) * 10.0
vert_pos[:, 2] += 25.0
vert_pos[:, :2] -= 5.0
vert_col = torch.rand(n_points, 3, dtype=torch.float32, device=device)
pcl = Pointclouds(points=vert_pos[None, ...], features=vert_col[None, ...])
# Alternatively, you can also use the look_at_view_transform to get R and T:
# R, T = look_at_view_transform(
#     dist=30.0, elev=0.0, azim=180.0, at=((0.0, 0.0, 30.0),), up=((0, 1, 0),),
# )
cameras = PerspectiveCameras(
    # The focal length must be double the size for PyTorch3D because of the NDC
    # coordinates spanning a range of two - and they must be normalized by the
    # sensor width (see the pulsar example). This means we need here
    # 5.0 * 2.0 / 2.0 to get the equivalent results as in pulsar.
    focal_length=(5.0 * 2.0 / 2.0,),
    R=torch.eye(3, dtype=torch.float32, device=device)[None, ...],
    T=torch.zeros((1, 3), dtype=torch.float32, device=device),
    image_size=((width, height),),
    device=device,
)
vert_rad = torch.rand(n_points, dtype=torch.float32, device=device)
raster_settings = PointsRasterizationSettings(
    image_size=(width, height),
    radius=vert_rad,
)
rasterizer = PointsRasterizer(cameras=cameras, raster_settings=raster_settings)
renderer = PulsarPointsRenderer(rasterizer=rasterizer).to(device)
# Render.
image = renderer(
    pcl,
    gamma=(1.0e-1,),  # Renderer blending parameter gamma, in [1., 1e-5].
    znear=(1.0,),
    zfar=(45.0,),
    radius_world=True,
    bg_col=torch.ones((3,), dtype=torch.float32, device=device),
)[0]
print("Writing image to `%s`." % (path.abspath("basic-pt3d.png")))
imageio.imsave("basic-pt3d.png", (image.cpu().detach() * 255.0).to(torch.uint8).numpy())
