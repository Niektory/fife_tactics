# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import PyCEGUI

def closeWindow(args):
	args.window.hide()

class GUINewCharacter:
	def __init__(self, application):
		self.application = application
		self.window = PyCEGUI.WindowManager.getSingleton().loadWindowLayout("NewCharacter.layout","NewCharacter/")
		self.window.subscribeEvent(PyCEGUI.FrameWindow.EventCloseClicked, closeWindow, "")

		self.OK_button = self.window.getChild("NewCharacter/OKButton")
		self.OK_button.subscribeEvent(PyCEGUI.PushButton.EventClicked, self, "modifyCharacter")

		self.action_checkboxes = []
		vert_pos = 143
		for action in self.application.combat_actions.actions:
			new_checkbox = PyCEGUI.WindowManager.getSingleton().createWindow("TaharezLook/Checkbox", "ActionCheckbox/" + action.name)
			new_checkbox.setProperty("Text", action.name)
			new_checkbox.setProperty("UnifiedSize", "{{0,180},{0,20}}")
			new_checkbox.setProperty("UnifiedPosition", "{{0,70},{0," + str(vert_pos) + "}}")
			new_checkbox.setSelected(True)
			self.window.addChildWindow(new_checkbox)
			self.action_checkboxes.append(new_checkbox)
			vert_pos += 20

	def addCharacter(self, tile):
		self.new_character_tile = tile
		self.window.getChild("NewCharacter/NameEdit").setText("")
		self.window.show()
		self.window.moveToFront()

	def modifyCharacter(self, args):
		try:
			character = self.application.world.addCharacterAt(self.new_character_tile, self.window.getChild("NewCharacter/NameEdit").getText())
			character.team = int(self.window.getChild("NewCharacter/TeamEdit").getText())
			character.max_AP = int(self.window.getChild("NewCharacter/APEdit").getText())
			character.max_HP = character.cur_HP = int(self.window.getChild("NewCharacter/HPEdit").getText())
			for checkbox in self.action_checkboxes:
				if checkbox.isSelected():
					character.addAction(self.application.combat_actions.getAction(checkbox.getName()[15:]))
			self.window.hide()
		except:
			print_exc()
			raise

