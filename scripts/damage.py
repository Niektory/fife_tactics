# -*- coding: utf-8 -*-
# Copyright 2017 Tomasz "Niektóry" Turowski

class DamagePacket:
	def __init__(self, source, target, amount, dmg_type, add_effect = "none"):
		self.source = source
		self.target = target
		self.amount = amount
		self.type = dmg_type
		self.add_effect = add_effect
		self.final_damage = self.amount - self.target.getResistance(self.type)

	def infoString(self):
		if type(self.source) == str:
			return "Attack details\n----------------\nSource: " + self.source + "\nTarget: " + self.target.name + "\nAttack strength: " + str(self.amount) + "\nDamage type: " + self.type + "\nTarget's " + self.type + " resistance: " + str(self.target.getResistance(self.type)) + "\nFinal damage: " + str(self.final_damage) + "\nAdditional effect: " + self.add_effect
		else:
			return "Attack details\n----------------\nSource: " + self.source.name + "\nTarget: " + self.target.name + "\nAttack strength: " + str(self.amount) + "\nDamage type: " + self.type + "\nTarget's " + self.type + " resistance: " + str(self.target.getResistance(self.type)) + "\nFinal damage: " + str(self.final_damage) + "\nAdditional effect: " + self.add_effect
