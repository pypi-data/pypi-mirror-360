import json

from dataclasses import dataclass, asdict, field

@dataclass
class BackupFileInfo:
    size: str = None
    backup_date: str = None
    backup_name: str = None
    sha1sum: str = None
    def __str__(self):
        '''String representation of that DataClass is valid json string'''
        return json.dumps(asdict(self), default=str)

@dataclass
class BackupMetadata:
    '''Class contain fields with info about backup'''
    type: str = None
    size: str = None
    time: str = None
    customer: str = None
    placement: str = None
    backup_name: str = None
    description: str = None
    last_backup_date: str = None
    count_of_backups: str = None
    supposed_backups_count: str = None
    sha1sum: str = None
    backups: list[BackupFileInfo] = field(default_factory=list)
    def __str__(self):
        '''String representation of that DataClass is valid json string'''
        return json.dumps(asdict(self), default=str)
