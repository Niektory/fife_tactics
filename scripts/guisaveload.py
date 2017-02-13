# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI
from os import listdir
from traceback import print_exc

def closeWindow(args):
	args.window.hide()

class GUISaveLoad:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("SaveLoad.layout","SaveLoad/")
		self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow, "")
		self.file_list = PyCEGUI.WindowManager.getSingleton().getWindow("SaveLoad/Files")
		self.file_list.subscribeEvent(PyCEGUI.Listbox.EventSelectionChanged, self, "fillEditBox")
		self.file_items = []
		for file_name in listdir("saves"):
			if file_name.endswith(".sav"):
				self.addSaveToList(file_name[:-4])
		self.save_button = self.window.getChild("SaveLoad/SaveButton")
		self.save_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "save")
		self.load_button = self.window.getChild("SaveLoad/LoadButton")
		self.load_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "load")
		self.name_edit = self.window.getChild("SaveLoad/NameEdit")
		self.name_edit.subscribeEvent(PyCEGUI.Editbox.EventTextChanged, self, "selectItem")
		self.ignore_selecting = False

	def show(self, args=None):
		self.window.show()
		self.window.moveToFront()
		if self.application.map:
			self.save_button.show()
		else:
			self.save_button.hide()

	def save(self, args):
		try:
			item = self.file_list.getFirstSelectedItem()
			if item:
				self.application.saveGame(item.getText())
			elif len(self.name_edit.getText()) > 0:
				self.application.saveGame(self.name_edit.getText())
				self.addSaveToList(self.name_edit.getText())
			self.window.hide()
		except:
			print_exc()
			raise

	def load(self, args):
		try:
			item = self.file_list.getFirstSelectedItem()
			if item:
				self.application.loadGame(item.getText())
		except:
			print_exc()
			raise

	def selectItem(self, args):
		try:
			self.ignore_selecting = True
			item = self.file_list.findItemWithText(self.name_edit.getText(), None)
			if item:
				self.file_list.setItemSelectState(item, True)
			elif self.file_list.getFirstSelectedItem():
				self.file_list.clearAllSelections()
			self.ignore_selecting = False
		except:
			print_exc()
			raise

	def fillEditBox(self, args):
		try:
			if not self.ignore_selecting:
				item = self.file_list.getFirstSelectedItem()
				if item:
					self.name_edit.setText(item.getText())
				else:
					self.name_edit.setText("")
		except:
			print_exc()
			raise

	def addSaveToList(self, save_name):
		self.file_items.append(PyCEGUI.ListboxTextItem(save_name))
		self.file_items[-1].setAutoDeleted(False)
		self.file_items[-1].setSelectionBrushImage("TaharezLook", "MultiListSelectionBrush")
		self.file_list.addItem(self.file_items[-1])

