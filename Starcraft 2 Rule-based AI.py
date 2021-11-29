import random
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
CYBERNETICSCORE, STALKER, STARGATE, VOIDRAY, FORGE, PHOTONCANNON

class FiliBot(sc2.BotAI):
    def __init__(self):
        self.MAX_WORKERS = 65
        self.MAX_WORKERS_PER_NEXUS = 16
        self.STALKER_TO_VOIDRAY_RATIO = 1.2     # x to 1

    async def on_step(self, iteration):
        self.minutes_elapsed = self.time/(60)
        await self.distribute_workers()         # Inherited
        await self.build_workers()              # Built method
        await self.build_pylons()               # Built method
        await self.build_assimilators()         # Build method
        # await self.build_defense()              # Build method
        await self.expand()                     # Build method
        await self.offensive_force_buildings()  # Build method
        await self.build_offensive_force()      # Build method
        await self.attack()                     # Build method

        if self.minutes_elapsed.is_integer():
            print("\n=====================================")
            print(self.minutes_elapsed, "mins")
            print("=====================================\n")
    
    async def build_workers(self):
        # if the defined upper limit of workers per nexus hasn't been reach yet
        # and no. of probes hasn't reached the max no. of workers limit
        # then warp a probe
        if (((len(self.units(NEXUS))+(1 if self.already_pending(NEXUS) == True else 0))
        *self.MAX_WORKERS_PER_NEXUS) > len(self.units(PROBE)) 
        and len(self.units(PROBE)) < self.MAX_WORKERS):
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
                    print("Warping Probe, No.", self.units(PROBE).amount+1)

    async def build_pylons(self):
        # if population left < 5 and not already building Pylon
        # then select the first Nexus and
        # if we can afford to build a Pylon
        # then build one near the first Nexus
        if self.supply_left < 5 and not self.already_pending(PYLON):
            first_nexus = self.units(NEXUS).ready.first
            if self.can_afford(PYLON):
                await self.build(PYLON, near=first_nexus)
                print("Building Pylon, No.", self.units(PYLON).amount+1)
                    
    async def build_assimilators(self):
        # for every built Nexus look for any geyser closer than 25 units from the nexus,
        # add that to a list of geysers 'vespenes'
        for nexus in self.units(NEXUS).ready:
            vespenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            # for every discovered geyser in 'vespenes'
            # if we can't afford to build an Assimilator, then stop checking all discovered geysers
            # grab a worker near the geyser and
            # if there's no assimilator already built close to the vespene
            # use the selected worker to build one
            for vespene in vespenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vespene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                    await self.do(worker.build(ASSIMILATOR, vespene))
                    print("Building Assimilator, No.", self.units(ASSIMILATOR).amount+1)

    async def build_defense(self):
        if self.units(NEXUS).exists:
            nexus = self.units(NEXUS).first
        
        # if Forge doesn't exist, then build one
        # else if Photon Cannon doesn't exist and there are more than 2 Pylons 
        # and can afford Photon Cannon, then build one near selected Pylon
        # else build a Photon Cannon
        if not self.units(FORGE).exists:
            pylon = self.units(PYLON).ready
            if pylon.exists:
                if self.can_afford(FORGE):
                    await self.build(FORGE, near=pylon.closest_to(nexus))
        elif not self.units(PHOTONCANNON).exists:
            if self.units(PYLON).ready.amount >= 2 and self.can_afford(PHOTONCANNON):
                # pylon = self.units(PYLON).closer_than(20, self.enemy_start_locations[0]).random
                pylon = self.units(PYLON).ready.random
                await self.build(PHOTONCANNON, near=pylon)
        else:
            if (self.can_afford(PHOTONCANNON)                                   # ensure "fair" decision
            and not self.units(PHOTONCANNON).amount > int(self.minutes_elapsed/2.5)):  # limiter
                for _ in range(20):
                    # pos = self.enemy_start_locations[0].random_on_distance(random.randrange(5, 12))
                    # building = PHOTONCANNON if self.state.psionic_matrix.covers(pos) else PYLON
                    pylon = self.units(PYLON).ready.random
                    r = await self.build(PHOTONCANNON, near=pylon)
                    if not r: # success
                        break

    async def expand(self):
        # if player has less nexuses than no. of minutes elapsed
        # and can afford to build more, then do so
        if (self.units(NEXUS).amount < self.minutes_elapsed                 # limiter
        and self.can_afford(NEXUS)):
            await self.expand_now()
            print("\n-------------------------------------")
            print("Expanding... Nexus No.", self.units(NEXUS).amount+1)
            print("-------------------------------------\n")

    async def offensive_force_buildings(self):
        # if player has a Pylon, then select any random Pylon
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random

            # if player has a Gateway and player doesn't have a Cyberneticscore yet
            # and player can afford a Cyberneticscore and not already building one,
            # then build one near selected Pylon
            if (self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE) 
            and self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE)):
                await self.build(CYBERNETICSCORE, near=pylon)
                print("Building Cyberneticscore, No.", self.units(CYBERNETICSCORE).amount+1)
            
            # if no. of gateways is < no. of minutes elapsed/2
            # and player can afford a Gateway and not already building one,
            # then build one near selected Pylon
            elif (len(self.units(GATEWAY)) < self.minutes_elapsed / 2       # limiter
            and self.can_afford(GATEWAY) and not self.already_pending(GATEWAY)):
                await self.build(GATEWAY, near=pylon)
                print("Building Gateway, No.", self.units(GATEWAY).amount+1)

            # if player has a Cyberneticscore 
            # and the no. of stargates the player has < minutes elapsed/2
            # and player can afford and not already building
            # then build one near selected Pylon
            if (self.units(CYBERNETICSCORE).ready.exists
            and len(self.units(STARGATE)) < self.minutes_elapsed / 2        # limiter
            and self.can_afford(STARGATE) and not self.already_pending(STARGATE)):
                await self.build(STARGATE, near=pylon)
                print("Building Cyberneticscore, No.", self.units(CYBERNETICSCORE).amount+1)

    async def build_offensive_force(self):
        # for every existing Gateway with no queue
        # if no. of Stalkers * defined ratio is < no. of Void Rays
        # and player can afford a Stalker and and there's room for one more,
        # then train one
        for gw in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.supply_left > 0:
                if self.minutes_elapsed < 6:
                    await self.do(gw.train(STALKER))
                elif (int(self.units(STALKER).amount * self.STALKER_TO_VOIDRAY_RATIO) 
                <= self.units(VOIDRAY).amount):
                    await self.do(gw.train(STALKER))
                    print("Warping STALKER, No.", self.units(STALKER).amount+1)

        # for every existing Stargate with no queue
        # if player can afford a Void Ray and there's room for one more,
        # then train one
        for sg in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(sg.train(VOIDRAY))
                print("Warping Voidray, No.", self.units(VOIDRAY).amount+1)

    def find_target(self, state):
        print("Finding targets...")
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        # {UNIT: [n to fight, n to defend]}
        aggressive_units = {STALKER: [15, 2],
                            VOIDRAY: [8, 2]}

        # if there are enough units to attack then attack
        # else if there are enough units to defend then defend
        for UNIT in aggressive_units:
            if (self.units(UNIT).amount > aggressive_units[UNIT][0]
            and self.units(UNIT).amount > aggressive_units[UNIT][1]):
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))
            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    print("Defending...")
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, FiliBot()),
    Computer(Race.Terran, Difficulty.Hard)
], realtime=False)