# Copyright 2019 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import


def setup_tobiko_config(conf):
    # pylint: disable=unused-argument
    from tobiko.tripleo import _ansible
    from tobiko.tripleo import overcloud
    from tobiko.tripleo import topology

    _ansible.setup_undercloud_ansible_playbook()
    overcloud.setup_overcloud_keystone_credentials()
    topology.setup_tripleo_topology()
