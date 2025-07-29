from .base import (
    DJBackUpBase, DJFileBackUp, DJDataBaseBackUp, DJBackUpStorageResult, DJStorage, DJFile, TaskSchedule
)
from .notification import *


def get_backup_object(backup_id):
    return DJBackUpBase.objects.get_subclass(id=backup_id)


__all__ = [
    'DJBackUpBase', 'DJFileBackUp', 'DJDataBaseBackUp',
    'DJBackUpStorageResult', 'DJStorage', 'DJFile',
    'DJBackupLog', 'TaskSchedule',
    'get_backup_object',
]
