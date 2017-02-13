# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI

from error import LogExceptionDecorator

@LogExceptionDecorator
def propagateMouseWheel(args):
	args.window.getParent().fireEvent(PyCEGUI.Window.EventMouseWheel, args)

class GUICombatLog:
	def __init__(self, help):
		self.links = []
		self.help = help
		self.messages = ""
		self.last_message = ""
		self.duplicate_count = 1
		self.length_before_last = 0
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("CombatLog.layout","CombatLog/")
		self.output = self.window.getChild("CombatLog/TextBox")

	def clear(self):
		# scroll the log to the beginning (workaround)
		args = PyCEGUI.MouseEventArgs(self.output)
		args.wheelChange = 1000
		self.output.fireEvent(PyCEGUI.GUISheet.EventMouseWheel, args)

		self.messages = ""
		self.last_message = ""
		self.duplicate_count = 1
		self.length_before_last = 0
		self.output.setText("")
		for link in self.links:
			self.output.removeChildWindow(link)

	def printMessage(self, message):
		if message == self.last_message:
			self.duplicate_count += 1
			self.messages = self.messages[:self.length_before_last] + "- " + message + " (x" + str(self.duplicate_count) + ")\n"
		else:
			self.length_before_last = len(self.messages)
			self.messages += ("- " + message + "\n")
			self.duplicate_count = 1
		self.output.setText(self.messages)
		self.last_message = message
		# scroll the log to the end (workaround)
		args = PyCEGUI.MouseEventArgs(self.output)
		args.wheelChange = -1000
		self.output.fireEvent(PyCEGUI.GUISheet.EventMouseWheel, args)

	def createLink(self, message, address):
		new_link = PyCEGUI.WindowManager.getSingleton().createWindow("TaharezLook/StaticText", "Link/" + str(len(self.links) + 1) + "=" + address)
		new_link.setProperty("Text", "[colour='FF00A0FF']" + message)
		new_link.setProperty("FrameEnabled", "False")
		new_link.setProperty("UnifiedSize", "{{0," + new_link.getProperty("HorzExtent") + "},{0," + new_link.getProperty("VertExtent") + "}}")
		self.output.addChildWindow(new_link)
		#self.output.setText(self.messages)
		new_link.subscribeEvent(PyCEGUI.Window.EventMouseClick, self.help, "linkClicked")
		new_link.subscribeEvent(PyCEGUI.Window.EventMouseWheel, propagateMouseWheel, "")
		self.links.append(new_link)
		return "[window='Link/" + str(len(self.links)) + "=" + address + "']"

