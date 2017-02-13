#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from scripts.error import LogException

if __name__ == '__main__':
	with LogException():
		from fife.extensions.pychan.fife_pychansettings import FifePychanSettings
		from scripts.tactics import TacticsApplication
		settings = FifePychanSettings(
			app_name="fife_tactics",
			settings_file="./settings.xml",
			settings_gui_xml="")
		application = TacticsApplication(settings)
		application.run()
