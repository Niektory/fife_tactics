#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

from battlecommand import BattleCommand
from replay import Replay

class BattleController(object):
	"""Handles battle commands issued by the player, AI, or a script. Can also record them to a replay file for later playback."""
	def __init__(self, application, world):
		self.application = application
		self.world = world
		self.recording = False

	def startRecording(self):
		self.recording = True
		self.replay = Replay()
		self.replay.saveWorld(self.world)

	def stopRecording(self):
		if self.recording:
			self.recording = False
			self.replay.saveCommands()
			
	def executeCommand(self, command):
		if command.command == "run":
			self.run(self.world.findObjectByID(command.target))
		elif command.command == "executeAction":
			self.executeAction(command.action, self.world.findObjectByID(command.target))
		elif command.command == "endTurn":
			self.endTurn()

	def run(self, dest_tile):
		"""Move the character to the target tile, checking for interrupts and triggers."""
		if self.recording:
			self.replay.addCommand(BattleCommand("run", dest_tile.ID))
		threat = self.world.getThreateningCharacter(self.world.current_character_turn.tile)
		if threat:
			threat.opportunityAttack(self.world.current_character_turn)
		else:
			route = self.application.pather.planMove(self.world.current_character_turn, dest_tile)
			#print "---"
			#for node in route.path:
			#	print node.coords
			self.world.current_character_turn.run(route)
			if not self.world.visual and self.world.current_character_turn:
				self.world.createMovementGrid(self.world.current_character_turn)

	def executeAction(self, action, target):
		if action.AP_cost > self.world.current_character_turn.cur_AP:
			return
		if self.recording:
			self.replay.addCommand(BattleCommand("executeAction", target.ID, action))
		#print "Action score:", self.application.ai.scoreAction(action, target)
		self.application.gui.combat_log.printMessage(self.world.current_character_turn.name + " used " + action.name + " on " + target.name + ".")
		action(self.application).execute(self.world.current_character_turn, target, self.world.getTargetsInArea(self.world.current_character_turn, target, action.targeting_rules))
		if not self.world.visual and self.world.current_character_turn:
			self.world.createMovementGrid(self.world.current_character_turn)

	def endTurn(self):
		if self.recording:
			self.replay.addCommand(BattleCommand("endTurn"))
		self.world.current_character_turn.endTurn()

