#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Tomasz "Niektóry" Turowski

from fife import fife

class TacticsMouseListener(fife.IMouseListener):
	def __init__(self, application):
		self.application = application
		fife.IMouseListener.__init__(self)
		self.middle_click_point = None
		
	def mousePressed(self, event):
		clickpoint = fife.ScreenPoint(event.getX(), event.getY())
		
		if (event.getButton() == fife.MouseEvent.MIDDLE):
			self.middle_click_point = clickpoint
			self.application.camera.detach()
			
		if (event.getButton() == fife.MouseEvent.RIGHT):
			instances = self.application.view.getInstancesAt(clickpoint)
			if instances:
				if instances[0].getObject().getId() == 'tile':
					self.application.gui.new_character.addCharacter(self.application.world.visual.findTile(instances[0]))
				
		if (event.getButton() == fife.MouseEvent.LEFT):
			instances = self.application.view.getInstancesAt(clickpoint)
			if instances:
				if not self.application.selected_action:
					if self.application.current_character and instances[0].getObject().getId() == 'tile':
						tile = self.application.world.visual.findTile(instances[0])
						if tile.movement_cost <= self.application.current_character.cur_AP and tile.movement_cost > 0:
							# walk current character to clicked tile
							self.application.battle_controller.run(tile)
							
				if self.application.selected_action:
				# execute selected combat action
					if instances[0].getObject().getId() in ["boy", "tile", "mushroom"]:
						target = self.application.world.visual.findObject(instances[0])
						if self.application.world.isValidTarget(self.application.current_character, target, self.application.selected_action.targeting_rules):
							self.application.battle_controller.executeAction(self.application.selected_action, target)
				
	def mouseReleased(self, event):
		if (event.getButton() == fife.MouseEvent.MIDDLE):
			self.middle_click_point = None
			self.application.view.snapRotation()

	def mouseMoved(self, event):
		pass
		
	def mouseEntered(self, event):
		pass
		
	def mouseExited(self, event):
		pass
		
	def mouseClicked(self, event):
		pass
		
	def mouseWheelMovedUp(self, event):
		self.application.view.zoomIn()
		
	def mouseWheelMovedDown(self, event):
		self.application.view.zoomOut()
		
	def mouseDragged(self, event):
		if self.middle_click_point:
			if event.isControlPressed():
				self.application.view.fineRotate((event.getX() - self.middle_click_point.x) / 2)
			else:
				self.application.view.moveCamera((self.middle_click_point.x - event.getX()) / 40.0, (self.middle_click_point.y - event.getY()) / 40.0)
			self.middle_click_point = fife.ScreenPoint(event.getX(), event.getY())

class TacticsKeyListener(fife.IKeyListener):
	def __init__(self, application):
		self.application = application
		fife.IKeyListener.__init__(self)
		self.alt_pressed = False

	def getHotkey(self, hotkey_name):
		if self.application.settings.get("hotkeys", hotkey_name):
			return int(self.application.settings.get("hotkeys", hotkey_name))
		else:
			return None
		
	def keyPressed(self, event):
		key_val = event.getKey().getValue()

		if key_val == self.getHotkey("End Turn"):
			self.application.endTurn(0)
		elif key_val == self.getHotkey("Character Info"):
			for character in self.application.world.characters:
				character.visual.displayStats()
		elif key_val == self.getHotkey("Movement Costs"):
			for tile in self.application.world.tiles:
				if tile.movement_cost > 0:
					self.application.gui.sayBubble(tile.visual.instance, str(tile.movement_cost))

		elif key_val == self.getHotkey("Zoom In"):
			self.application.view.zoomIn()
		elif key_val == self.getHotkey("Zoom Out"):
			self.application.view.zoomOut()
		elif key_val == self.getHotkey("Rotate Clockwise"):
			self.application.view.rotateClockwise()
		elif key_val == self.getHotkey("Rotate Counterclockwise"):
			self.application.view.rotateCounterclockwise()
		elif key_val == self.getHotkey("Raise Terrain"):
			self.application.view.increaseElevation()
		elif key_val == self.getHotkey("Flatten Terrain"):
			self.application.view.decreaseElevation()
		elif key_val == self.getHotkey("Pan Up"):
			self.application.view.camera_move_key_up = True
		elif key_val == self.getHotkey("Pan Down"):
			self.application.view.camera_move_key_down = True
		elif key_val == self.getHotkey("Pan Left"):
			self.application.view.camera_move_key_left = True
		elif key_val == self.getHotkey("Pan Right"):
			self.application.view.camera_move_key_right = True

		elif key_val == self.getHotkey("Quick Save"):
			self.application.saveGame("quick")
		elif key_val == self.getHotkey("Quick Load"):
			self.application.loadGame("quick")

		elif key_val == self.getHotkey("Start Recording"):
			self.application.battle_controller.startRecording()
		elif key_val == self.getHotkey("Stop Recording"):
			self.application.battle_controller.stopRecording()
		elif key_val == self.getHotkey("Replay"):
			self.application.startReplay()
		elif key_val == self.getHotkey("AI Move"):
			self.application.AIMove()
		elif key_val == self.getHotkey("AI Play"):
			self.application.startAIPlay()

		elif key_val == fife.Key.F1:
			self.application.gui.help.home()
		elif key_val == fife.Key.ESCAPE:
			self.application.gui.game_menu.show()
					
		elif self.application.current_character:
			if self.application.selected_action and (key_val == self.getHotkey("Walk")):
				self.application.selected_action = None
			else:
				for action in self.application.combat_actions.actions:
					if (key_val == self.getHotkey(action.name)) and self.application.current_character.hasAction(action.name):
						self.application.selectAction(action.name)

	def keyReleased(self, event):
		key_val = event.getKey().getValue()
		if key_val == fife.Key.UP:
			self.application.view.camera_move_key_up = False
		elif key_val == fife.Key.DOWN:
			self.application.view.camera_move_key_down = False
		elif key_val == fife.Key.LEFT:
			self.application.view.camera_move_key_left = False
		elif key_val == fife.Key.RIGHT:
			self.application.view.camera_move_key_right = False

