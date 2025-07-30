class Loading:
    results = {}

    def __init__(self):
        pass

    def loading(self, G=1.5, Q=0.5, P=None, width=1000, length=1000, weight=500):
        self.results['geometry'].update({'width': width, 'length': length, 'weight': weight})
        width = self.results['geometry']['width']
        length = self.results['geometry']['length']
        weight = self.results['geometry']['weight']

        comb_1 = 1.35 * G
        m_n_1 = comb_1 * length ** 2 / 8
        v_n_1 = comb_1 * length / 2
        comb_2 = 1.2 * G + 1.5 * Q
        m_n_2 = comb_2 * length ** 2 / 8
        v_n_2 = comb_2 * length / 2
        long_service = G + 0.7 * Q
        short_service = G + 0.4 * Q

        self.results.setdefault('loads', {'G': G,
                                          'Q': Q,
                                          'P': P,
                                          'Mn1': round(m_n_1, 2),
                                          'Mn2': round(m_n_2, 2),
                                          'Vn1': round(v_n_2, 2),
                                          'Vn2': round(v_n_2, 2),
                                          })

        if v_n_1 >= self.results['V'] or v_n_2 >= self.results['V']:
            self.results['loads']['V_check'] = 'not satisfied'
        else:
            self.results['loads']['V_check'] = 'satisfied'

        if m_n_1 >= self.results['M'] or m_n_2 >= self.results['M']:
            self.results['loads']['M_check'] = 'not satisfied'
        else:
            self.results['loads']['M_check'] = 'satisfied'
        return self.results['loads']
