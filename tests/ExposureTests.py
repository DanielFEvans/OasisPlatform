import io
import os
import inspect
import sys
import unittest
from flask import json
import shutil


TEST_DIRECTORY = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
TEST_DATA_DIRECTORY = os.path.abspath(os.path.join(TEST_DIRECTORY, 'data'))
LIB_PATH = os.path.abspath(os.path.join(TEST_DIRECTORY, '..', 'src'))
sys.path.append(LIB_PATH)

import app

class Test_ExposureTests(unittest.TestCase):
    ''' 
    Exposure API tests
    '''

    def touch(self, path):
        with open(path, 'a'):
            os.utime(path, None)

    def clean_directories(self):
        if os.path.exists(app.EXPOSURE_DATA_DIRECTORY):
            shutil.rmtree(app.EXPOSURE_DATA_DIRECTORY)
        os.makedirs(app.EXPOSURE_DATA_DIRECTORY)
        
        if os.path.exists(TEST_DATA_DIRECTORY):
            shutil.rmtree(TEST_DATA_DIRECTORY)
        os.makedirs(TEST_DATA_DIRECTORY)

    def setUp(self):
        app.DO_GZIP_RESPONSE = False
        exposure_data_directory = os.path.join(TEST_DIRECTORY, 'data')
        app.EXPOSURE_DATA_DIRECTORY = exposure_data_directory
        app.APP.config['TESTING'] = True
        self.app = app.APP.test_client()

    def test_get_exposure_1(self):
        self.clean_directories()
        self.touch(os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test1.tar'))
        self.touch(os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test2.tar'))
        self.touch(os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test3.tar'))
        self.touch(os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test4.tar'))
        response = self.app.get("/exposure")
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 4
        assert sum(1 for exposure in exposures if exposure['location'] == 'test1') == 1
        assert sum(1 for exposure in exposures if exposure['location'] == 'test2') == 1
        assert sum(1 for exposure in exposures if exposure['location'] == 'test3') == 1
        assert sum(1 for exposure in exposures if exposure['location'] == 'test4') == 1

    def test_get_exposure_by_location_1(self):
        self.clean_directories()
        self.touch(os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test1.tar'))
        response = self.app.get("/exposure/test1")
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 1
        assert sum(1 for exposure in exposures if exposure['location'] == 'test1') == 1

    def test_post_exposure_1(self):
        self.clean_directories()
        filepath = os.path.join(TEST_DIRECTORY, 'post1.tar')
        self.touch(filepath)
        with io.open(filepath, 'rb') as file_to_upload:
            response = self.app.post(
                "/exposure", 
                data = {
                    'file': (file_to_upload, filepath),
                }, 
                content_type='multipart/form-data')
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 1

    def test_delete_exposure_1(self):
        self.clean_directories()
        filepath1 = os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test1.tar')
        filepath2 = os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test2.tar')
        self.touch(filepath1)
        self.touch(filepath2)
        response = self.app.delete("/exposure")
        assert response._status_code == 200
        assert not os.path.exists(filepath1)
        assert not os.path.exists(filepath2)

    def test_delete_exposure_by_location_1(self):
        self.clean_directories()
        filepath1 = os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test1.tar')
        filepath2 = os.path.join(app.EXPOSURE_DATA_DIRECTORY, 'test2.tar')
        self.touch(filepath1)
        self.touch(filepath2)
        response = self.app.delete("/exposure/test1")
        assert response._status_code == 200
        assert not os.path.exists(filepath1)
        assert os.path.exists(filepath2)

    def test_exposure_roundtrip_1(self):
        self.clean_directories()
        filepath = os.path.join(TEST_DIRECTORY, 'post1.tar')
        self.touch(filepath)
        with io.open(filepath, 'rb') as file_to_upload:
            response = self.app.post(
                "/exposure", 
                data = {
                    'file': (file_to_upload, filepath),
                }, 
                content_type='multipart/form-data')
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 1
        location = exposures[0]['location']
        response = self.app.get("/exposure/" + location)
        assert response._status_code == 200
        exposures = json.loads(response.data.decode('utf-8'))['exposures']
        assert len(exposures) == 1
        assert sum(1 for exposure in exposures if exposure['location'] == location) == 1
        response = self.app.delete("/exposure/" + location)
        assert response._status_code == 200
        response = self.app.get("/exposure/" + location)
        assert response._status_code == 404

if __name__ == '__main__':
    unittest.main()