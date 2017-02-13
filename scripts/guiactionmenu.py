# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI

from error import LogExceptionDecorator

class GUIActionMenu:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("ActionMenu.layout","ActionMenu/")
		self.text_box = self.window.getChild("ActionMenu/TextBox")
		self.action_button_list = self.window.getChild("ActionMenu/ButtonList")

		self.walk_button = self.window.getChild("ActionMenu/WalkButton")
		self.walk_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "walk")
		self.end_turn_button = self.window.getChild("ActionMenu/EndTurnButton")
		self.end_turn_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self.application, "endTurn")

		self.action_buttons = []
		for action in self.application.combat_actions.actions:
			new_button = PyCEGUI.WindowManager.getSingleton().createWindow("TaharezLook/Button", "ActionButton/" + action.name)
			new_button.setProperty("Text", action.name)
			new_button.setProperty("UnifiedSize", "{{1,-10},{0,25}}")
			self.action_button_list.addChildWindow(new_button)
			new_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "combatAction")
			new_button.hide()
			self.action_buttons.append(new_button)

	def updateTextBox(self):
		"""Display HP and AP on the action menu text box."""
		self.text_box.resetList()
		self.messages = []
		if self.application.current_character:
			self.messages.append(PyCEGUI.ListboxTextItem(str(self.application.current_character.cur_AP) + " AP"))
			self.messages.append(PyCEGUI.ListboxTextItem(str(self.application.current_character.cur_HP) + " HP"))
			self.messages[-2].setAutoDeleted(False)
			self.messages[-1].setAutoDeleted(False)
			self.text_box.addItem(self.messages[-2])
			self.text_box.addItem(self.messages[-1])

	def updateButtons(self):
		# color the action menu buttons
		self.walk_button.setProperty("NormalTextColour", "FFFFFFFF")
		self.walk_button.setProperty("HoverTextColour", "FFFFFFFF")
		for button in self.action_buttons:
			button.setProperty("NormalTextColour", "FFFFFFFF")
			button.setProperty("HoverTextColour", "FFFFFFFF")
		if self.application.current_character and not self.application.selected_action:
			self.walk_button.setProperty("NormalTextColour", "FFFFD000")
			self.walk_button.setProperty("HoverTextColour", "FFFFD000")
		elif self.application.selected_action:
			for button in self.action_buttons:
				if self.application.selected_action.name == button.getName()[13:]:
					button.setProperty("NormalTextColour", "FFFFD000")
					button.setProperty("HoverTextColour", "FFFFD000")
		# show/hide the action menu buttons
		if self.application.current_character:
			self.walk_button.show()
			for button in self.action_buttons:
				if self.application.current_character.hasAction(button.getName()[13:]):
					button.show()
					button.setProperty("UnifiedSize", "{{1,-10},{0,25}}")
				else:
					button.hide()
					button.setProperty("UnifiedSize", "{{0,0},{0,0}}")
		else:
			self.walk_button.hide()
			for button in self.action_buttons:
					button.hide()
					button.setProperty("UnifiedSize", "{{0,0},{0,0}}")

	@LogExceptionDecorator
	def walk(self, args):
		self.application.selected_action = None

	@LogExceptionDecorator
	def combatAction(self, args):
		self.application.selectAction(args.window.getName()[13:])
