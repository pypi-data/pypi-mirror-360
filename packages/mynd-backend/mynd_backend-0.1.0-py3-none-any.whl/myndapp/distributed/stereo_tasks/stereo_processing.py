"""Module for stereo processing tasks."""

import mynd.database as db
import mynd.records as records
import mynd.schemas as schemas
import mynd.geometry.stereo as stereo

from mynd.utils.containers import Pair

from myndapp.api.server import load_application_database
from myndapp.api.settings import ApplicationSettings
from myndapp.distributed.worker import celery_app


@celery_app.task
def process_stereo_rectification(settings: ApplicationSettings, rig_id: int) -> None:
    """Rectifies a stereo rig."""

    engine: db.Engine = load_application_database(settings)

    with db.Session(engine) as session:
        stereo_rig: records.StereoRigRecord | None = session.get(
            records.StereoRigRecord, rig_id
        )
        if stereo_rig is None:
            return

        # If the stereo rig already has rectified sensors, we delete them and the
        # corresponding pixel maps
        if stereo_rig.is_rectified():
            delete_stereo_rig_rectification(session, stereo_rig)

        assert not stereo_rig.is_rectified(), "rectified sensors not deleted"
        assert not stereo_rig.has_pixel_maps(), "rectified maps not deleted"

        stereo_rig: records.StereoRigRecord = compute_stereo_rig_rectification(
            session, stereo_rig
        )


def delete_stereo_rig_rectification(
    session: db.Session, stereo_rig: records.StereoRigRecord
) -> None:
    """Deletes the rectified sensors and pixel maps for a stereo rig."""
    rectified_master: records.RectifiedSensorRecord = (
        stereo_rig.sensors.master.rectified_sensor
    )
    rectified_slave: records.RectifiedSensorRecord = (
        stereo_rig.sensors.slave.rectified_sensor
    )

    stereo_rig.sensors.master.sensor.rectified_sensor_id = None
    stereo_rig.sensors.slave.sensor.rectified_sensor_id = None

    master_pixel_map: records.StereoRigRecord.PixelMap = (
        stereo_rig.sensors.master.pixel_map
    )
    slave_pixel_map: records.StereoRigRecord.PixelMap = (
        stereo_rig.sensors.slave.pixel_map
    )

    stereo_rig.sensors.master.pixel_map_id = None
    stereo_rig.sensors.slave.pixel_map_id = None

    if rectified_master:
        session.delete(rectified_master)
    if rectified_slave:
        session.delete(rectified_slave)
    if master_pixel_map:
        session.delete(master_pixel_map)
    if slave_pixel_map:
        session.delete(slave_pixel_map)

    session.commit()
    session.refresh(stereo_rig)


def compute_stereo_rig_rectification(
    session: db.Session, stereo_rig_record: records.StereoRigRecord
) -> records.StereoRigRecord:
    """Computes rectified sensors and pixel maps for a stereo rig."""

    stereo_rig_schema: schemas.StereoRigSchema = schemas.StereoRigSchema.model_validate(
        stereo_rig_record
    )

    stereo.rectify_stereo_sensors(stereo_rig_schema.sensors)

    assert (
        stereo_rig_schema.sensors.master.is_rectified()
    ), "master sensor is not rectified"
    assert (
        stereo_rig_schema.sensors.slave.is_rectified()
    ), "slave sensor is not rectified"

    # Convert rectified sensors schemas to records and update record components
    stereo_rig_record.sensors.master.rectified_sensor = _convert_rectified_sensor(
        stereo_rig_schema.sensors.master.rectified_sensor
    )
    stereo_rig_record.sensors.slave.rectified_sensor = _convert_rectified_sensor(
        stereo_rig_schema.sensors.slave.rectified_sensor
    )

    # Update stereo sensors chunk
    stereo_rig_record.sensors.chunk = stereo_rig_record.chunk

    # Compute pixel maps to convert stereo sensors to rectified stereo sensors
    pixel_maps: Pair[stereo.PixelMap] = stereo.compute_stereo_rectification_map(
        stereo_rig_schema.sensors,
    )

    # Update the pixel maps of the stereo rig record
    stereo_rig_record.sensors.master.pixel_map = records.PixelMapRecord(
        values=pixel_maps.first.to_array().tolist()
    )
    stereo_rig_record.sensors.slave.pixel_map = records.PixelMapRecord(
        values=pixel_maps.second.to_array().tolist()
    )

    session.add(stereo_rig_record)
    session.commit()
    session.refresh(stereo_rig_record)

    return stereo_rig_record


def _convert_rectified_sensor(
    sensor_schema: schemas.SensorSchema,
) -> records.RectifiedSensorRecord:
    """Converts a sensor schema to a rectified sensor record."""
    calibration: records.RectifiedCalibrationRecord = (
        records.RectifiedCalibrationRecord.model_validate(
            sensor_schema.calibration.model_dump()
        )
    )
    sensor_record: records.RectifiedSensorRecord = (
        records.RectifiedSensorRecord.model_validate(sensor_schema.model_dump())
    )
    sensor_record.calibration = calibration
    return sensor_record
