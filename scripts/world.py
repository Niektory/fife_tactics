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
from actions import TrajectoryArc

class World(object):
	"""Holds the complete world and battle state, and methods for updating and reading it."""
	def __init__(self, application, maplayer):
		"""Create an empty world."""
		self.application = application
		self.maplayer = maplayer

		self.walls = []	# list of all walls
		self.wall_map = dict()	# dictionary that maps coordinates to walls
		self.tiles = []	# list of all tiles
		self.tile_columns = dict()	# list of tile columns; a column being a list of tiles sorted in reverse Z order; should be updated together with self.tiles
		self.characters = []	# list of all characters
		self.obstacles = []	# list of all obstacles
		self.current_character_turn = None	# character whose turn it is now
		self.timeline = TacticsTimeline()	# queue of events scheduled to happen after the current turn
		self.object_counter = 0	# increases when creating objects; used to assign object IDs

	def assignID(self, obj):
		obj.ID = self.object_counter
		self.object_counter += 1

	def findObjectByID(self, ID):
		for character in self.characters:
			if character.ID == ID:
				return character
		for obstacle in self.obstacles:
			if obstacle.ID == ID:
				return obstacle
		for tile in self.tiles:
			if tile.ID == ID:
				return tile

	def updateNeighborCache(self, tile):
		"""Populate neighbor cache of this tile and update nearby tiles to add this tile as a neighbor. Called when adding a tile."""
		tile.neighbor_cache = []
		neighbor_columns = self.getNearbyColumns(tile.coords)
		for neighbor_column in neighbor_columns:
			for neighbor in neighbor_column:
				if self.movementCost(tile, neighbor) < 100:
					tile.neighbor_cache.append(neighbor)
				if self.movementCost(neighbor, tile) < 100:
					neighbor.neighbor_cache.append(tile)
		for tile2 in self.tiles:
			if self.testLOS(tile.coords, tile2.coords):
				tile.los_cache.append(tile2)
				tile2.los_cache.append(tile)
			if self.testTrajectory(tile.coords, tile2.coords, TrajectoryArc(5)):
				tile.trajectory_cache.append(tile2)
			if self.testTrajectory(tile2.coords, tile.coords, TrajectoryArc(5)):
				tile2.trajectory_cache.append(tile)

	def removeFromNeighborCache(self, tile):
		"""Remove this tile from neighbor caches of nearby tiles. Called when deleting a tile."""
		neighbor_columns = self.getNearbyColumns(tile.coords)
		for neighbor_column in neighbor_columns:
			for neighbor in neighbor_column:
				if neighbor.neighbor_cache.count(tile) > 0:
					neighbor.neighbor_cache.remove(tile)
		for tile2 in self.tiles:
			if tile2.los_cache.count(tile) > 0:
				tile2.los_cache.remove(tile)
			if tile2.neighbor_cache.count(tile) > 0:
				tile2.neighbor_cache.remove(tile)

	def getNearbyColumns(self, coords):
		"""Return a list of tile columns in the radius of 2 tiles from location. Used by the neighbor cache update methods."""
		neighbor_columns = []
		# distance 1
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x+1, coords.y, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x-1, coords.y, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x, coords.y+1, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x, coords.y-1, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x+1, coords.y-1, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x-1, coords.y+1, coords.z)))
		# distance 2, straight
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x+2, coords.y, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x-2, coords.y, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x, coords.y+2, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x, coords.y-2, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x+2, coords.y-2, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x-2, coords.y+2, coords.z)))
		# distance 2, diagonal
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x+2, coords.y-1, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x-2, coords.y+1, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x-1, coords.y+2, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x+1, coords.y-2, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x+1, coords.y+1, coords.z)))
		neighbor_columns.append(self.getTilesByLocation(fife.ModelCoordinate(coords.x-1, coords.y-1, coords.z)))
		return neighbor_columns

	def addTileToColumn(self, tile):
		"""Add the tile to the appropriate column, creating or sorting the column. Called when adding a tile."""
		if (tile.coords.x,tile.coords.y) in self.tile_columns:
			self.tile_columns[tile.coords.x,tile.coords.y].append(tile)
			self.tile_columns[tile.coords.x,tile.coords.y].sort(key=methodcaller("getZ"), reverse = True)
		else:
			self.tile_columns[tile.coords.x,tile.coords.y] = [tile]

	def removeTileFromColumn(self, tile):
		"""Remove the tile form the appropriate column. Called when removing a tile."""
		if (tile.coords.x,tile.coords.y) in self.tile_columns:
			self.tile_columns[tile.coords.x,tile.coords.y].remove(tile)

	def addTile(self, coords, wall_type):
		"""Create a tile object, add it to the world structures, and return it."""
		# don't create multiple tiles at a single location
		if self.findTileByLocation(coords):
			return
		new_tile = TacticsTile(coords, gridhelper.getObjectSurface(wall_type))
		self.assignID(new_tile)
		# create the tile instance (optional)
		if self.visual:
			new_tile.visual = TileVisual(self.application, new_tile)
		# add the tile to the world structures
		self.tiles.append(new_tile)
		self.addTileToColumn(new_tile)
		self.updateNeighborCache(new_tile)
		return new_tile

	def removeTile(self, tile):
		"""Delete the tile and remove it from the world structures."""
		if self.tiles.count(tile):
			self.removeTileFromColumn(tile)
			self.removeFromNeighborCache(tile)
			self.tiles.remove(tile)
			if tile.visual:
				tile.visual.destroy()

	def getTilesByLocation(self, coords):
		"""Return a tile column (list of tiles) in given xy location sorted by Z decrementally."""
		if (coords.x, coords.y) in self.tile_columns:
			return self.tile_columns[(coords.x, coords.y)]
		else:
			return []

	def findTileByLocation(self, coords):
		"""Return a tile object that occupies a given XYZ location."""
		for tile in self.tiles:
			if coords.x == tile.coords.x and coords.y == tile.coords.y and ((coords.z == tile.coords.z) or (coords.z == (tile.coords.z - 1))):
				return tile

	def createMovementGrid(self, character):
		"""Populate the grid with information about possible moves for the given character, using the Dijkstra algorithm."""
		for tile in self.tiles:
			tile.movement_cost = 99
			tile.searched = False
			tile.previous = None

		character.tile.movement_cost = 0
		unvisited = self.tiles[:]
		while unvisited:
			unvisited.sort(key = attrgetter('movement_cost'))
			current = unvisited.pop(0)
			#if current.movement_cost >= character.cur_AP:
			#	break
			current.searched = True
			
			for neighbor in current.neighbor_cache:
				if (not neighbor.blocker) and (not neighbor.searched):
					cost = self.movementCost(current, neighbor)
					if neighbor.movement_cost > current.movement_cost + cost:
					# don't calculate moves beyond the current AP (no multiturn moves)
					#if (neighbor.movement_cost > current.movement_cost + cost) and (character.cur_AP >= current.movement_cost + cost):
						neighbor.movement_cost = current.movement_cost + cost
						neighbor.previous = current					

	def movementCost(self, cur, dest):
		"""Return the cost of moving from cur tile to dest tile, taking into account surface type. Only single step movement is considered. Returns 100 when movement is not possible."""
		if gridhelper.isDifficultSurface(cur.getSurface()):
			# moving from difficult terrain
			if gridhelper.horizontalDistance(cur.coords, dest.coords) == 1:
				if (cur.coords.z - dest.coords.z) <= 3 and (cur.coords.z - dest.coords.z) >= -1:
					return 2
		else:
			# moving from normal terrain
			if gridhelper.horizontalDistance(cur.coords, dest.coords) == 1:
				if (cur.coords.z - dest.coords.z) <= 3 and (cur.coords.z - dest.coords.z) >= -2:
					return 1
			elif gridhelper.horizontalDistance(cur.coords, dest.coords) == 2:
				if (cur.coords.z - dest.coords.z) <= 3 and (cur.coords.z >= dest.coords.z):
					x1 = int(cur.coords.x + floor((dest.coords.x - cur.coords.x) / 2.0))
					y1 = int(cur.coords.y + floor((dest.coords.y - cur.coords.y) / 2.0))
					x2 = int(cur.coords.x + ceil((dest.coords.x - cur.coords.x) / 2.0))
					y2 = int(cur.coords.y + ceil((dest.coords.y - cur.coords.y) / 2.0))
					loc1 = fife.ExactModelCoordinate(x1, y2, cur.coords.z)
					loc2 = fife.ExactModelCoordinate(x2, y1, cur.coords.z)
					if (not self.isBlocked(loc1, 4)) and (not self.isBlocked(loc2, 4)):
						return 3
		return 100

	def possibleMoves(self, turns = 0):
		"""Return all tiles current character can move to."""
		possible_moves = []
		if turns == 0:
			for tile in self.tiles:
				if (tile.movement_cost <= self.current_character_turn.cur_AP) and (tile.movement_cost > 0):
					possible_moves.append(tile)
		else:
			for tile in self.tiles:
				if (tile.movement_cost <= (self.current_character_turn.max_AP * turns)) and (tile.movement_cost > (self.current_character_turn.max_AP * (turns - 1))):
					possible_moves.append(tile)
		return possible_moves

	def isBlocked(self, coords, height):
		"""Return whether the given location contains a blocking object. Also checks higher locations according to the height parameter."""
		if self.isBlockedByCharacter(coords, height) or self.isBlockedByWall(coords, height) or self.isBlockedByObstacle(coords, height):
			return True
		else:
			return False
	
	def isBlockedByCharacter(self, coords, height):
		"""Return whether the given location contains a character. Also checks higher locations according to the height parameter."""
		for char in self.characters:	
			if char.coords.x == coords.x and char.coords.y == coords.y and (char.coords.z + char.height) > coords.z and char.coords.z <= (coords.z + height):
				return True
		return False

	def isBlockedByObstacle(self, coords, height):
		"""Return whether the given location contains an obstacle. Also checks higher locations according to the height parameter."""
		for obst in self.obstacles:
			if obst.coords.x == coords.x and obst.coords.y == coords.y and (obst.coords.z + obst.height) > coords.z and obst.coords.z <= (coords.z + height):
				return True
		return False

	def isBlockedByWall(self, ex_coords, height):
		"""Return whether the given location contains a wall. Also checks higher locations according to the height parameter."""
		#coords = location.getLayerCoordinates()
		# FIXME: fife bug workaround (Location.getLayerCoordinates() imprecise for hex grids)
		location = fife.Location(self.maplayer)
		location.setExactLayerCoordinates(ex_coords)
		coords = self.maplayer.getCellGrid().toLayerCoordinates(location.getMapCoordinates())
		# FIXME: temporary simple implementation to avoid using the fife layer
		#coords = gridhelper.toLayer(ex_coords)
		for i in xrange(height):
			if (coords.x, coords.y, coords.z) in self.wall_map:
				return True
			coords.z += 1
		return False

	def isLOS(self, tile1, tile2):
		if tile1.tile.los_cache.count(tile2.tile) > 0:
			return True
		else:
			return False

	def testLOS(self, coords1, coords2):
		"""Return False if a line from loc1 to loc2 is blocked by a wall, True if the line is clear. Uses locations slightly above the ones given."""
		ex_coords1 = gridhelper.toExact(coords1)
		ex_coords2 = gridhelper.toExact(coords2)
		step = (ex_coords2 - ex_coords1) / 10.0
		for i in range(1,10):
			ex_coords = ex_coords1 + step * float(i)
			if self.isBlockedByWall(fife.ExactModelCoordinate(ex_coords.x, ex_coords.y, ex_coords.z + 1), 1):
				return False
		return True

	def isTrajectory(self, tile1, tile2):
		if tile1.tile.trajectory_cache.count(tile2.tile) > 0:
			return True
		else:
			return False

	def testTrajectory(self, coords1, coords2, trajectory, visualize = False):
		"""
		Return False if an arc from loc1 to loc2 defined by trajectory is blocked by a wall or outside range, True if the arc is clear and in range.
		Uses locations slightly above the ones given.
		Creates an optional visual trajectory.
		"""
		# TODO: visualization probably should not be done here
		ex_coords1 = gridhelper.toExact(coords1)
		ex_coords2 = gridhelper.toExact(coords2)

		z_scale = 3.0
		dist = gridhelper.horizontalDistance(coords1, coords2) * z_scale
		if dist == 0:
			return False
		z = coords2.z - coords1.z
		g = 5.0 / z_scale
		d2 = pow(trajectory.range, 4) - g * (g * pow(dist, 2) + 2 * z * pow(trajectory.range, 2))
		if d2 < 0:
			return False
		angle1 = atan((pow(trajectory.range, 2) - sqrt(d2)) / (g * dist))
		#angle2 = atan((pow(trajectory.range, 2) + sqrt(d2)) / (g * dist))

		step = (ex_coords2 - ex_coords1) / 20.0
		if self.visual and visualize:
			los = VisualLOS(self.application)
			self.application.real_timeline.addTimer(TacticsTimer("line of sight", 1, 1, los.destroy))
		for i in range(1,20):
			ex_coords = ex_coords1 + step * float(i)
			ex_coords.z = ex_coords1.z + float(dist) / 20.0 * float(i) * tan(angle1) - g * pow(float(dist) / 20.0 * float(i), 2) / (2 * pow(trajectory.range * cos(angle1), 2))
			if self.visual and visualize:
				location = fife.Location(self.maplayer)
				location.setExactLayerCoordinates(fife.ExactModelCoordinate(ex_coords.x, ex_coords.y, ex_coords.z + 2))
				los.addDot(location, self.shadowLocation(location))
			if self.isBlockedByWall(fife.ExactModelCoordinate(ex_coords.x, ex_coords.y, ex_coords.z + 1.5), 1):
				if self.visual and visualize:
					self.application.gui.sayBubble(los.instances[-1], "blocked", 50)
				return False
		return True

	def shadowLocation(self, location):
		"""Return the location a shadow cast by an object at the given location should be at. This is the location of the first wall below the given location."""
		shadow_location = fife.Location(location)
		shadow_coords = location.getExactLayerCoordinates()
		shadow_coords.z = floor(shadow_coords.z-1)
		while shadow_coords.z >= -2:
			shadow_location.setExactLayerCoordinates(shadow_coords)
			if self.isBlockedByWall(shadow_location.getExactLayerCoordinates(), 1):
				break
			shadow_coords.z -= 1
		shadow_coords.z += 1
		shadow_location.setExactLayerCoordinates(shadow_coords)
		return shadow_location

	def isValidTarget(self, source, target, targeting_rules):
		"""Return whether target can be targeted by source under targeting_rules. Source is a character and target is a character, tile or obstacle."""
		if targeting_rules.can_target_self and (source == target):
			return True
		if (not targeting_rules.can_target_self) and (source.coords == target.coords):
			return False
		if type(target) == TacticsCharacter:
			if target.cur_HP <= 0:
				return False
		if (source != target) and ((targeting_rules.can_target_other and (type(target)) == TacticsCharacter) or (targeting_rules.can_target_tile and (type(target)) == TacticsTile) or (targeting_rules.can_target_obstacle and (type(target)) == Obstacle)):
			if targeting_rules.trajectory.type == targeting_rules.trajectory.TRAJECTORY_SINGLE:
				if (gridhelper.horizontalDistance(source.coords, target.coords) <= targeting_rules.trajectory.range) and ((source.coords.z - target.coords.z) <= targeting_rules.trajectory.range_down) and ((target.coords.z - source.coords.z) <= targeting_rules.trajectory.range_up):
					return True
			elif targeting_rules.trajectory.type == targeting_rules.trajectory.TRAJECTORY_LINE:
				if (gridhelper.horizontalDistance(source.coords, target.coords) <= targeting_rules.trajectory.range) and self.isLOS(source, target) and ((source.coords.z - target.coords.z) <= targeting_rules.trajectory.range_down) and ((target.coords.z - source.coords.z) <= targeting_rules.trajectory.range_up):
					return True
			elif targeting_rules.trajectory.type == targeting_rules.trajectory.TRAJECTORY_ARC:
				if self.isTrajectory(source, target):
					return True
		return False

	def getValidTargets(self, source, targeting_rules):
		"""Return all possible targets from source under targeting_rules."""
		valid_targets = []
		if targeting_rules.can_target_other:
			for target in self.characters:
				if self.isValidTarget(source, target, targeting_rules):
					valid_targets.append(target)
		if targeting_rules.can_target_obstacle:
			for target in self.obstacles:
				if self.isValidTarget(source, target, targeting_rules):
					valid_targets.append(target)
		if targeting_rules.can_target_tile:
			for target in self.tiles:
				if self.isValidTarget(source, target, targeting_rules):
					valid_targets.append(target)
		return valid_targets

	def getTargetsInArea(self, source, target, targeting_rules):
		"""Return all objects affected by an action performed by source targeting target under targeting_rules. Source is a character and target is a character, tile or obstacle."""
		targets = []

		if targeting_rules.area.type == targeting_rules.area.AREA_SINGLE:
			targets.append(target)

		if targeting_rules.area.type == targeting_rules.area.AREA_CIRCLE:
			if targeting_rules.can_target_tile:
				for tile in self.tiles:
					if gridhelper.horizontalDistance(target.coords, tile.coords) < targeting_rules.area.radius and ((target.coords.z - tile.coords.z) <= targeting_rules.area.range_down) and ((tile.coords.z - target.coords.z) <= targeting_rules.area.range_up):
						if self.isLOS(target, tile):
							targets.append(tile)
			if targeting_rules.can_target_other:
				for char in self.characters:
					if gridhelper.horizontalDistance(target.coords, char.coords) < targeting_rules.area.radius and ((target.coords.z - char.coords.z) <= targeting_rules.area.range_down) and ((char.coords.z - target.coords.z) <= targeting_rules.area.range_up):
						if self.isLOS(target, char):
							targets.append(char)
			if targeting_rules.can_target_obstacle:
				for obstacle in self.obstacles:
					if gridhelper.horizontalDistance(target.coords, obstacle.coords) < targeting_rules.area.radius and ((target.coords.z - obstacle.coords.z) <= targeting_rules.area.range_down) and ((obstacle.coords.z - target.coords.z) <= targeting_rules.area.range_up):
						if self.isLOS(target, obstacle):
							targets.append(obstacle)

		if targeting_rules.area.type == targeting_rules.area.AREA_LINE:
			targets.append(target)

		if targeting_rules.area.type == targeting_rules.area.AREA_CONE:
			if targeting_rules.can_target_tile:
				for tile in self.tiles:
					if gridhelper.horizontalDistance(source.coords, tile.coords) < targeting_rules.area.radius and ((source.coords.z - tile.coords.z) <= targeting_rules.area.range_down) and ((tile.coords.z - source.coords.z) <= targeting_rules.area.range_up):
						if (gridhelper.calcDirectionDiagonal(source.coords, target.coords) == gridhelper.calcDirection(source.coords, tile.coords)) or (gridhelper.calcDirectionDiagonal(source.coords, target.coords) == gridhelper.calcDirectionDiagonal(source.coords, tile.coords)):
							if self.isLOS(source, tile):
								targets.append(tile)
			if targeting_rules.can_target_other:
				for char in self.characters:
					if gridhelper.horizontalDistance(source.coords, char.coords) < targeting_rules.area.radius and ((source.coords.z - char.coords.z) <= targeting_rules.area.range_down) and ((char.coords.z - source.coords.z) <= targeting_rules.area.range_up):
						if (gridhelper.calcDirectionDiagonal(source.coords, target.coords) == gridhelper.calcDirection(source.coords, char.coords)) or (gridhelper.calcDirectionDiagonal(source.coords, target.coords) == gridhelper.calcDirectionDiagonal(source.coords, char.coords)):
							if self.isLOS(source, char):
								targets.append(char)
			if targeting_rules.can_target_obstacle:
				for obstacle in self.obstacles:
					if gridhelper.horizontalDistance(source.coords, obstacle.coords) < targeting_rules.area.radius and ((source.coords.z - obstacle.coords.z) <= targeting_rules.area.range_down) and ((obstacle.coords.z - source.coords.z) <= targeting_rules.area.range_up):
						if (gridhelper.calcDirectionDiagonal(source.coords, target.coords) == gridhelper.calcDirection(source.coords, obstacle.coords)) or (gridhelper.calcDirectionDiagonal(source.coords, target.coords) == gridhelper.calcDirectionDiagonal(source.coords, obstacle.coords)):
							if self.isLOS(source, obstacle):
								targets.append(obstacle)

		return targets
		
	def addObstacleAt(self, tile, obstacle_type):
		"""Create an obstacle of obstacle_type at coordinates. Add a tile on top of it."""
		if tile.blocker:
			return
		obstacle = Obstacle(tile, gridhelper.getObjectZSize(obstacle_type), self)
		self.assignID(obstacle)
		if self.visual:
			obstacle.createVisual()
		self.obstacles.append(obstacle)
		tile.visitors.append(obstacle)
		tile.blocker = True
		# add a tile on top of the obstacle
		coordinates2 = fife.ModelCoordinate(tile.coords)
		coordinates2.z += gridhelper.getObjectZSize(obstacle_type)
		new_tile = self.addTile(coordinates2, obstacle_type)
		obstacle.top_tile = new_tile

	def removeObstacle(self, obstacle):
		"""Delete the given obstacle. Delete the assiocated tile on top of it. Make the objects on top fall down."""
		obstacle.tile.visitors.remove(obstacle)
		obstacle.tile.blocker = False
		self.removeTile(obstacle.top_tile)
		self.obstacles.remove(obstacle)
		for visitor in obstacle.top_tile.visitors:
			visitor.fallDownTo(obstacle.tile)
		for trap in obstacle.top_tile.traps:
			trap.fallDownTo(obstacle.tile)
		for surface in obstacle.top_tile.surface_effects:
			if surface.visual:
				surface.visual.destroy()

	def addTrapAt(self, tile, trap_type):
		"""Create a trap of trap_type at coordinates."""
		if tile.blocker or (tile.getSurface() == "Water"):
			return
		trap = Trap(tile, self)
		if self.visual:
			trap.createVisual()
		tile.traps.append(trap)

	def addSurfaceAt(self, tile, surface_type):
		"""Add a surface of surface_type at coordinates."""
		for surface in tile.surface_effects:
			if ((surface_type == "tar") and (surface.name == "Tar")) or ((surface_type == "ice") and (surface.name == "Ice")):
				return
		if surface_type == "tar":
			surface = SurfaceTar(tile, self)
			if self.visual:
				surface.createVisual()
		elif surface_type == "ice":
			surface = SurfaceIce(tile, self)
			if self.visual:
				surface.createVisual()
				self.application.gui.combat_log.printMessage("Water froze.")
		tile.surface_effects.append(surface)

	def addCharacterAt(self, tile, name):
		"""Create and return a character with a given name at coordinates."""
		character = TacticsCharacter(name, tile, self)
		self.assignID(character)
		if self.visual:
			character.createVisual()
		self.characters.append(character)
		tile.visitors.append(character)
		tile.blocker = True
		return character
	
	def getThreateningCharacter(self, tile):
		"""Return one character threatening the location with an attack of opportunity."""
		for character in self.characters:
			if character.isThreatening(tile):
				return character

	def getSurvivingTeams(self):
		teams = []
		for character in self.characters:
			if (character.cur_HP > 0) and not (character.team in teams):
				teams.append(character.team)
		return teams

