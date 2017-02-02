#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

from fife import fife

class Wall(object):
	"""Represents a single wall block, can have various height. Instance is optional."""
	def __init__(self, coords, height, wall_type):
		self.visual = None
		self.type = wall_type
		self.coords = coords
		self.height = height

	def createVisual(self, application, instance = None):
		self.visual = WallVisual(application, self, instance)

class WallVisual(object):
	def __init__(self, application, wall, instance):
		self.application = application
		self.wall = wall
		if instance:
			self.instance = instance
		else:
			self.instance = self.application.maplayer.createInstance(self.application.model.getObject(self.wall.type, "tactics"), self.wall.coords)
			if wall.type[:5] == "block":
				self.instance.setCellStackPosition(0)
				fife.InstanceVisual.create(self.instance).setStackPosition(0)
			elif wall.type == "water":
				self.instance.setCellStackPosition(110)
				fife.InstanceVisual.create(self.instance).setStackPosition(110)

