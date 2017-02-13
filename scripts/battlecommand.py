# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

class BattleCommand(object):
	"""
	Holds a single battle command for BattleController. Possible commands:
	"run": requires target tile ID
	"executeAction": requires an action class and target ID
	"endTurn": no parameters required
	"""
	def __init__(self, command, target = None, action = None):
		self.command = command
		self.target = target
		self.action = action
