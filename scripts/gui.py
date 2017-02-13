# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI
from fife import fife

from bubble import SayBubble
from guipreferences import GUIPreferences
from guinewcharacter import GUINewCharacter
from guihelp import GUIHelp
from guisaveload import GUISaveLoad
from guiactionmenu import GUIActionMenu
from guimainmenu import GUIMainMenu, GUIGameMenu
from guitooltip import GUITooltip
from guicombatlog import GUICombatLog
from guitimeline import GUITimeline
from guiaistatus import GUIAIStatus

class TacticsGUI:
	def __init__(self, application):
		print "* Loading GUI..."
		self.application = application
		self.bubbles = []

		# create the root window
		PyCEGUI.SchemeManager.getSingleton().create("TaharezLook.scheme")
		self.root = PyCEGUI.WindowManager.getSingleton().createWindow("DefaultWindow", "_MasterRoot")
		self.root.setProperty("MousePassThroughEnabled", "True")
		PyCEGUI.System.getSingleton().setGUISheet(self.root)

		# load windows from layout files and attach them to the root
		self.save_load = GUISaveLoad(self.application)
		self.root.addChildWindow(self.save_load.window)
		self.help = GUIHelp()
		self.root.addChildWindow(self.help.window)
		self.combat_log = GUICombatLog(self.help)
		self.root.addChildWindow(self.combat_log.window)
		self.action_menu = GUIActionMenu(self.application)
		self.root.addChildWindow(self.action_menu.window)
		self.timeline = GUITimeline(self.application)
		self.root.addChildWindow(self.timeline.window)
		self.new_character = GUINewCharacter(self.application)
		self.root.addChildWindow(self.new_character.window)
		self.preferences = GUIPreferences(self.application)
		self.root.addChildWindow(self.preferences.window)
		self.game_menu = GUIGameMenu(self.application, self)
		self.root.addChildWindow(self.game_menu.window)
		self.main_menu = GUIMainMenu(self.application, self)
		self.root.addChildWindow(self.main_menu.window)
		self.tooltip = GUITooltip()
		self.root.addChildWindow(self.tooltip.shadow)
		self.root.addChildWindow(self.tooltip.shadow2)
		self.root.addChildWindow(self.tooltip.shadow3)
		self.root.addChildWindow(self.tooltip.shadow4)
		self.root.addChildWindow(self.tooltip.window)
		self.ai_status = GUIAIStatus()
		self.root.addChildWindow(self.ai_status.window)
		print "* GUI loaded!"

	def pump(self):
		self.timeline.update()
		self.tooltip.clear()
		self.action_menu.updateTextBox()
		self.action_menu.updateButtons()

	def sayBubble(self, instance, text, time = 2000):
		#for bubble in self.bubbles:
		#	if instance == bubble.instance:
		#		bubble.destroy()
		#		break
		#self.bubbles.append(SayBubble(self.application, instance, text, time))
		instance.say(text, time)

	def showHUD(self):
		self.main_menu.window.hide()
		self.combat_log.window.show()
		self.action_menu.window.show()
		self.timeline.window.show()
		self.save_load.window.hide()
		self.new_character.window.hide()
		self.preferences.window.hide()
		self.game_menu.window.hide()
		self.help.window.hide()
		self.combat_log.clear()
		self.combat_log.printMessage("Game loaded. Press F1 of click " + self.combat_log.createLink("<here>", "home") + " for help.")

	def showMainMenu(self):
		self.main_menu.show()
		self.save_load.window.hide()
		self.combat_log.window.hide()
		self.action_menu.window.hide()
		self.timeline.window.hide()
		self.new_character.window.hide()
		self.preferences.window.hide()
		self.game_menu.window.hide()
		self.help.window.hide()
		self.tooltip.window.hide()
		self.tooltip.shadow.hide()
		self.tooltip.shadow2.hide()
		self.tooltip.shadow3.hide()
		self.tooltip.shadow4.hide()
