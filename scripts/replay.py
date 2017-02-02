#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

import serializer

class Replay(object):
	"""Holds a recorded sequence of commands."""
	def __init__(self):
		self.commands = []
		self.current_command = 0

	def addCommand(self, command):
		self.commands.append(command)

	def getCommand(self):
		if len(self.commands) > self.current_command:
			self.current_command += 1
			return self.commands[self.current_command - 1]
		else:
			return None

	def saveWorld(self, world):
		serializer.save(world, "saves/replaystart.sav")

	def loadWorld(self):
		return serializer.load("saves/replaystart.sav")

	def saveCommands(self):
		serializer.save(self.commands, "saves/replaycommands.replay")

	def loadCommands(self):
		self.commands = serializer.load("saves/replaycommands.replay")
		self.current_command = 0

