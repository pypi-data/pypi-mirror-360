class Exceptions(Exception,):
    measures = ['NA', 'span', 'width']
    myUnits = {}
    layers = {}
    geometry = {}
    width = {}
    thickness = {}
    material = {}
    EG = {}
    results = {}
    y = {}
    a = {}
    z = {}
    span = {}
    loads = {}
    mass = {}
    check = {}
    wall = {}
    def __int__(self):
        Exceptions.__int__(self)

    def __str__(self):
        return 'ALL Exceptions'

    def is_valid(self,
                 numberCheck=False,
                 widthCheck=False,
                 materialCheck=False,
                 thicknessEntriesCheck=False,
                 thicknessEntries=None,
                 thicknessExistsCheck=False,
                 loadExistsCheck=False,
                 spanExistsCheck=False,
                 massExistsCheck=False,
                 resultsExistsCheck=False,

                 ):
        if numberCheck:
            if 'layers' not in self.results.keys():
                raise KeyError('Your CLT PANEL object must be set with object.add_layer(int) method')
        if widthCheck:
            if 'width' not in self.geometry.keys():
                raise KeyError('Your CLT PANEL object must be set with object.add_width(int or float) method')
        if materialCheck:
            if 'E' not in self.material.keys():
                raise KeyError('Your CLT PANEL object must be set with object.add_defined_material(str) method')
        if thicknessEntriesCheck:
            if not len(thicknessEntries) == self.layers['layers']:
                m = self.layers['layers']
                raise ValueError(
                    f'Your CLT PANEL was added {m} Layer, but Entered {len(thicknessEntries)} thickness layer')
        if thicknessExistsCheck:
            if 'tk_1' not in self.thickness.keys():
                raise KeyError('Your CLT PANEL object must be set with object.add_thickness(int) method')
        if massExistsCheck:
            if 'mass' not in self.geometry.keys():
                raise KeyError('Your CLT PANEL object must be set with object.mass(int) method')

        if spanExistsCheck:
            if 'span' not in self.geometry.keys():
                raise KeyError('Your CLT PANEL object must be set with object.span(int) method')

        if loadExistsCheck:
            if 'Q' not in self.loads.keys() or 'G' not in self.loads.keys():
                raise KeyError('Your CLT PANEL object must be set with object.load(int) method')

        if resultsExistsCheck:
            if 'M_y' not in self.results.keys() or 'V_y' not in self.results.keys():
                raise KeyError('Your CLT PANEL object must be set with object.My or Vy(int) method')
