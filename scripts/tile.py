# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

class TacticsTile(object):
	"""Represents a walkable tile."""
	def __init__(self, coords, surface):
		self.coords = coords
		self.movement_cost = 0
		self.searched = False
		self.previous = None
		self.blocker = False
		self.visitors = []
		self.traps = []
		self.neighbor_cache = []
		self.los_cache = []
		self.trajectory_cache = []
		self.surface_base = surface
		self.surface_effects = []
		self.visual = None

	@property
	def tile(self):
		return self

	@property
	def name(self):
		return self.getSurface()

	def getSurface(self):
		if len(self.surface_effects) > 0:
			return self.surface_effects[-1].name
		else:
			return self.surface_base

	def getZ(self):
		"""Return the Z coordinate of the tile. A helper function for sorting."""
		return self.coords.z

	def createVisual(self, application):
		self.visual = TileVisual(application, self)


class TileVisual(object):
	def __init__(self, application, tile):
		self.application = application
		self.tile = tile
		self.instance = self.application.maplayer.createInstance(self.application.model.getObject("tile", "tactics"), self.tile.coords)
		self.instance.setCellStackPosition(115)
		fife.InstanceVisual.create(self.instance).setStackPosition(115)
		self.instance.actRepeat("transparent")
		
	def destroy(self):
		self.application.maplayer.deleteInstance(self.instance)
