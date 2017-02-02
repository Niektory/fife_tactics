#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

import PyCEGUI

def closeWindow(args):
	args.window.hide()

class GUIHelp:
	def __init__(self):
		self.links = []
		self.pages = dict()
		self.pages["home"] = "This is the help home page. Amazing, isn't it?"
		self.history_back = []
		self.history_forward = []
		self.current_address = "home"
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("Help.layout","Help/")
		self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow, "")
		self.text = self.window.getChild("Help/Content")

		self.back_button = self.window.getChild("Help/BackButton")
		self.back_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "back")
		self.forward_button = self.window.getChild("Help/ForwardButton")
		self.forward_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "forward")
		self.home_button = self.window.getChild("Help/HomeButton")
		self.home_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "home")

	def linkClicked(self, args):
		try:
			address = args.window.getName()[args.window.getName().find("=")+1:]
			self.text.setText(self.pages[address])
			self.window.show()
			self.window.moveToFront()
			if self.current_address != address:
				if self.current_address:
					self.history_back.append(self.current_address)
				self.current_address = address
				self.history_forward = []
			self.updateButtons()
		except:
			print_exc()
			raise

	def home(self, args=None):
		try:
			self.text.setText(self.pages["home"])
			self.window.show()
			self.window.moveToFront()
			if self.current_address != "home":
				if self.current_address:
					self.history_back.append(self.current_address)
				self.current_address = "home"
				self.history_forward = []
			self.updateButtons()
		except:
			print_exc()
			raise

	def updateButtons(self):
		if len(self.history_back) > 0:
			self.back_button.setEnabled(True)
		else:
			self.back_button.setEnabled(False)
		if len(self.history_forward) > 0:
			self.forward_button.setEnabled(True)
		else:
			self.forward_button.setEnabled(False)

	def back(self, args):
		if len(self.history_back) > 0:
			self.history_forward.append(self.current_address)
			self.current_address = self.history_back[-1]
			self.history_back.remove(self.history_back[-1])
			self.text.setText(self.pages[self.current_address])
		self.updateButtons()

	def forward(self, args):
		if len(self.history_forward) > 0:
			self.history_back.append(self.current_address)
			self.current_address = self.history_forward[-1]
			self.history_forward.remove(self.history_forward[-1])
			self.text.setText(self.pages[self.current_address])
		self.updateButtons()

	def createPage(self, content):
		self.pages[str(len(self.pages) + 1)] = content
		return str(len(self.pages))

