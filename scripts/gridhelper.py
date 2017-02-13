# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

# this file contains a collection of helper functions for calculating grid positions etc.

from fife import fife

def sign(x):
	if x > 0:
		return 1
	elif x < 0:
		return -1
	else:
		return 0

def toExact(coords):
	"""Convert ModelCoordinate to ExactModelCoordinate"""
	return fife.ExactModelCoordinate(coords.x, coords.y, coords.z)

def toLayer(coords):
	"""Convert ExactModelCoordinate to ModelCoordinate"""
	return fife.ModelCoordinate(int(coords.x), int(coords.y), int(coords.z))

def horizontalDistance(loc1, loc2):
	"""Return the horizontal grid distance between the given locations (number of hexes traversed, not straight line distance)."""
	dx = loc1.x - loc2.x
	dy = loc1.y - loc2.y
	dxy = 0
	if dx > 0 and dy < 0:
		if dx > -dy:
			dxy = -dy
		else:
			dxy = dx
	if dx < 0 and dy > 0:
		if dy > -dx:
			dxy = dx
		else:
			dxy = -dy
	dx -= dxy
	dy += dxy
	return abs(dx) + abs(dy) + abs(dxy)

def calcDirection(coords1, coords2):
	"""Return the horizontal direction from loc1 to loc2, formatted as coordinates. Can be diagonal."""
	diff = coords2 - coords1
	dx = diff.x
	dy = diff.y
	dxy = 0
	if dx > 0 and dy < 0:
		if dx > -dy:
			dxy = -dy
		else:
			dxy = dx
	if dx < 0 and dy > 0:
		if dy > -dx:
			dxy = dx
		else:
			dxy = -dy
	dx -= dxy
	dy += dxy
	# same cell
	if (dx == 0) and (dy == 0) and (dxy == 0):
		dir_x = 0
		dir_y = 0
	# straight
	elif (abs(dx) > abs(dy)) and (abs(dx) > abs(dxy)):
		if dx > 0:
			dir_x = 1
		else:
			dir_x = -1
		dir_y = 0
	elif (abs(dy) > abs(dx)) and (abs(dy) > abs(dxy)):
		if dy > 0:
			dir_y = 1
		else:
			dir_y = -1
		dir_x = 0
	elif (abs(dxy) > abs(dx)) and (abs(dxy) > abs(dy)):
		if dxy > 0:
			dir_x = 1
			dir_y = -1
		else:
			dir_x = -1
			dir_y = 1
	# diagonal
	elif dx == dy:
		if dx > 0:
			dir_x = 1
			dir_y = 1
		else:
			dir_x = -1
			dir_y = -1
	elif dx == dxy:
		if dx > 0:
			dir_x = 2
			dir_y = -1
		else:
			dir_x = -2
			dir_y = 1
	elif dy == -dxy:
		if dy > 0:
			dir_x = -1
			dir_y = 2
		else:
			dir_x = 1
			dir_y = -2
	else:
		# this shouldn't happen
		print "Direction error!", dx, ":", dy, ":", dxy
	return fife.ModelCoordinate(dir_x, dir_y, 0)

def calcDirectionDiagonal(coords1, coords2):
	"""Return the horizontal direction from loc1 to loc2, formatted as coordinates. Favors diagonals."""
	diff = coords2 - coords1
	dx = diff.x
	dy = diff.y
	dxy = 0
	if dx > 0 and dy < 0:
		if dx > -dy:
			dxy = -dy
		else:
			dxy = dx
	if dx < 0 and dy > 0:
		if dy > -dx:
			dxy = dx
		else:
			dxy = -dy
	dx -= dxy
	dy += dxy
	# same cell
	if (dx == 0) and (dy == 0) and (dxy == 0):
		dir_x = 0
		dir_y = 0
	# straight
	elif (abs(dx) > 0) and (dy == 0) and (dxy == 0):
		if dx > 0:
			dir_x = 1
		else:
			dir_x = -1
		dir_y = 0
	elif (abs(dy) > 0) and (dx == 0) and (dxy == 0):
		if dy > 0:
			dir_y = 1
		else:
			dir_y = -1
		dir_x = 0
	elif (abs(dxy) > 0) and (dx == 0) and (dy == 0):
		if dxy > 0:
			dir_x = 1
			dir_y = -1
		else:
			dir_x = -1
			dir_y = 1
	# diagonal
	elif sign(dx) == sign(dy):
		if dx > 0:
			dir_x = 1
			dir_y = 1
		else:
			dir_x = -1
			dir_y = -1
	elif sign(dx) == sign(dxy):
		if dx > 0:
			dir_x = 2
			dir_y = -1
		else:
			dir_x = -2
			dir_y = 1
	elif sign(dy) == -sign(dxy):
		if dy > 0:
			dir_x = -1
			dir_y = 2
		else:
			dir_x = 1
			dir_y = -2
	else:
		# this shouldn't happen
		print "Direction error! diag", dx, ":", dy, ":", dxy
	return fife.ModelCoordinate(dir_x, dir_y, 0)

def inMeleeRange(cur, dest):
	"""Return whether dest location is in melee range of cur location."""
	if horizontalDistance(cur, dest) == 1:
		diff_z = cur.z - dest.z
		if (diff_z <= 3) and (diff_z >= -2):
			return True
	return False

def getObjectZSize(object_ID):
	"""Return the size of an object with the given ID and whether it extends up or down."""
	# TODO: this data should be elsewhere
	if object_ID == "boy":
		return 3
	elif object_ID == "block_gray":
		return -1
	elif object_ID == "water":
		return -1
	elif object_ID == "mushroom":
		return 2
	elif object_ID == "block_grass":
		return -1
	else:
		return 0

def getObjectSurface(wall_type):
	"""Return the surface type of an object with the given ID."""
	# TODO: this data should be elsewhere
	if wall_type == "block_gray":
		return "Pavement"
	elif wall_type == "water":
		return "Water"
	elif wall_type == "mushroom":
		return "Mushroom"
	elif wall_type == "block_grass":
		return "Grass"

def isDifficultSurface(surface):
	# TODO: this data should be elsewhere
	return (surface in ["Tar", "Water", "Ice"])
