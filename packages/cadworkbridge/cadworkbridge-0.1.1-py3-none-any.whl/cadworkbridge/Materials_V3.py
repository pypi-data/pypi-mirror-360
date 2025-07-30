"""
mass :The mass of an object is the same everywhere. Weight:  Weight depends on the effect of gravity(W=m∗g)
Density : Kg/m3  - multiply density by volume to get mass
E : Elasticity : GPa
Strength MPa(*10=Kg/cm2) : Material  - Resistance : civil engineering Material
Pa :N/m2 , MPa :N/mm2 GPa:KN/mm2
Kg = kg * g = N
floor : 500 kg/m2 , 5 KN/m2 ,0.5 Ton/m2
"""


class Materials:
    defiendMaterials = [
        {'radiata': {'species': 'radiata_pine', 'grade': 'building', 'fb': 33.9, 'fc': 28.6, 'ft': 20.3, 'fs': 4.1,
                     'fp': 9.4, 'E': 12, 'G': 0.8, 'Density': 500}},
        {'douglas': {'species': 'douglas_fir', 'grade': 'building', 'fb': 33, 'fc': 30.1, 'ft': 19.8, 'fs': 3.2,
                     'fp': 9.7, 'E': 12, 'G': 0.8, 'Density': 500}},
        {'steel': {'Density': 7850, 'E': 320, 'strength': 240}},
        {'concrete': {'Density': 2500, 'E': 25, 'strength': 25, 'grade': 350}},

    ]
    material = {}
    results = {}

    def __int__(self):
        pass

    def add_defined_material(self, materialName: str):
        found = False
        for material in self.defiendMaterials:
            for key, value in material.items():
                if key == materialName:
                    # self.material = value
                    self.results.update({'material': value})
                    print(f'material is set with {key}')
                    found = True
                    break
        if not found:
            print("No stores were found.")

    def add_new_material(self, species: str, grade: str, fb: float,
                         fc: float, ft: float, fs: float, fp: float, E: int, G: int):
        self.results.update({'material': {'species': species,
                                          'grade': grade,
                                          'fb': fb,
                                          'fc': fc,
                                          'ft': ft,
                                          'fs': fs,
                                          'fp': fp,
                                          'E': E,
                                          'G': G
                                          }})
