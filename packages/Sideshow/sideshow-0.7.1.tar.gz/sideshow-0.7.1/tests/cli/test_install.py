# -*- coding: utf-8; -*-

from unittest.mock import MagicMock, patch

from wuttjamaican.testing import ConfigTestCase
from wuttjamaican.install import InstallHandler

from sideshow.cli import install as mod


class TestInstall(ConfigTestCase):

    def test_run(self):
        ctx = MagicMock(params={})
        ctx.parent.wutta_config = self.config
        with patch.object(InstallHandler, 'run') as run:
            mod.install(ctx)
            run.assert_called_once_with()
