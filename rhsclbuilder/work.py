import logging
import os
import shutil
import tempfile

from rhsclbuilder import utils

LOG = logging.getLogger(__name__)


class Work(object):
    """A class to manage working directory."""

    def __init__(self, recipe):
        if recipe is None:
            raise ValueError('recipe is required.')

        self._recipe = recipe
        max_digit = len(str(recipe.num_of_package))
        self._num_dir_format = '%0{0}d'.format(str(max_digit))

        self._working_dir = tempfile.mkdtemp(prefix='rhscl-builder-')
        LOG.info('Working directory: %s', self._working_dir)

    @property
    def working_dir(self):
        return self._working_dir

    def close(self):
        if os.path.isdir(self._working_dir):
            shutil.rmtree(self._working_dir)

    def num_dir_name_from_count(self, count):
        num_dir_name = self._num_dir_format % count
        return num_dir_name

    def each_num_dir(self):
        if not os.path.isdir(self._working_dir):
            ValueError('working_dir does not exist.')

        count = 1
        for package_dict in self._recipe.each_normalized_package():
            num_dir_name = self.num_dir_name_from_count(count)
            num_dir = os.path.join(self._working_dir, num_dir_name)

            if not os.path.isdir(num_dir):
                os.makedirs(num_dir)
            with utils.pushd(num_dir):
                yield package_dict

            count += 1
        return True

    def each_package_dir(self):
        for package_dict in self.each_num_dir():
            package = package_dict['name']
            with utils.pushd(package):
                yield package_dict
        return True