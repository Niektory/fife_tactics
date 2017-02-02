#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

import PyCEGUI
from traceback import print_exc

def closeWindow(args):
	args.window.hide()

class GUIMainMenu:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("MainMenu.layout","MainMenu/")

		self.new_game_button = PyCEGUI.WindowManager.getSingleton().getWindow("MainMenu/NewGameButton")
		self.new_game_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "newGame")
		self.preferences_button = PyCEGUI.WindowManager.getSingleton().getWindow("MainMenu/PreferencesButton")
		self.preferences_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.gui.preferences, "show")
		self.load_button = PyCEGUI.WindowManager.getSingleton().getWindow("MainMenu/LoadButton")
		self.load_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.gui.save_load, "show")
		self.quit_game_button = PyCEGUI.WindowManager.getSingleton().getWindow("MainMenu/QuitGameButton")
		self.quit_game_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "quitGame")

	def show(self):
		self.window.show()
		self.window.moveToFront()

	def newGame(self, args):
		try:
			self.application.newGame()
		except:
			print_exc()
			raise

	def quitGame(self, args):
		try:
			self.application.quit()
		except:
			print_exc()
			raise

class GUIGameMenu:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("GameMenu.layout","GameMenu/")
		self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow, "")

		self.help_button = self.window.getChild("GameMenu/HelpButton")
		self.help_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "help")
		self.preferences_button = self.window.getChild("GameMenu/PreferencesButton")
		self.preferences_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "preferences")
		self.save_load_button = self.window.getChild("GameMenu/SaveLoadButton")
		self.save_load_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "saveLoad")
		self.main_menu_button = self.window.getChild("GameMenu/MainMenuButton")
		self.main_menu_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "mainMenu")

	def show(self):
		self.window.show()
		self.window.moveToFront()

	def help(self, args):
		try:

			self.gui.help.home()
			self.window.hide()
		except:
			print_exc()
			raise

	def saveLoad(self, args):
		try:
			self.gui.save_load.show()
			self.window.hide()
		except:
			print_exc()
			raise

	def preferences(self, args):
		try:
			self.gui.preferences.show()
			self.window.hide()
		except:
			print_exc()
			raise

	def mainMenu(self, args):
		try:
			self.application.unloadMap()
			self.gui.showMainMenu()
		except:
			print_exc()
			raise


