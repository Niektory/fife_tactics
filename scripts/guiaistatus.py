# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI

class GUIAIStatus:
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("AIStatus.layout")
		self.progress_bar = self.window.getChild("ProgressBar")

	def show(self):
		self.window.show()
		self.window.moveToFront()
		self.progress_bar.setProgress(0)
