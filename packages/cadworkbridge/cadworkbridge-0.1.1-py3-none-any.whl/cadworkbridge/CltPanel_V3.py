import numpy as np
import pandas as pd
import math
from Materials_V3 import Materials
from Exceptions_V3 import Exceptions
from Loading_V3 import Loading
import json

"""
Goals : 
    1 - Omit Dictionary
    2 - Return Dictionary ,Context/Json
    3 - Using Arrays/Pandas
    4 - Exceptions
    5 - Units
    6 - Add Beams


neutral axis : NA : EAY/EA  - AY: First Moment Of Inertia
C : Far AXIS
I = Moment Of Inertia E*bh3/12 + az^2 mm4 =>E*I
EI : effective bending stiffness(I) of the panel for the major strength axis
S = I/C the section modulus in the major direction (EI/E)/NA mm3
Factors : 
    -loadDurationFactor: Load Duration Factor Kd - Default : 1
    -serviceConditionFactor: Service Condition Factor Ks - Default : 1
    -treatmentFactor: Treatment Factor Kt - Default : 1
    -systemFactor: System Factor Kh - Default : 1
    
-Moment-
Element Resistance : fb(radiata moment strength) * S(section) * Resistance Factor * Strength Reduction Factors(Kd...)
Element Force Moment using G and Q = L2/8   Force(Q,G,V) --> Action(moment,shear)
-Shear-
fv(radiata shear strength)
V =  3/2 fv/A (Rectangular Section)

---------------------------
stress = F/A
Deflection : Need EI ,GA , Weight
    - 5WL^4/384EI + kWL2/8(GA)<=L/300
Vibration :  Need EI ,Mass
    - 𝐿 ≤ 0.11(EI/10^6 )^0.29/Mass^0.12
"""


class CLT(Materials, Exceptions, Loading):
    """Floor CLt PANEL CALCULATION is the main class of cross-wood package"""
    results = {}
    wall = {}

    def __init__(self):
        """This Class calculate CLT FLOOR PANEL"""
        Materials.__init__(self)
        Exceptions.__init__(self)
        Loading.__init__(self)

    def __str__(self):
        return self.results

    def add_layer(self, number: int):
        self.results.clear()
        self.results.update({'layers': number})

    def add_thickness(self, *args):
        self.is_valid(numberCheck=True)
        self.results.update({'geometry': {'width': 1000}})
        width = self.results['geometry']['width']
        self.results.update({'thickness': args})
        tk, eay, ea, e, g, a, y, z, ei = [], [], [], [], [], [], [], [], []
        tk = args
        status = True
        for i in range(0, self.results['layers']):
            a.append(tk[i] * width)
            y.append(tk[i] / 2 + sum(self.results['thickness'][:i]))
            if status is True:
                e.append(self.results['material']['E'])
                g.append(self.results['material']['G'])
                status = False
            else:
                e.append(self.results['material']['E'] / 15)
                g.append(self.results['material']['E'] / 16)
                status = True
            eay.append(e[i] * a[i] * y[i])
            ea.append(e[i] * a[i])
        self.results.update({'H': sum(args)})
        self.results.update({'a': a})
        self.results.update({'Ag': sum(a)})
        self.results.update({'y': y})
        self.results.update({'E': e})
        self.results.update({'G': g})
        na = sum(eay) / sum(ea)
        self.results.update({'NA': na})
        for i in range(0, self.results['layers']):
            z.append(abs(self.results['NA'] - y[i]))
            ei.append(e[i] * width * args[i] ** 3 / 12 + a[i] * z[i] ** 2)
        self.results.update({'z': z})
        self.results.update({'EI': round(sum(ei), 2)})
        # PANDAS
        index = range(1, len(args) + 1)
        data = {'tk': tk, 'E': e, 'G': g, 'A': a, 'Y': y, 'EAY': eay, 'EA': ea, 'Z': z, }
        df = pd.DataFrame(index=index, data=data, )
        ea = df.sum(axis='index')['EA']
        # print(df)
        # print(f"EA  is  : {ea}")
        # print(df.loc[df.tk == 42, 'Y'], 'nist')

    def floor_calculation(self, resistanceFactor=0.9,
                          strengthModificationFactor=0.85,
                          loadDurationFactor=1,
                          serviceConditionFactor=1,
                          treatmentFactor=1,
                          systemFactor=1,
                          ):
        width = self.results['geometry']['width']
        # Moment
        s = (self.results['EI'] / self.results['material']['E']) / self.results['NA']
        f_b = self.results['material']['fb'] * (
                loadDurationFactor * serviceConditionFactor * treatmentFactor * systemFactor)
        m_y = resistanceFactor * f_b * s * strengthModificationFactor
        self.results.update({'Fb': round(f_b, 2), 'S': round(s, 2), 'M': round(m_y, 2)})
        # Vy :Flat-wise Shear Resistance
        shear = []
        val = 0
        for i in range(1, len(self.results['thickness'])):
            val += self.results['thickness'][i] / self.results['G'][i] * width
        shear.append(self.results['H'])
        shear.append(self.results['thickness'][0])
        shear.append(self.results['thickness'][len(self.results['thickness']) - 1])
        shear.append(shear[1] / self.results['G'][0] * width)
        shear.append(shear[2] / self.results['G'][len(self.results['G']) - 1] * width)
        shear.append(val)
        ga = (shear[0] - shear[1] / 2 + shear[2] / 2) ** 2 / (shear[3] + shear[4] + shear[5])
        fs = self.results['material']['fs']
        f_s = fs * loadDurationFactor * serviceConditionFactor * treatmentFactor * systemFactor
        v = resistanceFactor * f_s * 2 * self.results['Ag'] / 3
        self.results.update({'GA': round(ga, 2), 'Fs': f_s, 'V': round(v, 2)})

    def wall_calculation(self, *args, **kwargs):
        width = self.results['geometry']['width']
        e = self.results['material']['E']
        ei = self.results['EI']
        l_eff = self.results['geometry']['length']
        f_c = self.results['material']['fc']
        i_eff = ei / e
        h, a = [], []
        for layer in args:
            h.append(self.results['thickness'][layer - 1])
            a.append(self.results['thickness'][layer - 1] * width)
        a = sum(a)
        r_eff = math.sqrt(i_eff / a)
        c_c = l_eff / (math.sqrt(12) * r_eff)
        k_zc = 6.3 * (2 * math.sqrt(3) * r_eff * l_eff) ** -.13
        k_se = 1
        k_t = 1
        k_c = (1 + (f_c * k_zc * c_c ** 3) / (35 * e * k_se * k_t)) ** -1
        p = 0.8 * f_c * a * k_zc * k_c
        self.results.update({'wall': {'H_eff': sum(h),
                                      'A_eff': a,
                                      'I_eff': i_eff,
                                      'r_eff': r_eff,
                                      'C_c': c_c,
                                      'k_zc': k_zc,
                                      'k_c': k_c,
                                      'P': p
                                      }})

    def Deflection(self):
        length = self.results['geometry']['length']
        dead = self.results['loads']['G']
        live = self.results['loads']['Q']
        ei = self.results['EI']
        ga = self.results['GA']
        top = (5 * (dead + live) * length ** 4) / (384 * ei)
        down = ((dead + live) * length ** 2) / (8 * ga)
        deflection = top + down
        self.results.setdefault('Deflection', round(deflection, 2))

    def Vibration(self):
        ei = self.results['EI']
        w = self.results['geometry']['weight']
        h = self.results['H']
        vibration = .11 * (ei / 1000000) ** .29 / ((h / 1000 * w) ** .12)
        self.results.setdefault('Vibration', round(vibration, 2))


clt = CLT()
clt.add_layer(6)
clt.add_defined_material('radiata')
clt.add_new_material(species='radiata', grade='radiata', fb=10, fc=10, ft=10, fs=10, fp=10, E=1000, G=1000)
clt.add_thickness(42, 20, 42, 20, 42, 20)
clt.floor_calculation()
clt.loading(G=1.5, Q=1, width=1983, length=12345, weight=1367)
clt.Deflection()
clt.Vibration()
clt.wall_calculation(1, 3, 5)
print(json.dumps(clt.results, indent=4))
