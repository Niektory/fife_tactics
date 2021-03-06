# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

from fife import fife

from timeline import TacticsTimer
import gridhelper
from error import LogExceptionDecorator

class VisualLOS:
	def __init__(self, application):
		self.application = application
		self.instances = []
		
	def addDot(self, location, shadow_location):
		# shadow
		instance = self.application.maplayer.createInstance(self.application.model.getObject("dot_red", "tactics"), shadow_location.getExactLayerCoordinates())
		instance.setCellStackPosition(125)
		fife.InstanceVisual.create(instance).setStackPosition(125)
		self.instances.append(instance)
		self.application.view.instance_renderer.addColored(instance, 0, 0, 0, 0)
		# floating dot
		instance = self.application.maplayer.createInstance(self.application.model.getObject("dot_red", "tactics"), location.getExactLayerCoordinates())
		instance.setCellStackPosition(125)
		fife.InstanceVisual.create(instance).setStackPosition(125)
		self.instances.append(instance)
		
	def destroy(self):
		for instance in self.instances:
			self.application.maplayer.deleteInstance(instance)


class Explosion(fife.InstanceActionListener):
	def __init__(self, application, coords, effect_type):
		fife.InstanceActionListener.__init__(self)
		self.application = application
		self.instance = self.application.maplayer.createInstance(self.application.model.getObject(effect_type, "tactics"), coords)
		self.instance.setCellStackPosition(125)
		fife.InstanceVisual.create(self.instance).setStackPosition(125)
		self.instance.addActionListener(self)
		self.instance.actOnce('boom')
		self.application.addAnimation(self)

#	def onInstanceActionFinished(self, instance, action):
#		self.instance.removeActionListener(self)
#		self.application.maplayer.deleteInstance(self.instance)

	def destroy(self):
		#self.application.maplayer.deleteInstance(self.instance)
		# FIXME: fife crashes when deleting many instances
		return

	@LogExceptionDecorator
	def onInstanceActionFinished(self, instance, action):
		self.instance.actRepeat('none')
		self.application.real_timeline.addTimer(TacticsTimer("explosion", 0, 1, self.destroy))
		self.application.removeAnimation(self)

	def onInstanceActionCancelled(self, instance, action):
		return


class Projectile(fife.InstanceActionListener):
	def __init__(self, application, source, target, final_action, proj_type, trajectory):
		fife.InstanceActionListener.__init__(self)
		self.application = application
		self.instance = self.application.maplayer.createInstance(self.application.model.getObject(proj_type, "tactics"), source)
		self.instance.setCellStackPosition(125)
		fife.InstanceVisual.create(self.instance).setStackPosition(125)
		self.instance.addActionListener(self)
		self.source = source
		self.target = target
		self.type = proj_type
		self.final_action = final_action
		self.application.pather.shoot(self, target, 1, trajectory)
		self.application.addAnimation(self)

	def moveInstance(self, coords, rotation = None):
		next_loc = self.instance.getLocation()
		next_loc.setExactLayerCoordinates(gridhelper.toExact(coords))
		self.instance.setLocation(next_loc)
		if rotation != None:
			self.instance.setRotation(rotation)

	def destroy(self):
		self.application.maplayer.deleteInstance(self.instance)

	@LogExceptionDecorator
	def onMoveFinished(self):
		self.application.real_timeline.addTimer(TacticsTimer("projectile", 0, 1, self.destroy))
		self.application.removeAnimation(self)
		self.final_action()

	def onInstanceActionCancelled(self, instance, action):
		return
