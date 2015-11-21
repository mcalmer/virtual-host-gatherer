# Copyright (c) 2015 SUSE LLC, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# http://pubs.vmware.com/vsphere-55/topic/com.vmware.wssdk.apiref.doc/right-pane.html

"""
File Worker module implementation.
"""

from __future__ import print_function, absolute_import, division
import logging
from gatherer.modules import WorkerInterface
from collections import OrderedDict
import json

try:
    import urlparse
    import urlgrabber
    IS_VALID = True
except ImportError as ex:
    IS_VALID = False


class File(WorkerInterface):
    """
    Worker class for the VMWare.
    """

    DEFAULT_PARAMETERS = OrderedDict([('url', '')])

    def __init__(self):
        """
        Constructor.

        :return:
        """

        self.log = logging.getLogger(__name__)
        self.url = None

    # pylint: disable=R0801
    def set_node(self, node):
        """
        Set node information

        :param node: Dictionary of the node description.
        :return: void
        """

        try:
            self._validate_parameters(node)
        except AttributeError as error:
            self.log.error(error)
            raise error

        self.url = node['url']

    def parameters(self):
        """
        Return default parameters

        :return: default parameter dictionary
        """

        return self.DEFAULT_PARAMETERS

    def run(self):
        """
        Start worker.

        :return: Dictionary of the hosts in the worker scope.
        """

        self.log.debug("Fetching %s", self.url)
        if not urlparse.urlsplit(self.url).scheme:
            self.url = "file://%s" % self.url
        try:
            output = json.loads(urlgrabber.urlread(str(self.url), timeout=300))
        except Exception, e:
            self.log.error("Unable to fetch '%s': %s" % (str(self.url), e))
            return None
        # pylint: disable=W1622
        first = output.itervalues().next()
        if "vms" not in first:
            # run() should return a dict of host entries
            # but here the first value is a virtual host manager
            # and not a host entry
            return first
        return output

    def valid(self):
        """
        Check plugin class validity.

        :return: True if all components are installed
        """

        return IS_VALID