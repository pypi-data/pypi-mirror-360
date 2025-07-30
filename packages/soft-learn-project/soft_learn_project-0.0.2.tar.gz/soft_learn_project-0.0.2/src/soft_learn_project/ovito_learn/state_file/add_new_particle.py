# This is a copy of the template file '/Applications/Ovito.app/Contents/Resources/scripts/modifiers/Add new particle type.py'.
# Feel free to modify the code below as needed.

#
# Add new particle type:
#
# A user-defined modifier function that adds a new particle type to the current system.
# This is can be useful if you want to add atoms of a new species to the system, which 
# didn't exist in the input file yet. The modifier displays the numeric ID of the newly
# create atom type in the log window. You can subsequently use OVITO's Compute Property
# modifier to change the value of the 'Particle Type' property of some atoms to the new 
# type ID, for example.
#

from ovito.data import ParticleType

def modify(frame, data, ptype = ParticleType()):
    
    # Make sure the 'Particle Type' property exists.
    ptype_property = data.particles_.create_property('Particle Type')
    
    # Append the ParticleType instance to the types list.
    ptype_property.types.append(ptype)
    
    # Create a mutable copy of the ParticleType, so that we can dynamically change its numeric ID.
    ptype = ptype_property.make_mutable(ptype)
    
    # Pick a unique numeric ID for the new particle type by adding 1 to the largest existing type ID in the system.
    ptype.id = max([t.id for t in ptype_property.types]) + 1
    
    print("Created particle type {}.".format(ptype.id))