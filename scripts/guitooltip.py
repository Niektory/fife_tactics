#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

import PyCEGUI

class GUITooltip:
	# TODO: merge the shadows with the main window
	def __init__(self):
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("Tooltip.layout","Tooltip/")
		self.shadow = self.window.clone("TooltipShadow")
		self.shadow2 = self.window.clone("TooltipShadow2")
		self.shadow3 = self.window.clone("TooltipShadow3")
		self.shadow4 = self.window.clone("TooltipShadow4")

	def clear(self):
		self.window.setText("")
		self.window.hide()
		self.shadow.setText("")
		self.shadow.hide()
		self.shadow2.setText("")
		self.shadow2.hide()
		self.shadow3.setText("")
		self.shadow3.hide()
		self.shadow4.setText("")
		self.shadow4.hide()
		self.messages = ""
		self.shadow_messages = ""

	def printMessage(self, message, color = ""):
		if PyCEGUI.System.getSingleton().getWindowContainingMouse().getType() == "DefaultWindow":
			self.window.show()
			self.messages += (color + message + "\n")
			self.window.setText(self.messages)
			self.window.setProperty("UnifiedSize", "{{0," + self.window.getProperty("HorzExtent") + "},{0," + self.window.getProperty("VertExtent") + "}}")
			self.shadow.show()
			self.shadow_messages += (message + "\n")
			self.shadow.setText("[colour='FF000000']" + self.shadow_messages)
			self.shadow.setProperty("UnifiedSize", "{{0," + self.window.getProperty("HorzExtent") + "},{0," + self.window.getProperty("VertExtent") + "}}")
			self.shadow2.show()
			self.shadow2.setText("[colour='FF000000']" + self.shadow_messages)
			self.shadow2.setProperty("UnifiedSize", "{{0," + self.window.getProperty("HorzExtent") + "},{0," + self.window.getProperty("VertExtent") + "}}")
			self.shadow3.show()
			self.shadow3.setText("[colour='FF000000']" + self.shadow_messages)
			self.shadow3.setProperty("UnifiedSize", "{{0," + self.window.getProperty("HorzExtent") + "},{0," + self.window.getProperty("VertExtent") + "}}")
			self.shadow4.show()
			self.shadow4.setText("[colour='FF000000']" + self.shadow_messages)
			self.shadow4.setProperty("UnifiedSize", "{{0," + self.window.getProperty("HorzExtent") + "},{0," + self.window.getProperty("VertExtent") + "}}")

	def move(self, x, y):
		self.window.setPosition(PyCEGUI.UVector2(PyCEGUI.UDim(0,x+10), PyCEGUI.UDim(0,y+20)))
		self.shadow.setPosition(PyCEGUI.UVector2(PyCEGUI.UDim(0,x+11), PyCEGUI.UDim(0,y+20)))
		self.shadow2.setPosition(PyCEGUI.UVector2(PyCEGUI.UDim(0,x+9), PyCEGUI.UDim(0,y+20)))
		self.shadow3.setPosition(PyCEGUI.UVector2(PyCEGUI.UDim(0,x+10), PyCEGUI.UDim(0,y+21)))
		self.shadow4.setPosition(PyCEGUI.UVector2(PyCEGUI.UDim(0,x+10), PyCEGUI.UDim(0,y+19)))

