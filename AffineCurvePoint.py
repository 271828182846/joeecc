#
#	joeecc - A small Elliptic Curve Cryptography Demonstration.
#	Copyright (C) 2011-2011 Johannes Bauer
#	
#	This file is part of joeecc.
#
#	joeecc is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	joeecc is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with joeecc; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>
#

import math

from ModInt import ModInt
from Comparable import Comparable

class AffineCurvePoint(Comparable):
	def __init__(self, x, y, curve):
		assert(((x is None) and (y is None)) or ((x is not None) and (y is not None)))		# Either x and y are None (Point at Infty) or both are defined
		assert((x is None) or isinstance(x, int))
		assert((y is None) or isinstance(y, int))
#		assert(isinstance(curve, EllipticCurve))
		if x is None:
			# Point at infinity
			self._x = None
			self._y = None
		else:
			self._x = ModInt(x, curve.getp())
			self._y = ModInt(y, curve.getp())
		self._curve = curve

	def setmodulus(self, modulus):
		self._x.setmodulus(modulus)
		self._y.setmodulus(modulus)

	def getmodulus(self):
		return self._x.getmodulus()

	def getx(self):
		return self._x
	
	def gety(self):
		return self._y
	
	def getcurve(self):
		return self._curve

	def clone(self):
		return AffineCurvePoint(self.getx().getintvalue(), self.gety().getintvalue(), self.getcurve())

	def __iadd__(self, other):
		assert(isinstance(other, AffineCurvePoint))
	
		if self.infinity():
			self._x = other.getx()
			self._y = other.gety()
		elif self == -other:
			# K == -J, return O (point at infinity)
			self._x = None
			self._y = None
		elif self == other:
			# K == J, double self
			s = ((3 * self._x ** 2) + self._curve.geta()) // (2 * self._y)
			newx = s * s - (2 * self._x)
			newy = s * (self._x - newx) - self._y
			(self._x, self._y) = (newx, newy)
		else:
			# Point addition
			s = (self._y - other.gety()) // (self._x - other.getx())
			newx = (s ** 2) - self._x - other.getx()
			newy = s * (self._x - newx) - self._y
			(self._x, self._y) = (newx, newy)
		return self

	def __isub__(self, other):
		self += -other
		return self

	def __add__(self, other):
		n = self.clone()
		n += other
		return n

	def __rmul__(self, other):
		return self * other

	def __mul__(self, other):
		n = self.clone()
		n *= other
		return n

	def __imul__(self, scalar):
		# Scalar point multiplication
		assert(isinstance(scalar, int))
		
		n = self.clone()
		self._x = None
		self._y = None
		if scalar > 0:
			bitcount = math.ceil(math.log(scalar, 2)) + 1
			for bit in range(bitcount):
				if (scalar & (1 << bit)):
					self += n
				n += n
		return self


	def __sub__(self, other):
		n = self.clone()
		n -= other
		return n

	def __neg__(self):
		n = self.clone()
		n._y = -n.gety()
		return n

	def cmpkey(self):
		return (self.getx(), self.gety())

	def oncurve(self):
		lhs = self.gety() * self.gety()
		rhs = (self.getx() ** 3) + (self._curve.geta() * self.getx()) + self._curve.getb()
		return lhs == rhs

	def infinity(self):
		return self.getx() is None

	def __str__(self):
		return "(%s, %s)" % (str(self._x), str(self._y))

	def compress(self):
		return (self._x.getintvalue(), self._y.getintvalue() % 2)

	def uncompress(self, compressed):
		(x, ybit) = compressed
		self._x = ModInt(x, self._curve.getp())
		alpha = (self._x ** 3) + (self._curve.geta() * self._x) + self._curve.getb()
		(beta1, beta2) = alpha.sqrt()
		if (beta1.getintvalue() % 2) == ybit:
			self._y = beta1
		else:
			self._y = beta2
		return self

