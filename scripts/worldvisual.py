#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

from fife import fife
from math import floor, ceil, atan, sqrt, tan, cos
from operator import attrgetter, methodcaller

import gridhelper
from tile import TacticsTile, TileVisual
from timeline import TacticsTimeline, TacticsTimer
from character import TacticsCharacter
from charactervisual import CharacterVisual
from effects import VisualLOS
from surface import SurfaceTar, SurfaceIce, TarVisual, IceVisual
from obstacle import Obstacle, ObstacleVisual
from trap import Trap, TrapVisual
from wall import Wall

class WorldVisual(object):
	"""Contains the visual representation of the world."""
	def initFromMap(self, application, maplayer, world):
		"""Initialize the world + visual from the fife map layer."""
		print "* Initializing movement grid..."
		self.application = application
		self.maplayer = maplayer
		self.world = world

		print "  * Creating wall cache..."
		# create a dictionary that maps coordinates to walls
		for instance in self.maplayer.getInstances():
			coords = instance.getLocation().getLayerCoordinates()
			z_size = gridhelper.getObjectZSize(instance.getObject().getId())
			new_wall = Wall(instance.getLocation().getLayerCoordinates(), z_size, instance.getObject().getId())
			new_wall.createVisual(self.application, instance)
			self.world.walls.append(new_wall)
			if z_size > 0:
				for z_offset in xrange(z_size):
					self.world.wall_map[(coords.x, coords.y, coords.z + z_offset)] = new_wall
			elif z_size < 0:
				for z_offset in xrange(0 - z_size):
					self.world.wall_map[(coords.x, coords.y, coords.z - z_offset - 1)] = new_wall

		print "  * Creating walkable tiles..."
		# add tiles
		for instance in self.maplayer.getInstances():
			if instance.getObject().getId() in ["block_gray", "water", "block_grass"]:
				tile = self.world.addTile(instance.getLocation().getLayerCoordinates(), instance.getObject().getId())
				if tile:
					tile.createVisual(self.application)
		# add tiles that should be inaccessible to the to_remove list
		to_remove = []
		for tile in self.world.tiles:
			column = self.world.getTilesByLocation(tile.coords)
			last_z = 50
			for column_tile in column:
				if column_tile.coords.z + 4 >= last_z:
					to_remove.append(column_tile)
				last_z = column_tile.coords.z
		# remove tiles in the to_remove list
		for tile in to_remove:
			self.world.removeTile(tile)

	def initFromWorld(self, application, maplayer, world):
		"""Create fife instances of all objects. Used after loading the world state."""
		self.application = application
		self.maplayer = maplayer
		self.world = world
		# create wall instances
		for wall in self.world.walls:
			wall.createVisual(self.application)
		# create tile instances
		for tile in self.world.tiles:
			tile.createVisual(self.application)
			# create trap instances
			for trap in tile.traps:
				trap.createVisual()
			# create surface instances
			for surface in tile.surface_effects:
				surface.createVisual()
		# create character instances and listeners
		for	character in self.world.characters:
			character.createVisual()
		# create obstacle instances
		for obstacle in self.world.obstacles:
			obstacle.createVisual()

	def findTile(self, instance):
		"""Return the tile object that corresponds the given instance."""
		for tile in self.world.tiles:
			if instance.getFifeId() == tile.visual.instance.getFifeId():
				return tile

	def findCharacter(self, instance):
		"""Return the character object represented by instance."""
		for character in self.world.characters:
			if instance.getFifeId() == character.visual.instance.getFifeId():
				return character
	
	def findObstacle(self, instance):
		"""Return the obstacle object represented by instance."""
		for obstacle in self.world.obstacles:
			if instance.getFifeId() == obstacle.visual.instance.getFifeId():
				return obstacle

	def findObject(self, instance):
		"""Return the object (tile, character or instance) represented by instance."""
		obj = self.findCharacter(instance)
		if obj:
			return obj
		obj = self.findObstacle(instance)
		if obj:
			return obj
		obj = self.findTile(instance)
		if obj:
			return obj


