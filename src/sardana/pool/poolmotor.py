#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module is part of the Python Pool libray. It defines the base classes
for"""

__all__ = [ "PoolMotor" ]

__docformat__ = 'restructuredtext'

import math

from poolbase import *
from pooldefs import *
from poolelement import *
from poolmotion import *
from poolmoveable import *

class PoolMotor(PoolElement):

    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._position = None
        self._wposition = None
        self._dial_position = None
        self._offset = 0.0
        self._sign = 1.0
        self._backlash = 0
        self._step_per_unit = 1.0
        self._limit_switches = None
        self._limit_switches_event = None
        self._acceleration = None
        self._deceleration = None
        self._velocity = None
        self._base_rate = None
        self.set_action_cache(PoolMotion("%s.Motion" % self._name))

    def get_type(self):
        return ElementType.Motor
    
    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------

    def _from_ctrl_state_info(self, state_info):
        if len(state_info) > 2:
            state, status, ls = state_info[:3]
        else:
            state, ls = state_info[:2]
            status = ''
        state, ls = int(state), tuple(map(bool, (ls&4,ls&2,ls&1)))
        return state, status, ls
    
    def _set_state_info(self, state_info, propagate=1):
        PoolElement._set_state_info(self, state_info[:2], propagate=propagate)
        ls = state_info[-1]
        self._set_limit_switches(ls, propagate=propagate)
    
    # --------------------------------------------------------------------------
    # limit switches
    # --------------------------------------------------------------------------
    
    def get_limit_switches(self, cache=True, propagate=1):
        self.get_state(cache=cache, propagate=propagate)
        return self._limit_switches
    
    def set_limit_switches(self, ls, propagate=1):
        self._set_limit_switches(ls, propagate=propagate)
    
    def _set_limit_switches(self, ls, propagate=1):
        self._limit_switches = tuple(ls)
        if not propagate:
            return
        if ls == self._limit_switches_event:
            # current ls is equal to last ls_event. Skip event
            return
        self._limit_switches_event = ls
        self.fire_event(EventType("limit_switches", priority=propagate), ls)
    
    limit_switches = property(get_limit_switches, set_limit_switches,
                              doc="motor limit_switches")
    
    # --------------------------------------------------------------------------
    # backlash
    # --------------------------------------------------------------------------
    
    def has_backlash(self, cache=True):
        return self._backlash != 0

    def is_backlash_positive(self, cache=True):
        return self._backlash > 0

    def is_backlash_negative(self, cache=True):
        return self._backlash < 0

    def get_backlash(self, cache=True):
        return self._backlash
    
    def set_backlash(self, backlash, propagate=1):
        self._backlash = backlash
        self.fire_event(EventType("backlash", priority=propagate), backlash)
    
    backlash = property(get_backlash, set_backlash, doc="motor backlash")
    
    # --------------------------------------------------------------------------
    # offset
    # --------------------------------------------------------------------------
    
    def get_offset(self, cache=True):
        return self._offset
    
    def set_offset(self, offset, propagate=1):
        self._offset = offset
        self.fire_event(EventType("offset", priority=propagate), offset)
        # recalculate position and send event
        self._position = self.sign * self.dial_position + offset
        self.fire_event(EventType("position", priority=propagate), self._position)
    
    offset = property(get_offset, set_offset, doc="motor offset")
    
    # --------------------------------------------------------------------------
    # sign
    # --------------------------------------------------------------------------
    
    def get_sign(self, cache=True):
        return self._sign
    
    def set_sign(self, sign, propagate=1):
        self._sign = sign
        if propagate:
            self.fire_event(EventType("sign", priority=propagate), sign)
        # recalculate position and send event
        self._position = sign * self.dial_position + self.offset
        if propagate:
            self.fire_event(EventType("position", priority=propagate), self._position)
        # invert lower with upper limit switches and send event in case of change
        ls = self._limit_switches
        if ls is not None:
            self._set_limit_switches((ls[0],ls[2],ls[1]), propagate=propagate)
        
    sign = property(get_sign, set_sign, doc="motor sign")
    
    # --------------------------------------------------------------------------
    # step per unit
    # --------------------------------------------------------------------------
    
    def get_step_per_unit(self, cache=True, propagate=1):
        if not cache or self._step_per_unit is None:
            step_per_unit = self.read_step_per_unit()
            self._set_step_per_unit(step_per_unit, propagate=propagate)
        return self._step_per_unit
    
    def set_step_per_unit(self, step_per_unit, propagate=1):
        self.controller.ctrl.SetPar(self.axis, "step_per_unit", step_per_unit)
        self._set_step_per_unit(step_per_unit, propagate=propagate)
    
    def _set_step_per_unit(self, step_per_unit, propagate=1):
        self._step_per_unit = step_per_unit
        if propagate:
            self.fire_event(EventType("step_per_unit", priority=propagate), step_per_unit)
            # force ask controller for new position to send priority event
            self.get_position(cache=False, propagate=2)
    
    def read_step_per_unit(self):
        return self.controller.ctrl.GetPar(self.axis, "step_per_unit")
    
    step_per_unit = property(get_step_per_unit, set_step_per_unit,
                             doc="motor steps per unit")
                            
    # --------------------------------------------------------------------------
    # acceleration
    # --------------------------------------------------------------------------
    
    def get_acceleration(self, cache=True, propagate=1):
        if not cache or self._acceleration is None:
            acceleration = self.read_acceleration()
            self._set_acceleration(acceleration, propagate=propagate)
        return self._acceleration
    
    def set_acceleration(self, acceleration, propagate=1):
        self.controller.ctrl.SetPar(self.axis, "acceleration", acceleration)
        self._set_acceleration(acceleration, propagate=propagate)
    
    def _set_acceleration(self, acceleration, propagate=1):
        self._acceleration = acceleration
        if not propagate:
            return
        self.fire_event(EventType("acceleration", priority=propagate), acceleration)
    
    def read_acceleration(self):
        return self.controller.ctrl.GetPar(self.axis, "acceleration")
    
    acceleration = property(get_acceleration, set_acceleration,
                            doc="motor acceleration")
    
    # --------------------------------------------------------------------------
    # deceleration
    # --------------------------------------------------------------------------
    
    def get_deceleration(self, cache=True, propagate=1):
        if not cache or self._deceleration is None:
            deceleration = self.read_deceleration()
            self._set_deceleration(deceleration, propagate=propagate)
        return self._deceleration
    
    def set_deceleration(self, deceleration, propagate=1):
        self.controller.ctrl.SetPar(self.axis, "deceleration", deceleration)
        self._set_deceleration(deceleration, propagate=propagate)
    
    def _set_deceleration(self, deceleration, propagate=1):
        self._deceleration = deceleration
        if not propagate:
            return
        self.fire_event(EventType("deceleration", priority=propagate), deceleration)
    
    def read_deceleration(self):
        return self.controller.ctrl.GetPar(self.axis, "deceleration")
    
    deceleration = property(get_deceleration, set_deceleration,
                            doc="motor deceleration")
    # --------------------------------------------------------------------------
    # base_rate
    # --------------------------------------------------------------------------
    
    def get_base_rate(self, cache=True, propagate=1):
        if not cache or self._base_rate is None:
            base_rate = self.read_base_rate()
            self._set_base_rate(base_rate, propagate=propagate)
        return self._base_rate
    
    def set_base_rate(self, base_rate, propagate=1):
        self.controller.ctrl.SetPar(self.axis, "base_rate", base_rate)
        self._set_base_rate(base_rate, propagate=propagate)
    
    def _set_base_rate(self, base_rate, propagate=1):
        self._base_rate = base_rate
        if not propagate:
            return
        self.fire_event(EventType("base_rate", priority=propagate), base_rate)
    
    def read_base_rate(self):
        return self.controller.ctrl.GetPar(self.axis, "base_rate")
    
    base_rate = property(get_base_rate, set_base_rate,
                         doc="motor base rate")
    
    # --------------------------------------------------------------------------
    # velocity
    # --------------------------------------------------------------------------
    
    def get_velocity(self, cache=True, propagate=1):
        if not cache or self._velocity is None:
            velocity = self.read_velocity()
            self._set_velocity(velocity, propagate=propagate)
        return self._velocity
    
    def set_velocity(self, velocity, propagate=1):
        self.controller.ctrl.SetPar(self.axis, "velocity", velocity)
        self._set_velocity(velocity, propagate=propagate)
    
    def _set_velocity(self, velocity, propagate=1):
        self._velocity = velocity
        if not propagate:
            return
        self.fire_event(EventType("velocity", priority=propagate), velocity)
    
    def read_velocity(self):
        return self.controller.ctrl.GetPar(self.axis, "velocity")
    
    velocity = property(get_velocity, set_velocity,
                        doc="motor velocity")
    
    # --------------------------------------------------------------------------
    # position & dial position
    # --------------------------------------------------------------------------
    
    def get_position(self, cache=True, propagate=1):
        if not cache or self._position is None:
            dial_position = self.read_dial_position()
            self._set_dial_position(dial_position, propagate=propagate)
        return self._position
    
    def set_position(self, position):
        self._wposition = position
        self.start_move(position)
    
    def put_position(self, position, propagate=1):
        self._set_position(position, propagate=propagate)
    
    def _set_position(self, position, propagate=1):
        dial_position = (position - self._offset) / self._sign
        self._set_dial_position(dial_position, propagate=propagate)
        
    def read_dial_position(self):
        return self.motion.read_dial_position()[self]
    
    def put_dial_position(self, dial_position, propagate=1):
        self._set_dial_position(dial_position, propagate=propagate)
    
    def get_dial_position(self, cache=True, propagate=1):
        if not cache or self._dial_position is None:
            dial_position = self.read_dial_position()
            self._set_dial_position(dial_position, propagate=propagate)
        return self._dial_position

    def _set_dial_position(self, dial_position, propagate=1):
        self._dial_position = dial_position
        self._position = self.sign * dial_position + self.offset

        if not propagate:
            return
        self.fire_event(EventType("dial_position", priority=propagate), dial_position)
        self.fire_event(EventType("position", priority=propagate), self._position)
    
    position = property(get_position, set_position, doc="motor user position")
    dial_position = property(get_dial_position, doc="motor dial position")
    
    # --------------------------------------------------------------------------
    # motion
    # --------------------------------------------------------------------------

    def get_motion(self):
        return self.get_action_cache()
    
    motion = property(get_motion, doc="motion object")

    # --------------------------------------------------------------------------
    # motion calculation
    # --------------------------------------------------------------------------
    
    def _calculate_move(self, new_position):
        old_position = self.position
        old_dial = self.dial_position
        
        ctrl = self.controller
        
        # compute dial position
        dial_pos = (new_position - self.offset) / self.sign
        
        # add backlash if necessary
        do_backlash = False
        displacement = dial_pos - old_dial
        if self.has_backlash() and \
           math.fabs(displacement) > pool.EpsilonError and \
           not ctrl.has_backlash():
           
            positive_displacement = displacement > 0
            positive_backlash = self.is_backlash_positive()
            do_backlash = positive_backlash != positive_displacement
            if do_backlash:
                dial_pos = dial_pos - self._backlash / self._step_per_unit
        
        # compute a rounding value if necessary
        if ctrl.wants_rounding():
            nb_step  = round(dial_pos * self._step_per_unit)
            dial_pos = nb_step / self._step_per_unit
        
        backlash_position = dial_pos
        if do_backlash:
            backlash_position = dial_pos + self._backlash / self._step_per_unit
        
        return new_position, dial_pos, do_backlash, backlash_position
    
    def start_move(self, new_position):
        self._aborted = False
        pos, dial, do_backlash, dial_backlash = self._calculate_move(new_position)
        if not self._simulation_mode:
            items = { self : (pos, dial, do_backlash, dial_backlash) }
            self.motion.run(items=items)
    
