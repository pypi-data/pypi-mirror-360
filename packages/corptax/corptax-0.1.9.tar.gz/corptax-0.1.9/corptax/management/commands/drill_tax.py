import logging
import csv
from pprint import pprint
import operator as op
from inspect import getmembers, isfunction

from django.core.management.base import BaseCommand
from django.conf import settings

from eveuniverse.models import EveType, EveTypeMaterial, EveMarketPrice, EveMoon, EvePlanet, EveSolarSystem, EveConstellation, EveRegion
from moonmining.models import Moon, MoonProduct
from structures.models import Structure, StructureTag

logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Generate Moon Drill Rental'
    def handle(self, *args, **options):
        print(f'Starting Moon Rental calculation')
        csv_filename = "/tmp/total_moon_value_without_minerals.csv"
        moons = Moon.objects.all()
        report = []
        for moon in moons:
            moon_location = EveMoon.objects.get(id=moon.eve_moon_id)
            eve_planet = EvePlanet.objects.get(id=moon_location.eve_planet_id)
            moon_system = EveSolarSystem.objects.get(id=eve_planet.eve_solar_system_id)
            moon_constellation = EveConstellation.objects.get(id=moon_system.eve_constellation_id)
            moon_region = EveRegion.objects.get(id=moon_constellation.eve_region_id)
            moon_product = MoonProduct.objects.filter(moon_id=moon.eve_moon_id)
            if moon_region.name != "Placid":
                print(moon_region.name)
                continue
            total_moon_value = 0
            material_output = ""
            for x in moon_product:
                # 21888000 = 30.000(per hour) * 24 (hours) * 30.4 (days)
                ore_output_volume = 21888000 * x.amount
                ore_output = ore_output_volume / 10
                ore_material = EveTypeMaterial.objects.filter(eve_type=x.ore_type_id)
                moon =  Moon.objects.get(eve_moon_id=moon.eve_moon_id)
                for y in ore_material:
                    ore_material_value = 0
                    material_type = EveType.objects.get(id=y.material_eve_type_id)
                    if material_type.eve_group_id not in [427]:
                        continue
                    total_minerales = ore_output * y.quantity / 100
                    input_mats_name = str(EveType.objects.get(id=y.material_eve_type_id))
                    price = EveMarketPrice.objects.get(eve_type=y.material_eve_type_id)
                    ore_material_value = total_minerales * price.average_price
                    total_moon_value = total_moon_value + ore_material_value
                    material_output = material_output + " / " + str(input_mats_name)
                    #print(input_mats_name, round(total_minerales))
            total_value = round(total_moon_value)
            razo_tax_total = round(total_moon_value * 0.05)
            edge_tax_total = round(total_moon_value * 0.1)
            drill_value = round(total_value * 0.4)
            print(f'{moon_region.name} / {str(moon.name)} / {str(moon.name)} Tax: {total_moon_value}')
            report_dict = {"Constalation": str(moon_system.eve_constellation),"System": str(moon_system.name), 
                           "Moon": str(moon.name), "Rarity Class": moon.rarity_class, 
                           "Total Value": total_value, "Drill value": drill_value, "Razor Tax": razo_tax_total,
                           "EDGE Tax": edge_tax_total, "Material": material_output
            }
            report.append(report_dict)

        fields = ['Constalation', 'System', 'Moon','Rarity Class' ,'Total Value', 'Drill value', 'Razor Tax', 'EDGE Tax', 'Material']
        with open(csv_filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=fields, dialect='excel')
            writer.writeheader()
            writer.writerows(report)


