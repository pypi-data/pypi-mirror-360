""""

Iran : C = ABI/Ru
New Zealand :
AI =>> Z * Ru * N(D,T)
B =>> Ch(T)
Ru = Sp/Ku
As a Result :
Ch(T) = Spectral Shape Factor
ELASTIC SITE SPECTRA FOR HORIZONTAL LOADING => C(T1) = Ch(T) * Z * Ru * N(D,T)
Horizontal Design Action Coefficient  => Cd(T1) = C(T1) * Sp/Ku

Step 1 :
importance level: Importance level for hotel, offices, and apartments less than 15 stories high car buildings, shopping
    centers less than 10000 m^2 gross area is 2
Step 2 :
For this importance level (2): consequences of failure are ordinary, thus; Annual probability of the design event
    for safety is 1/500  for wind, 1/150 for snow and 1/500 for earthquake

Step 3 :
    Determine Vertical irregularity

Step 4:
    Determine method of analysis
    based on irregularity, floors and period; or (The equivalent static method of analysis shall be used only when at
    least one of the following criteria is satisfied)
•	The height between the base and the top of the structure is less than 10 m
•	The largest translational period calculated as specified in Clause 4.1.2(4.1.2 Period determination for the
    equivalent static method) is less than 0.4 s or
•	The structure is not classified as irregular under Clause 4.5 (4.5 STRUCTURAL IRREGULARITY) and the largest
    translation period is less than 2.0 seconds
•	6.2.3 Scaling of deflections
•	5.3.2 Accidental eccentricity


Step 5:
    Estimate the natural period   T1=  N/20=5/20=0.25     Where:N= the number of storeys

Step 6:
    Determine subsoil class
    	Class A – Strong rock 3.3.3.2
    	Class B – Rock 3.1.3.3
    	Class C – Shallow soil sites 3.1.3.4
    	Class D – Deep or soft soil sites 3.1.3.5
Step 7:
    Determine The spectral shape factor,
    Ch (T) based on the site subsoil class and natural period (T=N/20) defined in Clause 3.1.3
    	The spectral shape factor functions are graphed in Figure 3.1 for general cases and in Figure 3.2 for values for
    the modal response spectrum and the numerical integration time history methods
    	 The spectral shape factor for the equivalent static method need not exceed the value given by equation 3.1(2) for
    a period T of 0.4 s.

Step 8:
    Determine Z: the hazard factor determined from Clause 3.1.4
    Auckland is 0.13

Step 9:
    R: the return period factor R_δ or R_u for the appropriate limit state determined from Clause 3.1.5
    but limited such that ZR_u does not exceed 0.7    From=Table 3.5   1⁄500 =1  ultimate state,1⁄25=serviceability

Step 10:
    N (T, D): the near-fault factor determined from Clause 3.1.6
    Annual probability of exceedance≥1⁄250   ,    N(T,D)=1
    Annual probability of exceedance<1⁄250
        N(T,D)=N_max (T)     D≤2 Km
        N(T,D)=1+(N_max (T)-1)(20-D)/18     2Km<D≤2 Km if T<1.5 then N (T, D) =1
        N(T,D)=1    D>2 Km
    D : the shortest distance (in kilometers) from the site to the nearest fault listed in Table 3.6.

Step 11:
    Determine 3.1 ELASTIC SITE SPECTRA FOR HORIZONTAL LOADING  C(T1) = Ch(T) * Z * Ru * N(D,T)

Step 12:
    18.	Determine 2.2 STRUCTURAL TYPES

Step 13:
    Determine μ= MAXIMUM LEVELS OF DUCTILITY DEMAND ON STRUCTURAL STEEL SEISMIC-RESISTING SYSTEMS

Step 14: Sp and Ku
    μ= MAXIMUM LEVELS OF DUCTILITY DEMAND ON STRUCTURAL STEEL SEISMIC-RESISTING SYSTEMS
    Sp : The structural performance factor determined by Clause 4.4
    the structural performance factor, Sp, for the ultimate limit state shall be taken
    as 0.7 except where 1.0 < < 2.0 then Sp shall be defined by: Sp = 1.3 – 0.3

    Ku : The structural performance
    For soil classes A, B, C, D Kμ =μ   For T_1≥0.7s , Kμ =((μ-1) T_1)/0.7 For T1<0.7s
    For soil classes E      Kμ =μ   For T1≥1s or μ<1.5 , Kμ = (μ-1.5)T1+1.5 T1<1s or μ≥1.5


Step 15:
    Horizontal Design Action Coefficient  => Cd(T1) = C(T1) * Sp/Ku

Step 16:

    4.2 SEISMIC WEIGHT AND SEISMIC MASS w_i=G_i+∑▒φ_e  Q_i (وزن لرزه ایی)
        G_i,φ_e Q_i  Are summed between the mid-heights of adjacent stores
        G_i : The permanent action (self-weight or 'dead' action) at level i (DEAD)
        φ_e : 0. 6 is the earthquake-imposed action (live load) combination factor for storage applications
        φ_e : 0. 3 is the earthquake-imposed action (live load) combination factor for all
        Q_i : The imposed action for each occupancy class on level i (AS/NZS 1170.1)
        Q_i For roofs shall include allowance of 1kPa for ice on roofs
        the seismic mass at each level,m_i shall be taken as w_i/g


Step 17:
    Determine 6.2.1.2 Horizontal seismic shear V=Cd(T1)Wt
Step 18:
    Determine 3.2 SITE HAZARD SPECTRA FOR VERTICAL LOADING Cv(T)=0.7C(T)

Step 19:
    Determine 5.4 VERTICAL DESIGN ACTIONS Cvd=Cv(T) * Sp




"""
import math


class HDAC:
    results = {}
    pass
