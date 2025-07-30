"""Module for testing schema models, i.e. camera, sensor, calibration, reference."""

import pytest

import numpy as np
import sqlmodel as sqlm

import mynd.schemas as schemas


"""
Calibration unit tests:
 - test_calibration_initialization
 - test_projection_matrix
 - test_distortion_vector
 - test_projection_matrix_type
 - test_distortion_vector_type
 - test_calibration_with_different_values
"""


@pytest.fixture
def sample_calibration():
    return schemas.CalibrationSchema(
        id=1,
        width=1920,
        height=1080,
        fx=1000.0,
        fy=1000.0,
        cx=960.0,
        cy=540.0,
        k1=0.1,
        k2=0.2,
        k3=0.3,
        p1=0.01,
        p2=0.02,
    )


def test_calibration_initialization(sample_calibration):
    assert isinstance(sample_calibration, sqlm.SQLModel)
    assert sample_calibration.id == 1
    assert sample_calibration.width == 1920
    assert sample_calibration.height == 1080
    assert sample_calibration.fx == 1000.0
    assert sample_calibration.fy == 1000.0
    assert sample_calibration.cx == 960.0
    assert sample_calibration.cy == 540.0
    assert sample_calibration.k1 == 0.1
    assert sample_calibration.k2 == 0.2
    assert sample_calibration.k3 == 0.3
    assert sample_calibration.p1 == 0.01
    assert sample_calibration.p2 == 0.02


def test_projection_matrix(sample_calibration):
    expected_matrix = np.array(
        [[1000.0, 0.0, 960.0], [0.0, 1000.0, 540.0], [0.0, 0.0, 1.0]]
    )
    assert np.allclose(sample_calibration.projection_matrix, expected_matrix)


def test_distortion_vector(sample_calibration):
    expected_vector = np.array([0.1, 0.2, 0.01, 0.02, 0.3])
    assert np.allclose(sample_calibration.distortion_vector, expected_vector)


def test_projection_matrix_type(sample_calibration):
    assert isinstance(sample_calibration.projection_matrix, np.ndarray)
    assert sample_calibration.projection_matrix.shape == (3, 3)


def test_distortion_vector_type(sample_calibration):
    assert isinstance(sample_calibration.distortion_vector, np.ndarray)
    assert sample_calibration.distortion_vector.shape == (5,)


def test_calibration_with_different_values():
    cal = schemas.CalibrationSchema(
        id=2,
        width=640,
        height=480,
        fx=500.0,
        fy=500.0,
        cx=320.0,
        cy=240.0,
        k1=-0.1,
        k2=0.05,
        k3=0.0,
        p1=-0.001,
        p2=0.001,
    )

    expected_matrix = np.array(
        [[500.0, 0.0, 320.0], [0.0, 500.0, 240.0], [0.0, 0.0, 1.0]]
    )
    assert np.allclose(cal.projection_matrix, expected_matrix)

    expected_vector = np.array([-0.1, 0.05, -0.001, 0.001, 0.0])
    assert np.allclose(cal.distortion_vector, expected_vector)


"""
schemas.SensorSchema unit tests:
 - test_sensor_initialization
 - test_sensor_default_values
 - test_sensor_location_vector
 - test_sensor_rotation_matrix
 - test_sensor_location_vector_type
 - test_sensor_rotation_matrix_type
 - test_sensor_with_none_location_rotation
 - test_sensor_with_different_values
"""


@pytest.fixture
def sample_sensor(sample_calibration):
    return schemas.SensorSchema(
        id=1,
        label="Test schemas.SensorSchema",
        width=1920,
        height=1080,
        location=[1.0, 2.0, 3.0],
        rotation=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        calibration=sample_calibration,
    )


def test_sensor_initialization(sample_sensor, sample_calibration):
    assert isinstance(sample_sensor, sqlm.SQLModel)
    assert sample_sensor.id == 1
    assert sample_sensor.label == "Test schemas.SensorSchema"
    assert sample_sensor.width == 1920
    assert sample_sensor.height == 1080
    assert sample_sensor.location == [1.0, 2.0, 3.0]
    assert sample_sensor.rotation == [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    assert sample_sensor.calibration == sample_calibration


def test_sensor_default_values():
    sensor = schemas.SensorSchema(
        id=2, label="Default schemas.SensorSchema", width=640, height=480
    )
    assert sensor.location is None
    assert sensor.rotation is None
    assert sensor.calibration is None


def test_sensor_location_vector(sample_sensor):
    expected_vector = np.array([1.0, 2.0, 3.0])
    assert np.allclose(sample_sensor.location_vector, expected_vector)


def test_sensor_rotation_matrix(sample_sensor):
    expected_matrix = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    assert np.allclose(sample_sensor.rotation_matrix, expected_matrix)


def test_sensor_location_vector_type(sample_sensor):
    assert isinstance(sample_sensor.location_vector, np.ndarray)
    assert sample_sensor.location_vector.shape == (3,)


def test_sensor_rotation_matrix_type(sample_sensor):
    assert isinstance(sample_sensor.rotation_matrix, np.ndarray)
    assert sample_sensor.rotation_matrix.shape == (3, 3)


def test_sensor_with_none_location_rotation():
    sensor = schemas.SensorSchema(id=3, label="None Sensor", width=800, height=600)
    assert sensor.location_vector is None
    assert sensor.rotation_matrix is None


def test_sensor_with_different_values():
    sensor = schemas.SensorSchema(
        id=4,
        label="Different Sensor",
        width=3840,
        height=2160,
        location=[5.0, -2.0, 1.5],
        rotation=[[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]],
    )
    assert np.allclose(sensor.location_vector, np.array([5.0, -2.0, 1.5]))
    assert np.allclose(
        sensor.rotation_matrix,
        np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
    )


"""
Reference unit tests:
 - test_reference_initialization
 - test_reference_location_vector
 - test_reference_rotation_vector
 - test_reference_location_vector_type
 - test_reference_rotation_vector_type
 - test_reference_with_different_values
 - test_reference_property_immutability
 - test_reference_attributes
 - test_reference_str_representation
"""


@pytest.fixture
def sample_reference():
    return schemas.ReferenceSchema(
        id=1,
        epsg_code=4326,
        longitude=10.123,
        latitude=50.456,
        height=100.5,
        yaw=30.0,
        pitch=5.0,
        roll=0.5,
    )


def test_reference_initialization(sample_reference):
    assert isinstance(sample_reference, sqlm.SQLModel)
    assert sample_reference.id == 1
    assert sample_reference.epsg_code == 4326
    assert sample_reference.longitude == 10.123
    assert sample_reference.latitude == 50.456
    assert sample_reference.height == 100.5
    assert sample_reference.yaw == 30.0
    assert sample_reference.pitch == 5.0
    assert sample_reference.roll == 0.5


def test_reference_location_vector(sample_reference):
    expected_vector = np.array([10.123, 50.456, 100.5])
    assert np.allclose(sample_reference.location_vector, expected_vector)


def test_reference_rotation_vector(sample_reference):
    expected_vector = np.array([30.0, 5.0, 0.5])
    assert np.allclose(sample_reference.rotation_vector, expected_vector)


def test_reference_location_vector_type(sample_reference):
    assert isinstance(sample_reference.location_vector, np.ndarray)
    assert sample_reference.location_vector.shape == (3,)


def test_reference_rotation_vector_type(sample_reference):
    assert isinstance(sample_reference.rotation_vector, np.ndarray)
    assert sample_reference.rotation_vector.shape == (3,)


def test_reference_with_different_values():
    ref = schemas.ReferenceSchema(
        id=2,
        epsg_code=3857,
        longitude=-74.006,
        latitude=40.7128,
        height=10.0,
        yaw=180.0,
        pitch=-10.0,
        roll=2.5,
    )
    assert np.allclose(ref.location_vector, np.array([-74.006, 40.7128, 10.0]))
    assert np.allclose(ref.rotation_vector, np.array([180.0, -10.0, 2.5]))


def test_reference_property_immutability(sample_reference):
    location_vector = sample_reference.location_vector
    rotation_vector = sample_reference.rotation_vector

    # Attempt to modify the vectors
    location_vector[0] = 0
    rotation_vector[0] = 0

    # Check that the original properties are unchanged
    assert np.allclose(
        sample_reference.location_vector, np.array([10.123, 50.456, 100.5])
    )
    assert np.allclose(sample_reference.rotation_vector, np.array([30.0, 5.0, 0.5]))


@pytest.mark.parametrize(
    "attr",
    [
        "id",
        "epsg_code",
        "longitude",
        "latitude",
        "height",
        "yaw",
        "pitch",
        "roll",
    ],
)
def test_reference_attributes(sample_reference, attr):
    assert hasattr(sample_reference, attr)


def test_reference_str_representation(sample_reference):
    assert str(sample_reference) != ""
    assert repr(sample_reference) != ""
