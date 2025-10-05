import numpy as np
import math

type_astroid = 0
verif = False
density = 0
G = 6.6743*pow(10, -11)

#in cm
estimated_diameter_min = 100
estimated_diameter_max = 200 

while (verif == False) :
    print("choose type of meteorite : default (D), C, S, M)")
    type_astroid = input()
    match type_astroid :
        case "D" : 
            density = 2 
            verif = True
        case "C" : 
            density = 1.38
            verif = True
        case "S" : 
            density = 2.71
            verif = True
        case "M" : 
            density = 5.32
            verif = True
print("Your astroid estimated density is : %f g/cm^3" %density)
      
mass_astroid = 3/4*(np.pi* estimated_diameter_min * estimated_diameter_max * estimated_diameter_min) * density
print("the heavily approximated mass of the astroid : %f g" %mass_astroid)
      
#location of the impact (g/cm^3)

'''
verif = False
while (verif == False) :
    print("choose type of soil : default (D), sand (S) clay (C)")
    type_astroid = input()
    match type_astroid :
        case "D" : 
            density_crater = 5.513  
            verif = True
        case "S" : 
            density_crater = 1.52
            verif = True
        case "C" : 
            density_crater = 1.20
            verif = True
'''

density_crater = 5.513  

print("Your soil estimated density is : %f g/cm^3" %density_crater)
      
#velocity of astroid near impact
print("Enter velocity:")
v = float(input())

#gravitational acceleration of  astroid 
g_astroid = G*mass_astroid/pow(estimated_diameter_max/2,2)
                               
#crater impact size
kinetic_energy = (mass_astroid*v*v)/2
print("kinetic_energy = %f J" % kinetic_energy)
diameter_crater = 0.07*1.3*pow(g_astroid/G, 1/6)*pow(kinetic_energy*density/density_crater, 1/3.4)
print("diameter_crater = ", diameter_crater)

print("Enter the entry angle:")
angle_entry = input()
diameter_astroid = (estimated_diameter_min+estimated_diameter_max)/2

def air_density_to11(h) :
    return 101325.0*math.pow((1+(-0.0065/288)*h), 9.80665*28.9644/8.31432*0.0065)
                      
def air_density_11plus(h) :
    return 22632.0*math.exp((-9.80665*28.9644*(h-110000)/(8.31432*71.5)))

Y = [0,0]


from scipy.integrate import solve_ivp

#everything in meter and sec 
#suppose astroid = spehere

def equadif(t, Y, a, b):
    y1 = Y[0]
    y2 = Y[1]

    dy1_dt = y2
    dy2_dt = -a*dy1_dt-b*y1

    return [dy1_dt, dy2_dt]

mass_earth = 5.972 * (10**4)
Vol = 3/4*(np.pi* estimated_diameter_min * estimated_diameter_max * estimated_diameter_min)
S = np.pi*pow(Vol*3/(4*np.pi), 2/3)
angle = np.pi/6 #30deg
x0 = 0
y0 = 50000
X0 = 30
Y0 = 30

h = 50
while (h>0) :
    if (h<11000) :
        print("the hingh is less than 11000")
        alpha = 0.5*(0.9*air_density_to11(h)*S)*mass_astroid
        print("Alpha:", alpha)
    else : 
        alpha = 0.5*(0.9*air_density_11plus(h)*S)*mass_astroid

    
    beta = mass_astroid*G*mass_earth*math.sqrt(h)
    print(beta)
    solution = solve_ivp(equadif, [0, 50], [x0, X0], method='RK45', args=(alpha , beta))
    print("go")
    print(solution.y[0])
    print(solution.y[1])
    h=h-1


print(air_density_to11(2.0))