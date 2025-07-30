class UnitMixins:
    result = {}
    measures = ['NA', 'span', 'width']
    measuresUnits = ['mm', 'cm', 'm']

    def add_unit(self, myDict: dict, **kwargs):
        for key, value in kwargs.items():
            if key in myDict and key in self.measures:
                if value == 'm':
                    myDict.setdefault(key + '_' + value, myDict[str(key)] / 1000)
                    myDict.pop(key)
                elif value == 'mm':
                    myDict.setdefault(key + '_' + value, myDict[str(key)])
                    myDict.pop(key)
                elif value == 'cm':
                    myDict.setdefault(key + '_' + value, myDict[str(key)] / 10)
                    myDict.pop(key)
            else:
                continue
        return myDict

    def centimeter(self, value):
        return self

    def millimeter(self, value):
        return self
