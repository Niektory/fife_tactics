# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

import math

import PyCEGUI

from fife import fife
from fife.extensions.pychan.internal import get_manager
from character import TacticsCharacter
from obstacle import Obstacle
from tile import TacticsTile

class TacticsView:
	def __init__(self, application):
		print "* Initializing view..."
		self.application = application
		self.camera = self.application.camera
		self.target_rotation = self.camera.getRotation()
		self.target_zoom = self.camera.getZoom()
		self.target_ZToY = self.camera.getZToY()

		self.camera_move_key_up = False
		self.camera_move_key_down = False
		self.camera_move_key_left = False
		self.camera_move_key_right = False
		self.camera_move_mouse_up = False
		self.camera_move_mouse_down = False
		self.camera_move_mouse_left = False
		self.camera_move_mouse_right = False

		self.camera.setViewPort(fife.Rect(0,0,self.application.engine.getRenderBackend().getScreenWidth(),self.application.engine.getRenderBackend().getScreenHeight()))
		
		print "  * Enabling renderers..."
		self.instance_renderer = fife.InstanceRenderer.getInstance(self.camera)
		#self.cell_renderer = fife.CellRenderer.getInstance(self.camera)
		#self.cell_renderer.setEnabled(True)
		#self.cell_renderer.setEnabledPathVisual(True)
		#self.cell_renderer.setPathColor(255, 210, 0)
		#self.cell_renderer.activateAllLayers(self.application.map)

		self.floating_text_renderer = fife.FloatingTextRenderer.getInstance(self.camera)
		#print get_manager()
		textfont = get_manager().createFont('fonts/rpgfont.png', 0, str(application.settings.get("FIFE", "FontGlyphs")));
		self.floating_text_renderer.setFont(textfont)
		self.floating_text_renderer.activateAllLayers(self.application.map)
		self.floating_text_renderer.setBackground(255, 210, 0, 127)
		self.floating_text_renderer.setBorder(255, 210, 0)
		self.floating_text_renderer.setEnabled(True)
		
		#self.grid_renderer = self.camera.getRenderer('GridRenderer')
		#self.grid_renderer.setEnabled(True)
		#self.grid_renderer.activateAllLayers(self.application.map)
		#self.coordinate_renderer = fife.CoordinateRenderer.getInstance(self.camera)
		#self.coordinate_renderer.setFont(textfont)
		#self.coordinate_renderer.setEnabled(True)
		#self.coordinate_renderer.activateAllLayers(self.application.map)
		
		# outline the terrain by cloning instances and manipulating drawing order
		print "  * Generating outlines and mist..."
		for instance in self.application.maplayer.getInstances():
			coordinates = instance.getLocation().getExactLayerCoordinates()

			if instance.getObject().getId()[:5] == "block":
				new_instance = self.application.maplayer.createInstance(instance.getObject(), coordinates)
				new_instance.setCellStackPosition(55)
				fife.InstanceVisual.create(new_instance).setStackPosition(55)

				newer_instance = self.application.maplayer.createInstance(instance.getObject(), coordinates)
				newer_instance.setCellStackPosition(110)
				fife.InstanceVisual.create(newer_instance).setStackPosition(110)

				self.instance_renderer.addOutlined(new_instance, 0, 0, 0, 1, 1, 15, 49, 32, 34)
				self.instance_renderer.addOutlined(instance, 0, 0, 0, 1, 1, 0, 0, 0, 0)

			elif instance.getObject().getId() == "water":
				coordinates.z -= 0.5
				new_instance = self.application.maplayer.createInstance(self.application.model.getObject("water_under", "tactics"), coordinates)
				new_instance.setCellStackPosition(110)

				coordinates.z -= 0.5
				newer_instance = self.application.maplayer.createInstance(self.application.model.getObject("water_under", "tactics"), coordinates)
				newer_instance.setCellStackPosition(110)

				instance.setCellStackPosition(110)
				
			#self.instance_renderer.addOutlined(new_instance, 0, 0, 0, 1, 1)
			#self.instance_renderer.addOutlined(instance, 0, 0, 0, 1, 1)
			
			# add mist gradient
			self.instance_renderer.addColored(newer_instance, 0, 0, 0, self.mistIntensity(coordinates.z))

	def mistIntensity(self, z):
		#return 255
		return min(int(225 + z * 5), 255)

	def zoomIn(self):
#		if self.target_zoom < 1:
#			self.target_zoom = 1
#		else:
		self.target_zoom = min(self.target_zoom + 1, 3)

	def zoomOut(self):
#		if self.target_zoom <= 1:
#			self.target_zoom = 0.5
#		else:
		self.target_zoom = max(self.target_zoom - 1, 1)

	def increaseElevation(self):
		self.target_ZToY = min(self.target_ZToY + 8, 16)

	def decreaseElevation(self):
		self.target_ZToY = max(self.target_ZToY - 8, 0)

	def rotateClockwise(self):
		self.target_rotation = (self.target_rotation - 60) % 360

	def rotateCounterclockwise(self):
		self.target_rotation = (self.target_rotation + 60) % 360

	def fineRotate(self, angle):
		self.target_rotation = (self.target_rotation + angle) % 360
		self.camera.setRotation(self.target_rotation)

	def snapRotation(self):
		self.target_rotation = math.floor(self.target_rotation / 60) * 60 + 30

	def moveCamera(self, camera_move_x, camera_move_y):
		cur_rot = self.camera.getRotation()
		coord = self.camera.getLocationRef().getMapCoordinates()
		coord.x += math.cos(cur_rot / 180 * math.pi) * camera_move_x - math.sin(cur_rot / 180 * math.pi) * camera_move_y
		coord.y += math.cos(cur_rot / 180 * math.pi) * camera_move_y + math.sin(cur_rot / 180 * math.pi) * camera_move_x
		self.camera.getLocationRef().setMapCoordinates(coord)
		self.camera.refresh()

	def animateCamera(self):
		cur_rot = self.camera.getRotation()
		if self.target_rotation != cur_rot:
			if (self.target_rotation - cur_rot) % 360 < 180:
				if (self.target_rotation - cur_rot) % 360 > 5:
					self.camera.setRotation((cur_rot + 5) % 360)
				else:
					self.camera.setRotation(self.target_rotation)
			else:
				if (self.target_rotation - cur_rot) % 360 < 355:
					self.camera.setRotation((cur_rot - 5) % 360)
				else:
					self.camera.setRotation(self.target_rotation)

		cur_zoom = self.camera.getZoom()
		if self.target_zoom > cur_zoom:
			if self.target_zoom < cur_zoom + 0.1:
				self.camera.setZoom(self.target_zoom)
			else:
				self.camera.setZoom(cur_zoom + 0.1)
		elif self.target_zoom < cur_zoom:
			if self.target_zoom > cur_zoom - 0.1:
				self.camera.setZoom(self.target_zoom)
			else:
				self.camera.setZoom(cur_zoom - 0.1)

		cur_ZToY = self.camera.getZToY()
		if self.target_ZToY > cur_ZToY:
			if self.target_ZToY < cur_ZToY + 1:
				self.camera.setZToY(self.target_ZToY)
			else:
				self.camera.setZToY(cur_ZToY + 1)
		elif self.target_ZToY < cur_ZToY:
			if self.target_ZToY > cur_ZToY - 1:
				self.camera.setZToY(self.target_ZToY)
			else:
				self.camera.setZToY(cur_ZToY - 1)

		if self.camera_move_key_up or self.camera_move_mouse_up:
			camera_move_y = -0.4
		elif self.camera_move_key_down or self.camera_move_mouse_down:
			camera_move_y = 0.4
		else:
			camera_move_y = 0
		if self.camera_move_key_left or self.camera_move_mouse_left:
			camera_move_x = -0.4
		elif self.camera_move_key_right or self.camera_move_mouse_right:
			camera_move_x = 0.4
		else:
			camera_move_x = 0
		self.moveCamera(camera_move_x, camera_move_y)

	def getInstancesAt(self, clickpoint):
		return self.camera.getMatchingInstances(clickpoint, self.application.maplayer)

	def highlightInstances(self):
		for character in self.application.world.characters:
			if character.visual.instance:
				# clear colorings and outlines from characters
				self.instance_renderer.removeOutlined(character.visual.instance)
				self.instance_renderer.removeColored(character.visual.instance)
				# display fog on characters
				self.instance_renderer.addColored(character.visual.instance, 0, 0, 0, self.mistIntensity(character.visual.instance.getLocation().getLayerCoordinates().z))
			# move shadows under characters and fire
			#character.shadow.setLocation(self.application.grid.shadowLocation(character.instance.getLocation()))
			#character.fire.setLocation(character.instance.getLocation())

		for obstacle in self.application.world.obstacles:
			# clear colorings and outlines from obstacles
			self.instance_renderer.removeOutlined(obstacle.visual.instance)
			self.instance_renderer.removeColored(obstacle.visual.instance)

		#route_planned = False
		
		# display movement grid
		for tile in self.application.world.tiles:
			if self.application.current_character and not self.application.selected_action and not self.application.animating() and not self.application.replaying:
				if tile.movement_cost <= self.application.current_character.cur_AP and tile.movement_cost > 0:
					tile.visual.instance.act('movement', True)
				else:
					tile.visual.instance.act('transparent', True)
			else:
				tile.visual.instance.act('transparent', True)

		if (self.application.gui.context.getWindowContainingMouse().getName() == "_MasterRoot") \
				and not self.application.animating() and not self.application.replaying:
			# on mouse over
			ptx, pty = self.application.engine.getCursor().getPosition()
			pt = fife.ScreenPoint(ptx, pty)
			# move the tooltip near the mouse cursor
			self.application.gui.tooltip.move(ptx, pty)
			instances = self.getInstancesAt(pt);
			for instance in instances:
				# skip distractions under the cursor
				if instance.getObject().getId() in ["shadow", "dot_red", "fire", "tar"]:
					continue
				# display object name in the tooltip
				self.application.gui.tooltip.printMessage("Object ID: " + instance.getObject().getId())
				# display coordinates in the tooltip
				self.application.gui.tooltip.printMessage("Coordinates: " + str(instance.getLocation().getLayerCoordinates()))
				# display tile info in the tooltip
				if instance.getObject().getId() == 'tile':
					surface = self.application.world.visual.findTile(instance).getSurface()
					self.application.gui.tooltip.printMessage("Surface: " + surface)
					if surface in ["Tar", "Water", "Ice"]:
						self.application.gui.tooltip.printMessage("Movement restricted")
				# display character info in the tooltip
				if instance.getObject().getId() == 'boy':
					target_character = self.application.world.visual.findCharacter(instance)
					self.application.gui.tooltip.printMessage("Name: " + target_character.name)
					self.application.gui.tooltip.printMessage("Team: " + str(target_character.team))
					self.application.gui.tooltip.printMessage("AP: " + str(target_character.cur_AP) + "/" + str(target_character.max_AP))
					self.application.gui.tooltip.printMessage("HP: " + str(target_character.cur_HP) + "/" + str(target_character.max_HP))
					self.application.gui.tooltip.printMessage("Opportunity attacks: " + str(target_character.opportunity_attacks) + "/" + str(target_character.max_opportunity_attacks))
					if target_character.timer:
						self.application.gui.tooltip.printMessage(str(target_character.timer.getTicks()) + " ticks to next turn")
					if target_character == self.application.world.current_character_turn:
						self.application.gui.tooltip.printMessage("Current turn")
					if target_character.cur_HP <= 0:
						self.application.gui.tooltip.printMessage("Dead")
					if target_character.fire_timer:
						self.application.gui.tooltip.printMessage("Burning", "[colour='FFFF9000']")
					if target_character.freeze_timer:
						self.application.gui.tooltip.printMessage("Frozen", "[colour='FF00FFFF']")
				# highlight a tile or character
				if not self.application.selected_action:
					if instance.getObject().getId() == 'boy':
						self.instance_renderer.addColored(instance, 255, 210, 0, 128)
						self.instance_renderer.addOutlined(instance, 255, 210, 0, 1)
					elif instance.getObject().getId() == 'tile':
						if self.application.current_character:
							if instance.getLocation().getLayerCoordinates() != self.application.current_character.coords:
								# plan route to highlighted tile
								path = self.application.current_character.planRoute(self.application.world.visual.findTile(instance))
								if len(path) > 0:
									for path_node in path[1:-1]:
										path_node.visual.instance.act('path', True)
									path[-1].visual.instance.act('blocked', True)
								# display route length in the tooltip
								movement_cost = self.application.world.visual.findTile(instance).movement_cost
								if movement_cost == 99:
									self.application.gui.tooltip.printMessage("No movement possible")
								else:
									self.application.gui.tooltip.printMessage("Movement cost: " + str(movement_cost))
						instance.act('selected', True)
				if self.application.selected_action:
					# highlight area of effect
					if instance.getObject().getId() in ["boy", "tile", "mushroom"]:
						target = self.application.world.visual.findObject(instance)
						if self.application.world.isValidTarget(self.application.current_character, target, self.application.selected_action.targeting_rules):
							targets = self.application.world.getTargetsInArea(self.application.current_character, target, self.application.selected_action.targeting_rules)
							for target in targets:
								if type(target) in [TacticsCharacter,Obstacle]:
									if target.visual.instance:
										self.instance_renderer.addColored(target.visual.instance, 255, 210, 0, 128)
										self.instance_renderer.addOutlined(target.visual.instance, 255, 210, 0, 1)
								elif type(target) == TacticsTile:
									target.visual.instance.act('selected', True)
				break

		# outline the selected character
		if self.application.current_character:
			if self.application.current_character.visual.instance:
				self.instance_renderer.addOutlined(self.application.current_character.visual.instance, 255, 255, 255, 2)

	def pump(self):
		self.animateCamera()
		self.highlightInstances()
