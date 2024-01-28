import sys
import csv
from itertools import groupby

def csv_to_dict(file_path: str) -> list[dict[str,str]]:
    result = []
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            result.append(row)
    return result

args = sys.argv

encounter_file = 'encounters.csv'

output_location = 'encounters.txt'

# if len(args) > 0:
#     encounter_file = args[0]
#     if len(args) > 1:
#         output_location = args[1]

class Encounter():
    def __init__(self, species: str, rate: int,lower_lvl: int, upper_lvl: int):
        if lower_lvl > upper_lvl:
            raise Exception(f'Lower level {lower_lvl} > Upper level {upper_lvl} for {species}')
        self.species = species
        self.rate = rate
        self.lower_lvl = lower_lvl
        self.upper_lvl = upper_lvl
    
    def generate_pbs(self):
        return f"    {self.rate},{self.species},{self.lower_lvl},{self.upper_lvl}"

class EncounterType():
    def __init__(self, e_type: str, rate: int):
        self.e_type = e_type
        self.rate = rate
        self.encounters: list[Encounter] = []
    
    def process_encounters(self, data: list[dict[str,str]]):
        for enc_data in data:
            levels = enc_data['Level'].split('-')
            self.encounters.append(
                Encounter(lower_lvl= int(levels[0]),
                          upper_lvl= int(levels[1]),
                          rate= enc_data['Rate'],
                          species= enc_data['Pokemon']
                          )
            )
    def generate_pbs(self):
        e_pbs = [e.generate_pbs() for e in self.encounters]
        e_pbs = '\n'.join(e_pbs)
        head = f"{self.e_type}" if self.rate in [None,'',0] else f"{self.e_type},{self.rate}"
        return f"{head}\n" + e_pbs

class EncounterLocation():
    def __init__(self, location_id: str, location_name: str):
        self.location_id = location_id
        self.location_name = location_name
        self.encounter_types: list[EncounterType] = []
        """"""
    
    def process_encounter_types(self,data: list[dict]):
        grouped_encounter_types = groupby(data, key=lambda x: x['Type'])
        for e_type, e_data in grouped_encounter_types:
            e_data = list(e_data)
            overall_rate = e_data[0]['Overall Rate']
            encounter_type = EncounterType(e_type= e_type, rate= overall_rate)
            encounter_type.process_encounters(e_data)
            self.encounter_types.append(encounter_type)
    
    def generate_pbs(self):
        e_type_pbs = [et.generate_pbs() for et in self.encounter_types]
        e_type_pbs = '\n'.join(e_type_pbs)
        return f"[{self.location_id}] # {self.location_name}\n{e_type_pbs}\n#-------------------------------"

encounter_locations: list[EncounterLocation] = []
raw_data = csv_to_dict(file_path= encounter_file)

grouped_locations = groupby(raw_data, key=lambda x: x['Location Id'])

for location_code, location_data in grouped_locations:
    location_data = list(location_data)
    encounter_location = EncounterLocation(location_id=location_code, location_name= location_data[0]['Location'])
    encounter_location.process_encounter_types(location_data)
    encounter_locations.append(encounter_location)
# print(encounter_locations)
pbs_locations = [loc.generate_pbs() for loc in encounter_locations]

with open(output_location, 'w') as file:
    # Write the string to the file
    file.write('\n'.join(pbs_locations))
print(f'Generated file for {len(pbs_locations)} at {output_location}')
# sample
"""
[002] # Lappet Town
Water,2
    60,TENTACOOL,14,19
    30,MANTYKE,15,16
    10,REMORAID,14,16
OldRod
    100,MAGIKARP,16,19
GoodRod
    60,BARBOACH,17,18
    20,KRABBY,15,16
    20,SHELLDER,16,19
SuperRod
    40,CHINCHOU,17,19
    40,QWILFISH,16,19
    15,CORSOLA,15,18
    5,STARYU,15,17
#-------------------------------
[005] # Route 1
Land,21
    40,PIDGEY,11,14
    40,RATTATA,11,14
    9,PIDGEY,11,13
    9,RATTATA,11,13
    1,PIDGEY,14
    1,RATTATA,14
LandNight,21
    39,RATTATA,10,14
    30,HOOTHOOT,10,13
    20,SPINARAK,8,12
    9,HOOTHOOT,10,14
    1,HOOTHOOT,14
    1,RATTATA,15
"""
