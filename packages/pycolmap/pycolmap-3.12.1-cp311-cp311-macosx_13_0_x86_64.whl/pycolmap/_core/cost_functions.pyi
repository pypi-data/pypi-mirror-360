from __future__ import annotations
import pycolmap
import numpy
import typing

__all__: list[str] = [
    "AbsolutePosePositionPriorCost",
    "AbsolutePosePriorCost",
    "Point3DAlignmentCost",
    "RelativePosePriorCost",
    "ReprojErrorCost",
    "RigReprojErrorCost",
    "SampsonErrorCost",
]

@typing.overload
def AbsolutePosePositionPriorCost(
    position_in_world_prior: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    3-DoF error on the absolute camera pose's position.
    """

@typing.overload
def AbsolutePosePositionPriorCost(
    position_cov_in_world_prior: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]
    ],
    position_in_world_prior: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    3-DoF error on the absolute camera pose's position with prior covariance.
    """

@typing.overload
def AbsolutePosePriorCost(cam_from_world_prior: pycolmap.Rigid3d):
    """
    6-DoF error on the absolute camera pose.
    """

@typing.overload
def AbsolutePosePriorCost(
    cam_cov_from_world_prior: numpy.ndarray[
        tuple[typing.Literal[6], typing.Literal[6]], numpy.dtype[numpy.float64]
    ],
    cam_from_world_prior: pycolmap.Rigid3d,
):
    """
    6-DoF error on the absolute camera pose with prior covariance.
    """

@typing.overload
def Point3DAlignmentCost(
    point_in_b_prior: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Error between 3D points transformed by a 3D similarity transform.
    """

@typing.overload
def Point3DAlignmentCost(
    point_cov_in_b_prior: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[3]], numpy.dtype[numpy.float64]
    ],
    point_in_b_prior: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Error between 3D points transformed by a 3D similarity transform. with prior covariance
    """

@typing.overload
def RelativePosePriorCost(i_from_j_prior: pycolmap.Rigid3d):
    """
    6-DoF error between two absolute camera poses based on a prior relative pose.
    """

@typing.overload
def RelativePosePriorCost(
    i_cov_from_j_prior: numpy.ndarray[
        tuple[typing.Literal[6], typing.Literal[6]], numpy.dtype[numpy.float64]
    ],
    i_from_j_prior: pycolmap.Rigid3d,
):
    """
    6-DoF error between two absolute camera poses based on a prior relative pose with prior covariance.
    """

@typing.overload
def ReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Reprojection error.
    """

@typing.overload
def ReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D_cov: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[2]], numpy.dtype[numpy.float64]
    ],
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Reprojection error with 2D detection noise.
    """

@typing.overload
def ReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
    cam_from_world: pycolmap.Rigid3d,
):
    """
    Reprojection error with constant camera pose.
    """

@typing.overload
def ReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D_cov: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[2]], numpy.dtype[numpy.float64]
    ],
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
    cam_from_world: pycolmap.Rigid3d,
):
    """
    Reprojection error with constant camera pose and 2D detection noise.
    """

@typing.overload
def ReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
    point3D: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Reprojection error with constant 3D point.
    """

@typing.overload
def ReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D_cov: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[2]], numpy.dtype[numpy.float64]
    ],
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
    point3D: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Reprojection error with constant 3D point and 2D detection noise.
    """

@typing.overload
def RigReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Reprojection error for camera rig.
    """

@typing.overload
def RigReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D_cov: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[2]], numpy.dtype[numpy.float64]
    ],
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Reprojection error for camera rig with 2D detection noise.
    """

@typing.overload
def RigReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
    cam_from_rig: pycolmap.Rigid3d,
):
    """
    Reprojection error for camera rig with constant cam-from-rig pose.
    """

@typing.overload
def RigReprojErrorCost(
    camera_model_id: pycolmap.CameraModelId,
    point2D_cov: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[2]], numpy.dtype[numpy.float64]
    ],
    point2D: numpy.ndarray[
        tuple[typing.Literal[2], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
    cam_from_rig: pycolmap.Rigid3d,
):
    """
    Reprojection error for camera rig with constant cam-from-rig pose and 2D detection noise.
    """

def SampsonErrorCost(
    cam_ray1: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
    cam_ray2: numpy.ndarray[
        tuple[typing.Literal[3], typing.Literal[1]], numpy.dtype[numpy.float64]
    ],
):
    """
    Sampson error for two-view geometry.
    """
