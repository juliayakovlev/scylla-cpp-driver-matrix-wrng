import logging
import os
import shutil
import subprocess
import yaml
import processjunit


class Run:

    def __init__(self, cpp_driver_git, scylla_install_dir, tag, protocol):
        self._tag = tag
        self._cpp_driver_git = cpp_driver_git
        self._scylla_install_dir = scylla_install_dir
        self._protocol = protocol
        # self._xunit_file = self._get_xunit_file(self._setup_out_dir())
        self._run()
        # self._junit = self._process_output()

    # @property
    # def summary(self):
    #     return self._junit.summary

    def __repr__(self):
        details = dict(version=self._tag, protocol=self._protocol)
        # details.update(self._junit.summary)
        return '{version}: v{protocol}: testcases: {testcase},' \
            ' failures: {failure}, errors: {error}, skipped: {skipped},' \
            ' ignored_in_analysis: {ignored_in_analysis}'.format(**details)

    # def _setup_out_dir(self):
    #     here = os.path.dirname(__file__)
    #     xunit_dir = os.path.join(here, 'xunit', self._tag)
    #     if not os.path.exists(xunit_dir):
    #         os.makedirs(xunit_dir)
    #     return xunit_dir

    # def _get_xunit_file(self, xunit_dir):
    #     file_path = os.path.join(xunit_dir, 'nosetests.v{}.{}.xml'.format(self._protocol, self._tag))
    #     if os.path.exists(file_path):
    #         os.unlink(file_path)
    #     return file_path

    def _ignoreFile(self):
        here = os.path.dirname(__file__)
        return os.path.join(here, 'versions', self._tag, 'ignore.yaml')

    def _ignoreList(self):
        ignore_tests = []
        with open(self._ignoreFile()) as f:
            content = yaml.load(f)
            ignore_tests.extend(content['tests'])
        return ignore_tests

    def _environment(self):
        result = {}
        result.update(os.environ)
        result['PROTOCOL_VERSION'] = self._protocol
        result['INSTALL_DIRECTORY'] = self._scylla_install_dir
        return result

    def _apply_patch(self):
        here = os.path.dirname(__file__)
        patch_file = os.path.join(here, 'versions', self._tag, 'patch')
        if not os.path.exists(patch_file):
            raise Exception('Cannot find patch for version {}'.format(self._tag))
        command = "patch -p1 -i {}".format(patch_file)
        subprocess.check_call(command, shell=True)

    def _run(self):
        os.chdir(self._cpp_driver_git)
        subprocess.check_call('git checkout .'.format(self._tag), shell=True)
        subprocess.check_call('git checkout {}'.format(self._tag), shell=True)
        self._apply_patch()
        # exclude_str = ' '

        gtest_filter = ':'.join(self._ignoreList())
        # cmd = 'nosetests --with-xunit --xunit-file {} -s {} {}'.format(self._xunit_file, self._tests, exclude_str)
        cmd = f'./cassandra-integration-tests --install-dir=[{self._scylla_install_dir}] --version={self._tag} --category=CASSANDRA --verbose=ccm --gtest_filter={gtest_filter}'
        logging.info(cmd)
        subprocess.call(cmd.split(), env=self._environment())

    # def _process_output(self):
    #     junit = processjunit.ProcessJUnit(self._xunit_file, self._ignoreFile())
    #     content = open(self._xunit_file).read()
    #     open(self._xunit_file, 'w').write(content.replace('classname="', 'classname="version_{}_v{}_'.format(
    #         self._tag, self._protocol)))
    #     return junit
