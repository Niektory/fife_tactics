#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys, os
from fife import fife
from fife.extensions.pychan.fife_pychansettings import FifePychanSettings

from scripts.tactics import TacticsApplication

settings = FifePychanSettings(app_name="fife_tactics",
              settings_file="./settings.xml", 
              settings_gui_xml="")

if __name__ == '__main__':
	app = TacticsApplication(settings)
	app.run()
