#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Tomasz "Niektóry" Turowski

from fife import fife
from math import sqrt, pow, atan, tan, cos

import gridhelper
from character import TacticsCharacter


class ProjectileRoute:
	def __init__(self, map_object, destination, speed, trajectory):
		self.map_object = map_object
		self.origin = map_object.source
		self.destination = destination
		self.speed = speed
		self.trajectory = trajectory

	def follow(self):
		instance_coords = self.map_object.instance.getLocation().getExactLayerCoordinates()
		
		# distance from the current partial position to the destination
		dx = (self.destination.x - instance_coords.x)
		dy = (self.destination.y - instance_coords.y)
		dz = (self.destination.z - instance_coords.z)
		distance = sqrt(dx * dx + dy * dy)
		# distance from the origin to the destination
		path_dx = (self.destination.x - self.origin.x)
		path_dy = (self.destination.y - self.origin.y)
		path_dz = (self.destination.z - self.origin.z)
		path_distance = sqrt(path_dx * path_dx + path_dy * path_dy)

		z_scale = 3.0
		grid_distance = gridhelper.horizontalDistance(self.origin, self.destination) * z_scale

		if (distance < self.speed) or (grid_distance == 0):
			# pop to the destination
			self.map_object.moveInstance(self.destination)
			return False
		else:
			g = 5.0 / z_scale
			d2 = pow(self.trajectory.range, 4) - g * (g * pow(grid_distance, 2) + 2 * path_dz * pow(self.trajectory.range, 2))
			angle1 = atan((pow(self.trajectory.range, 2) - sqrt(d2)) / (g * grid_distance))

			# normal partial movement
			instance_coords.x += (dx / distance) * self.speed
			instance_coords.y += (dy / distance) * self.speed
			# z calculation
			instance_coords.z = self.origin.z + grid_distance * (1 - distance / path_distance) * tan(angle1) - g * pow(grid_distance * (1 - distance / path_distance), 2) / (2 * pow(self.trajectory.range * cos(angle1), 2)) + 2
			self.map_object.moveInstance(instance_coords)
			return True


class FallRoute:
	def __init__(self, map_object, destination, speed):
		self.map_object = map_object
		self.destination = destination
		self.speed = speed

	def follow(self):
		self.speed += 0.01
		instance_coords = self.map_object.visual.instance.getLocation().getExactLayerCoordinates()
		
		if self.destination.coords.z >= instance_coords.z - self.speed:
			# pop to the destination
			self.map_object.visual.moveInstance(self.destination.coords)
			return False
		else:
			instance_coords.z -= self.speed
			self.map_object.visual.moveInstance(instance_coords)
			return True


class MoveRouteBase:
	def follow(self):
		# fixed?: inconsistent speed because of using exact layer coordinates instead of map coordinates
		# there's also a rotation problem at some angles, probably for the same reason
		if self.next >= len(self.path):
		#	print "Warning: Next node out of range. Path:"
		#	for node in self.path:
		#		print node.coords.x, node.coords.y, node.coords.z
			return False

		grid = self.map_object.visual.instance.getLocation().getLayer().getCellGrid()

		next_node = self.path[self.next]
		next_node_coords = grid.toMapCoordinates(next_node.coords)
		instance_coords = self.map_object.visual.instance.getLocation().getMapCoordinates()
		prev_node = self.path[self.next - 1]
		prev_node_coords = grid.toMapCoordinates(prev_node.coords)

		# distance from the current partial position to the target node
		dx = (next_node_coords.x - instance_coords.x)
		dy = (next_node_coords.y - instance_coords.y)
		dz = (next_node_coords.z - instance_coords.z)
		distance = sqrt(dx * dx + dy * dy)
		# distance from the previous node to the target node
		cell_dx = (next_node_coords.x - prev_node_coords.x)
		cell_dy = (next_node_coords.y - prev_node_coords.y)
		cell_dz = (next_node_coords.z - prev_node_coords.z)
		cell_distance = sqrt(cell_dx * cell_dx + cell_dy * cell_dy)

		if distance < self.speed:
			# pop to next node
			self.next += 1
			self.map_object.visual.moveInstance(next_node.coords)
			continue_route = (self.next < len(self.path))
			if continue_route:
				#print "A:", fife.getAngleBetween(instance_coords, grid.toMapCoordinates(self.path[self.next].coords))
				self.map_object.visual.instance.setRotation(fife.getAngleBetween(instance_coords, grid.toMapCoordinates(self.path[self.next].coords)))
			return continue_route
		else:
			#print "B:", fife.getAngleBetween(instance_coords, next_node_coords)
			self.map_object.visual.instance.setRotation(fife.getAngleBetween(instance_coords, next_node_coords))
			# normal partial movement
			instance_coords.x += (dx / distance) * self.speed
			instance_coords.y += (dy / distance) * self.speed
			# z calculation
			if gridhelper.horizontalDistance(prev_node.coords, next_node.coords) == 1:
				# walking between adjacent nodes
				if cell_dz > 0:
					# uphill
					if (distance / cell_distance) < 0.5:
						# flat movement on target tile
						instance_coords.z = next_node_coords.z
					else:
						# jumping up from previous tile
						instance_coords.z = prev_node_coords.z + cell_dz - 4*(0.5-distance/cell_distance)*(0.5-distance/cell_distance) * cell_dz
				elif cell_dz < 0:
					# downhill
					if (distance / cell_distance) < 0.5:
						# jumping down on target tile
						instance_coords.z = prev_node_coords.z + 4*(0.5-distance/cell_distance)*(0.5-distance/cell_distance) * cell_dz
			elif gridhelper.horizontalDistance(prev_node_coords, next_node_coords) == 2:
				# jumping 2 tiles
				if (distance / cell_distance) > 0.5:
					# up
					instance_coords.z = prev_node_coords.z + 1 - 4*(0.5-distance/cell_distance)*(0.5-distance/cell_distance)
				else:
					# down
					instance_coords.z = prev_node_coords.z + 1 + 4*(0.5-distance/cell_distance)*(0.5-distance/cell_distance) * (cell_dz - 1)
			self.map_object.visual.moveInstance(grid.toExactLayerCoordinates(instance_coords))
			return True


class MoveRoute(MoveRouteBase):
	def __init__(self, map_object, destination, speed, application):
		self.map_object = map_object
		self.origin = map_object.tile
		self.destination = destination
		self.path = []
		self.next = 1
		self.speed = speed
		self.application = application
		self.solve()

	def solve(self):
		tile = self.destination
		while True:
			if len(tile.traps) > 0:
				self.path = []
				self.destination = tile
			if self.map_object.world.getThreateningCharacter(tile):
				self.path = []
				self.destination = tile
			if tile.movement_cost > self.map_object.cur_AP:
				self.destination = tile.previous
			else:
				self.path.insert(0, tile)
			if tile.previous:
				tile = tile.previous
			else:
				break


class PushRoute(MoveRouteBase):
	def __init__(self, map_object, destination, speed):
		self.map_object = map_object
		self.origin = map_object.tile
		self.destination = destination
		self.path = [self.origin, self.destination]
		self.next = 1
		self.speed = speed


class TacticsPather(fife.TimeEvent):
	def __init__(self, application):
		super(TacticsPather, self).__init__(0)
		self.application = application
		self.routes = []
		
	def updateEvent(self, time):
		if self.routes == []:
			return
		remove_routes = []
		for route in self.routes:
			if not route.follow():
				route.map_object.onMoveFinished()
				remove_routes.append(route)
		for route in remove_routes:
			self.routes.remove(route)

	def planMove(self, map_object, destination):
		new_route = MoveRoute(map_object, destination, 0, self.application)
		#self.planRoute(new_route.route)
		return new_route

	def move(self, map_object, route, speed):
		#new_route = MoveRoute(map_object, destination, speed / 10.0, self.application)
		route.speed = speed / 10.0
		self.routes.append(route)
		return route

	def push(self, map_object, destination, speed):
		new_route = PushRoute(map_object, destination, speed / 10.0)
		self.routes.append(new_route)

	def shoot(self, map_object, destination, speed, trajectory):
		new_route = ProjectileRoute(map_object, destination, speed / 10.0, trajectory)
		self.routes.append(new_route)

	def fall(self, map_object, destination, speed):
		new_route = FallRoute(map_object, destination, speed / 10.0)
		self.routes.append(new_route)


