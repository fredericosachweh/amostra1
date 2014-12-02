import sys
import os

if 'test' in sys.argv:
    from tempfile import mkdtemp
    from .settings import (
        DEBUG,
        PROJECT_ROOT_PATH,
        MULTICAT_LOGS_DIR,
        MULTICAT_SOCKETS_DIR,
        DVBLAST_CONFS_DIR,
        DVBLAST_LOGS_DIR,
        DVBLAST_SOCKETS_DIR,
        VLC_VIDEOFILES_DIR,
        CHANNEL_RECORD_DIR,
        NBRIDGE_LOGS_DIR,
        NBRIDGE_SOCKETS_DIR,
        NBRIDGE_UPSTREAM,
        NBRIDGE_CONF_DIR,
        NBRIDGE_UPSTREAM_DIR
    )
    # Create a temporary dir for when running tests
    tmpdir = mkdtemp(prefix='iptv-test-')
    os.chmod(tmpdir, 0o777)
    # Change vars to point the new location
    MULTICAT_LOGS_DIR = tmpdir + MULTICAT_LOGS_DIR
    os.makedirs(MULTICAT_LOGS_DIR)
    os.chmod(MULTICAT_LOGS_DIR, 0o777)
    MULTICAT_SOCKETS_DIR = tmpdir + MULTICAT_SOCKETS_DIR
    os.makedirs(MULTICAT_SOCKETS_DIR)
    os.chmod(MULTICAT_SOCKETS_DIR, 0o777)
    DVBLAST_CONFS_DIR = tmpdir + DVBLAST_CONFS_DIR
    os.makedirs(DVBLAST_CONFS_DIR)
    os.chmod(DVBLAST_CONFS_DIR, 0o777)
    DVBLAST_LOGS_DIR = tmpdir + DVBLAST_LOGS_DIR
    os.makedirs(DVBLAST_LOGS_DIR)
    os.chmod(DVBLAST_LOGS_DIR, 0o777)
    DVBLAST_SOCKETS_DIR = tmpdir + DVBLAST_SOCKETS_DIR
    os.makedirs(DVBLAST_SOCKETS_DIR)
    os.chmod(DVBLAST_SOCKETS_DIR, 0o777)
    VLC_VIDEOFILES_DIR = tmpdir + VLC_VIDEOFILES_DIR
    os.makedirs(VLC_VIDEOFILES_DIR)
    os.chmod(VLC_VIDEOFILES_DIR, 0o777)
    CHANNEL_RECORD_DIR = tmpdir + CHANNEL_RECORD_DIR
    os.makedirs(CHANNEL_RECORD_DIR)
    os.chmod(CHANNEL_RECORD_DIR, 0o777)
    # Pseudo executables folder
    HELPER_FOLDER = os.path.join(PROJECT_ROOT_PATH, 'device', 'helper')
    # Settings to replace
    DVBLAST_DUMMY = os.path.join(HELPER_FOLDER, 'dvblast_dummy.py')
    DVBLASTCTL_DUMMY = os.path.join(HELPER_FOLDER, 'dvblastctl_dummy.py')
    MULTICAT_DUMMY = os.path.join(HELPER_FOLDER, 'multicat_dummy.py')
    MULTICATCTL_DUMMY = os.path.join(HELPER_FOLDER, 'multicatctl_dummy.py')
    VLC_DUMMY = os.path.join(HELPER_FOLDER, 'vlc_dummy.py')
    # Settings nbridge
    NBRIDGE_LOGS_DIR = tmpdir + NBRIDGE_LOGS_DIR
    os.makedirs(NBRIDGE_LOGS_DIR)
    os.chmod(NBRIDGE_LOGS_DIR, 0o777)
    NBRIDGE_SOCKETS_DIR = tmpdir + NBRIDGE_SOCKETS_DIR
    os.makedirs(NBRIDGE_SOCKETS_DIR)
    os.chmod(NBRIDGE_SOCKETS_DIR, 0o777)
    NBRIDGE_UPSTREAM = tmpdir + NBRIDGE_UPSTREAM
    NBRIDGE_CONF_DIR = tmpdir + NBRIDGE_CONF_DIR
    os.makedirs(NBRIDGE_CONF_DIR)
    os.chmod(NBRIDGE_CONF_DIR, 0o777)
    NBRIDGE_UPSTREAM_DIR = tmpdir + NBRIDGE_UPSTREAM_DIR
    os.makedirs(NBRIDGE_UPSTREAM_DIR)
    os.chmod(NBRIDGE_UPSTREAM_DIR, 0o777)
    NBRIDGE_SERVER_KEY = 'fake'

TASTYPIE_FULL_DEBUG = DEBUG
TASTYPIE_ABSTRACT_APIKEY = False
FORCE_SCRIPT_NAME = ""
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
