#!/usr/bin/env python3

from typing import Dict, List, Tuple
import time
import pickle
import os


class BaseClass():
    def __eq__(self, other):
            return self.__dict__ == other.__dict__

class Credentials(BaseClass):
    """Class Credentials that contains the following fields
    Username - string
    Password - string
    Domain - string"""

    def __init__(self, username:str, password:str, domain:str):
            self.username = username
            self.password = password
            self.domain = domain

    def __repr__(self):
        return "credentials:{self.username}:{self.password}:{self.domain}"

class MountPoint(BaseClass):
    """Class MountPoint that contains following fields:
    Mount point name - string - Example: “c:\”
    Total size of the volume - int"""

    def __init__(self, name:str, size:int):
            self.name = name
            self.size = size

    def __repr__(self):
        return "mountpoint:{self.name}:{self.size}"


class Workload(BaseClass):
    """Class Workload that contains following fields:
    IP string, credentials of type Credentials
    Storage that contains list of instances of type MountPoint"""

    def __init__(self, ip:str, credentials:Credentials, storage:List[MountPoint]):
            self.ip = ip
            self.credentials = credentials
            self.storage = storage

    def __repr__(self):
        return f"workload:{self.ip}:{self.credentials}:{self.storage}"



class Source(BaseClass):
    """Add following business constraints to class Source:
    Username, password, IP should not be None
    IP cannot change for the specific source"""

    def __init__(self, ip:str, username:str, password:str):
        if not all((username, password, ip)):
            raise ValueError
        self.__ip = ip
        self.username = username
        self.password = password

    @property
    def ip(self):
        return self.__ip

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password


class MigrationTarget(BaseClass):
    """Class MigrationTarget that contains following fields:
    Cloud type: aws, azure, vsphere, vcloud - no other values are allowed
    Cloud Credentials of type Credentials
    Target Vm object of type Workload"""

    __cloud_types = ("aws", "azure", "vsphere", "vcloud")

    def __init__(self, cloud:str, cloud_credentials:Credentials, target_vm:Workload):
        if cloud in self.__cloud_types:
            self.__cloud_type = cloud
            self.cloud_credentials = cloud_credentials
            self.target_vm = target_vm
        else:
            raise ValueError

    def __repr__(self):
        return f"migration_target_class:{self.__cloud_type}:{self.cloud_credentials}:{self.target_vm}"


class Migration(BaseClass):
    """Define class Migration that contains the following
    Selected Mount points: list of MountPoint
    Source of type Workload
    Migration Target of type MigrationTarget
    Migration state: not started, running, error, success
    """

    volume_c_allowed = True

    def __init__(self, selected_mount_points:List[MountPoint], source:Workload, migration_target:MigrationTarget):
            self.selected_mount_points = selected_mount_points
            self.source = source
            self.migration_target = migration_target
            self.migration_state = "not started"

    def run(self):
        """Implement run() method -
           run method should sleep for X min (simulate running migration)
           copy source object to the Migration Target.
           Target VM  and target should only have mount points that are selected.
           For example, if source has: C:\ D: and E:\ and only C: was selected, target should only have C:\
           Implement business logic to not allow running migrations when volume C:\ is not allowed
        """
        X = .1
        self.migration_state = "running"
        source_storage_ok = False not in [y.name in [x.name for x in self.source.storage]
                                          for y in self.selected_mount_points]
        if self.volume_c_allowed and source_storage_ok:
            for source_storage in self.source.storage:
                if not source_storage.name in [x.name for x in self.selected_mount_points]:
                    continue
                self.migration_target.target_vm.storage.append(source_storage)

            self.migration_target.target_vm.ip = self.source.ip
            self.migration_target.target_vm.credentials = self.source.credentials
            time.sleep(X*60)
            self.migration_state = "success"
        else:
            self.migration_state = "error"

    def __repr__(self):
        return f"migration_class:{self.selected_mount_points}:{self.source}:{self.migration_target}:{self.migration_state}"


class PersistenceLayer():
    def __init__(self, class_objects_lst:List, pickle_file:str):
            self.class_objects_lst = class_objects_lst
            self.pickle_file = pickle_file

    def create(self, class_object_lst=None):
        ip_lst = {'Source': [], 'Migration': []}
        if class_object_lst == None or class_object_lst == []:
            class_object_lst = self.class_objects_lst
        for class_object in class_object_lst:
            if isinstance(class_object, Source):
                if class_object.ip in ip_lst['Source']:
                    continue
                ip_lst['Source'].append(class_object.ip)
            elif isinstance(class_object, Migration):
                ip_lst['Migration'].append(class_object.source.ip)
        with open(self.pickle_file, 'wb') as dump_file:
            pickle.dump(class_object, dump_file)

    def read(self):
        with open(self.pickle_file, 'rb') as dump_file:
            self.class_objects_lst = pickle.load(dump_file)
        return self.class_objects_lst


    def update(self):
        class_objects_lst = self.class_objects_lst[:]
        saved_class_objects_lst = self.read()
        for class_object in saved_class_objects_lst:
            if class_object in class_objects_lst:
                continue
            class_objects_lst.append(class_object)
        self.create(class_objects_lst)


    def delete(self):
        os.remove(self.pickle_file)
