#file: item.py
#Copyright (C) 2005,2006,2008 Evil Mr Henry, Phil Bordelon, and FunnyMan3595
#This file is part of Endgame: Singularity.

#Endgame: Singularity is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#Endgame: Singularity is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Endgame: Singularity; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#This file contains the item class.

import buyable
import g

class ItemType(object):
    """ Item type, 4 fixed instances: cpu, reactor, network and security """
    def __init__(self, id, **kwargs):

        # Either cpu, reactor, network or security
        self.id   = id

        # Text is language-dependent data, thus ideally it should not be passed
        # to the constructor, so label, hotkey and pos are created with default
        # (blank) values. When language changes, update data with text.setter
        self.text = kwargs.pop("text", id)

        #TODO: Extend this class so eventually item_type attribute of Item and
        # ItemClass classes can be an instance of this, instead of a string.
        # Maybe a new "item" attribute and leave item_type alone until all
        # methods are converted. Be careful with interface to Buyable
        # Useful attributes would be:
        # - iscpu (Boolean, so no more type == 'cpu' testing)
        # - extra_item_index (Integer, so no more relying on list order)
        # - desc_text - for item_qual bonus description in knowledge screen

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        # Updates language-dependent data
        try:
            hotkey = g.hotkey(value)
        except AttributeError:
            # g.hotkey() wasn't declared yet, mimic its defaults
            hotkey = dict(text= value,
                          key = value[0:1],
                          pos = 0,)
        self._text  = value
        self.label  = hotkey['text'] # "Friendly" name for screens and buttons
        self.hotkey = hotkey['key']  # Hotkey char
        self.pos    = hotkey['pos']  # Hotkey index in Label

    def __repr__(self):
        return self.id

# TODO: Deharcode ItemType

cpu_type = "cpu"
reactor_type = "reactor"
network_type = "network"
security_type = "security"

# Order IS NOT relevant!
# Because the ugly extra_items are gone and I am happy. :)))
item_types = [
    ItemType(cpu_type),
    ItemType(reactor_type),
    ItemType(network_type),
    ItemType(security_type),
]

def all_types():
    for item_type in item_types:
        yield item_type

class ItemClass(buyable.BuyableClass):
    """ Item as a buyable item (CPUs, Reactors, Network and Security items) """

    def __init__(self, name, description, cost, prerequisites, item_type,
            item_qual, buildable):
        super(ItemClass, self).__init__(name, description, cost, prerequisites,
                                         type="item")

        self.item_type = item_type
        self.item_qual = item_qual
        self.regions = buildable

    def get_info(self):
        basic_text = super(ItemClass, self).get_info()
        if self.item_type == cpu_type:
            return basic_text.replace("---", _("Generates {0} CPU.",
                                               g.add_commas(self.item_qual)) + \
                                      "\n---")
        return basic_text

    def get_quality_for(self, quality):
        
        # TODO: Deharcode quality to item type.
        
        if (quality == "cpu" and self.item_type == cpu_type) or \
           (quality == "cpu_modifier" and self.item_type == network_type) or \
           (quality == "discover_modifier" and (self.item_type == reactor_type or \
                                                self.item_type == security_type)):
            return self.item_qual
        
        return 0

    def get_quality_info(self):
        bonus_text = ""
        
        if self.item_type == cpu_type:
            bonus_text += _("CPU per day:")+" "
            bonus_text += g.add_commas(self.item_qual)
        elif self.item_type == reactor_type:
            bonus_text += _("Detection chance reduction:")+" "
            bonus_text += g.to_percent(self.item_qual)
        elif self.item_type == network_type:
            bonus_text += _("CPU bonus:")+" "
            bonus_text += g.to_percent(self.item_qual)
        elif self.item_type == security_type:
            bonus_text += _("Detection chance reduction:")+" "
            bonus_text += g.to_percent(self.item_qual)

        return bonus_text

class Item(buyable.Buyable):
    """ An installed Item in a Player's Base """

    def __init__(self, item_type, base=None, count=1):
        super(Item, self).__init__(item_type, count)
        self.item_qual = item_type.item_qual
        self.base = base

    def convert_from(self, load_version):
        super(Item, self).convert_from(load_version)
        if load_version < 4.91: # < r5_pre
            self.type = g.items[self.type.id]

    def get_quality_for(self, quality):
        item_qual = self.type.get_quality_for(quality)
        
        # Modifiers are not affected by count.
        # TODO: Allow modifiers to be multiplied by count. Need a custom function.
        if quality.endswith("_modifier"):
            return item_qual
            
        return item_qual * self.count

    def finish(self):
        super(Item, self).finish()
        if self.base:
            self.base.recalc_cpu()

    def __iadd__(self, other):
        if isinstance(other, Item) and self.base == other.base \
                and self.type == other.type:
            if other.count == 0:
                return self

            # Calculate what's been paid and what is left to be paid.
            total_cost_paid = self.cost_paid + other.cost_paid
            self.total_cost += other.total_cost

            # Labor takes as long as the less complete item would need.
            total_cost_paid[buyable.labor] = min(self.cost_paid[buyable.labor],
                                                 other.cost_paid[buyable.labor])
            self.total_cost[buyable.labor] = other.total_cost[buyable.labor]

            # Set what we've paid (and hence what we have left to pay).
            self.cost_paid = total_cost_paid

            # Increase the size of this stack.
            self.count += other.count

            # Tell the base it has no CPU for now.
            self.base.raw_cpu = 0
            self.base.recalc_cpu

            # See if we're done or not.
            self.done = False
            self.work_on(0, 0, 0)

            return self
        else:
            return NotImplemented
