#!/usr/bin/env python3

import unittest
import mainapp as app
import time
import os


class TestCredentials(unittest.TestCase):

    def test_credintials(self):
        c = app.Credentials('name', 'pass', 'domain')
        self.assertEqual(c.username, 'name')
        self.assertEqual(c.password, 'pass')
        self.assertEqual(c.domain, 'domain')

class TestMountPoint(unittest.TestCase):
    def test_mount_point(self):
        mp = app.MountPoint('c:', 10)
        self.assertEqual(mp.name, 'c:')
        self.assertEqual(mp.size, 10)

class TestWorkload(unittest.TestCase):
    def setUp(self):
        self.credentials = app.Credentials('name', 'pass', 'domain')
        self.storage = [app.MountPoint('c:', 10), app.MountPoint('d:', 10)]

    def test_workload(self):
        workload = app.Workload('192.168.1.1', self.credentials, self.storage)
        self.assertEqual(workload.ip, '192.168.1.1')
        self.assertEqual(workload.credentials, self.credentials)
        self.assertEqual(workload.storage, self.storage)

    

class TestSource(unittest.TestCase):
    def setUp(self):
        self.s = app.Source('192.168.1.1', 'user', 'pass')

    def test_source(self):
        self.assertEqual(self.s.ip, '192.168.1.1')
        self.assertEqual(self.s.get_username(), 'user')
        self.assertEqual(self.s.get_password(), 'pass')

    def test_ip_none(self):
        self.assertRaises(ValueError, app.Source, None, 'user', 'pass')

    def test_username_none(self):
        self.assertRaises(ValueError, app.Source, '192.168.1.1', None, 'pass')

    def test_password_none(self):
        self.assertRaises(ValueError, app.Source, '192.168.1.1', 'user', None)



class TestMigrationTarget(unittest.TestCase):
    def setUp(self):
        self.cloud_credentials = app.Credentials('cloudname', 'cloudpass', 'domain')
        self.credentials = app.Credentials('name', 'pass', 'domain')
        self.storage = [app.MountPoint('c:', 10), app.MountPoint('d:', 10)]
        self.target_vm = app.Workload('192.168.1.1', self.credentials, self.storage)
        self.mt = app.MigrationTarget("aws", self.cloud_credentials, self.target_vm)

    def test_cloud_type_not_in_set(self):
        self.assertRaises(ValueError,
                          app.MigrationTarget,
                          "google",
                          self.cloud_credentials,
                          self.target_vm)


class TestMigration(unittest.TestCase):
    def setUp(self):
        self.selected_mount_points = [app.MountPoint('c:', 10)]
        self.source_credentials = app.Credentials('name',
                                                  'pass',
                                                  'sourcedomain')
        self.source_storage = [app.MountPoint('c:', 10),
                               app.MountPoint('d:', 10),
                               app.MountPoint('e:', 10)]


        self.source = app.Workload('192.168.1.1',
                                   self.source_credentials,
                                   self.source_storage)

        self.cloud_credentials = app.Credentials('cloudname',
                                                 'cloudpass',
                                                 'clouddomain')
        
        self.target_credentials = app.Credentials('targetname',
                                                  'tergetpass',
                                                  'tergetdomain')

        self.target_storage = [app.MountPoint('f:', 10),
                               app.MountPoint('g:', 10)]

        self.target_vm = app.Workload('192.168.1.2',
                                      self.target_credentials,
                                      self.target_storage)

        self.migration_target = app.MigrationTarget("aws",
                                                    self.cloud_credentials,
                                                    self.target_vm)

        self.migration = app.Migration(self.selected_mount_points,
                                       self.source,
                                       self.migration_target)

    def test_proper_migration(self):
        self.assertEqual(self.migration.selected_mount_points,
                         self.selected_mount_points)
        self.assertEqual(self.migration.source, self.source)
        self.assertEqual(self.migration.migration_target,
                         self.migration_target)



if __name__ == "__main__":
    unittest.main()
