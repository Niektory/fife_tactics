# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI

from error import LogExceptionDecorator

@LogExceptionDecorator
def closeWindow(args):
	args.window.hide()

class GUIMainMenu:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("MainMenu.layout")

		self.new_game_button = self.window.getChild("MainMenu/NewGameButton")
		self.new_game_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.newGame)
		self.preferences_button = self.window.getChild("MainMenu/PreferencesButton")
		self.preferences_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.preferences.show)
		self.load_button = self.window.getChild("MainMenu/LoadButton")
		self.load_button.subscribeEvent(
					PyCEGUI.PushButton.EventClicked, self.gui.save_load.show)
		self.quit_game_button = self.window.getChild("MainMenu/QuitGameButton")
		self.quit_game_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.quitGame)

	def show(self):
		self.window.show()
		self.window.moveToFront()

	@LogExceptionDecorator
	def newGame(self, args):
		self.application.newGame()

	@LogExceptionDecorator
	def quitGame(self, args):
		self.application.quit()


class GUIGameMenu:
	def __init__(self, application, gui):
		self.application = application
		self.gui = gui
		self.window = PyCEGUI.WindowManager.getSingleton().loadLayoutFromFile("GameMenu.layout")
		self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow)

		self.help_button = self.window.getChild("HelpButton")
		self.help_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.help)
		self.preferences_button = self.window.getChild("PreferencesButton")
		self.preferences_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.preferences)
		self.save_load_button = self.window.getChild("SaveLoadButton")
		self.save_load_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.saveLoad)
		self.main_menu_button = self.window.getChild("MainMenuButton")
		self.main_menu_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.mainMenu)

	def show(self):
		self.window.show()
		self.window.moveToFront()

	@LogExceptionDecorator
	def help(self, args):
		self.gui.help.home()
		self.window.hide()

	@LogExceptionDecorator
	def saveLoad(self, args):
		self.gui.save_load.show()
		self.window.hide()

	@LogExceptionDecorator
	def preferences(self, args):
		self.gui.preferences.show()
		self.window.hide()

	@LogExceptionDecorator
	def mainMenu(self, args):
		self.application.unloadMap()
		self.gui.showMainMenu()
