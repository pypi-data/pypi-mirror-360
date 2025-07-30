###############################################################################
#
# (C) Copyright 2025 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from everysk.api.api_resources import Workspace
from everysk.core.unittests import TestCase


###############################################################################
#   Workspace TestCase Implementation
###############################################################################
class APIWorkspaceTestCase(TestCase):

    def test_workspace_class_name(self):
        self.assertEqual(Workspace.class_name(), 'workspace')
