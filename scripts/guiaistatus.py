# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI

class GUIAIStatus:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("AIStatus.layout","AIStatus/")
		self.progress_bar = self.window.getChild("AIStatus/ProgressBar")

	def show(self):
		self.window.show()
		self.window.moveToFront()
		self.progress_bar.setProgress(0)
