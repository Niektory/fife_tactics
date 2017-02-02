#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

from fife import fife
import PyCEGUI

from timeline import TacticsTimer

class SayBubble(fife.InstanceDeleteListener):
	def __init__(self, application, instance, text, time):
		fife.InstanceDeleteListener.__init__(self)
		self.application = application
		self.instance = instance
		self.text = text
		self.timer = TacticsTimer("SayBubble", time, 1, self.destroy, self.adjustPosition)
		self.application.real_timeline.addTimer(self.timer)
		self.instance.addDeleteListener(self)
		self.bubble = PyCEGUI.WindowManager.getSingleton().createWindow("TaharezLook/StaticText", "SayBubble/" + str(self.instance.getFifeId()))
		self.application.gui.root.addChildWindow(self.bubble)
		self.bubble.setText(text)
		self.bubble.setProperty("UnifiedSize", "{{0," + self.bubble.getProperty("HorzExtent") + "},{0," + self.bubble.getProperty("VertExtent") + "}}")
		self.bubble.setProperty("FrameEnabled", "False")
		self.bubble.setProperty("BackgroundEnabled", "False")

	def adjustPosition(self):
		coords = self.application.camera.toScreenCoordinates(self.instance.getLocation().getMapCoordinates())
		self.bubble.setProperty("UnifiedPosition", "{{0," + str(coords.x) + "},{0," + str(coords.y) + "}}")

	def destroy(self):
		PyCEGUI.WindowManager.getSingleton().destroyWindow("SayBubble/" + str(self.instance.getFifeId()))
		if self.application.gui.bubbles.count(self):
			self.application.gui.bubbles.remove(self)
		if self.application.real_timeline.timers.count(self.timer):
			self.application.real_timeline.timers.remove(self.timer)

	def onInstanceDeleted(self, instance):
		self.destroy()

