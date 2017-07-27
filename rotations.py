# classes and combos
from rotation import Rotation
from conqueror.combos import *
from conqueror.abilities import *
from guardian.combos import *
from guardian.abilities import *


## Guardian Aggro Rotation
def Guardian_Aggro():
    guard_aggro = Rotation()
    guard_aggro.repeat = False
    guard_aggro.repeat_count = 2

    # Combos
    guard_aggro.use( ShieldSlam() ).at( 1, 5, 9, 13, 18, 20 )
    guard_aggro.use( GuardDestroyer(4) ).at( 2, 12 )

    t_smash_buffs = TitanicSmash()
    t_smash_buffs.attach_prefinishers( (Powerhouse(), BattleCry(), CallToArms()) )
    t_smash_buffs.name += " (Buffs)"
    t_smash_buffs = guard_aggro.use( t_smash_buffs ).at( 3 )

    guard_aggro.use( TitanicSmash() ).at( 10, 17 )
    guard_aggro.use( DullingBlow() ).at( 8, 16 )
    guard_aggro.use( Overreach(5) ).at( 4, 7, 9, 14 )
    guard_aggro.use( Overreach(6) ).at( 6, 11, 15, 19 )

    # Abilities
    guard_aggro.use( TacticProvoke() ).at( 1 )
    guard_aggro.use( CryOfHavoc() ).at( 3 )
    guard_aggro.use( Irritate() ).at( 2 )
    guard_aggro.use( BloodyVengeance() ).at( 19 )

    return guard_aggro


def Guardian_DPS():
    ## Guard DPS Rotation
    rot = Rotation()

    # Combos
    rot.use( GuardDestroyer(4) ).at( 1, 10 )

    t_smash_buffs = TitanicSmash()
    t_smash_buffs.attach_prefinishers( (Powerhouse(), BattleCry(), CallToArms()) )
    t_smash_buffs.name = t_smash_buffs.name + " (Buffs)"
    t_smash_buffs = rot.use( t_smash_buffs ).at( 2, 20 )

    rot.use( TitanicSmash() ).at( 7, 13 )
    rot.use( Counterweight() ).at( 3, 5, 8, 11, 14, 17 )
    rot.use( Overreach(6) ).at( 4, 6, 15 )
    rot.use( Overreach(5) ).at( 12, 16, 18 )
    rot.use( DullingBlow() ).at( 9, 19 )

    # Abilities
    rot.use( BloodyVengeance() ).at( 4, 11 )
    rot.use( Reckoning() ).at( 4, 6, 9, 12, 15, 18 )
    #rot.use( switch_weapons, (19,))

    return rot


def Conqueror_DPS():
    ## Conqueror DPS Rotation
    conq_dps = Rotation()
    conq_dps.repeat = True
    conq_dps.repeat_count = 2

    # Combos
    conq_dps.use( Breech(4) ).at( 1 )
    conq_dps.use( Whirlwind() ).at( 2, 6, 10 )
    conq_dps.use( BloodyHack(6) ).at( 3, 11 )
    conq_dps.use( BloodyHack(5) ).at( 5, 7, 9 )
    conq_dps.use( Bloodbath(6) ).at( 4, 8, )

    # Abilities
    #conq_dps.use( BladeWeave() ).at( 1 )
    #conq_dps.use( UseDiscipline() ).at( 2 )
    conq_dps.use( Annihilate() ).at( 3 )
    conq_dps.use( RendFlesh() ).at( 4 )

    return conq_dps
