
# Written by June Skeeter
# Equations Adapted From:
# https://gml.noaa.gov/grad/solcalc/calcdetails.html

import numpy as np

def SunStats(LAT,LON,JD,TIME,TZ):
    F2 = JD+TIME-TZ/24 ## Use PD.to_julian
    G2 = (F2-2451545)/36525 #Julian Century
    I2 = (280.46646+G2*(36000.76983 + G2*0.0003032))%360 #Geom Mean Long Sun (deg)
    J2 = 357.52911+G2*(35999.05029 - 0.0001537*G2)#Geom Mean Anom Sun (deg)
    K2 = 0.016708634-G2*(0.000042037+0.0000001267*G2)#Eccent Earth Orbit
    L2 = np.sin(np.radians(J2))*(1.914602-G2*(0.004817+0.000014*G2))+np.sin(np.radians(2*J2))*(0.019993-0.000101*G2)+np.sin(np.radians(3*J2))*0.000289 #Sun Eq of Ctr
    M2 = I2+L2 #Sun True Long (deg)
    N2 = J2+L2 #Sun True Anom (deg)
    O2 = (1.000001018*(1-K2*K2))/(1+K2*np.cos(np.radians(N2))) #Sun Rad Vector (AUs)
    P2 = M2-0.00569-0.00478*np.sin(np.radians(125.04-1934.136*G2)) #Sun App Long (deg)
    Q2 = 23+(26+((21.448-G2*(46.815+G2*(0.00059-G2*0.001813))))/60)/60 #Mean Obliq Ecliptic (deg)
    R2 = Q2+0.00256*np.cos(np.radians(125.04-1934.136*G2)) #Obliq Corr (deg)
    S2 = np.radians(np.arctan2(np.cos(np.radians(R2))*np.sin(np.radians(P2)),np.cos(np.radians(P2)))) #Sun Rt Ascen (deg)
    T2 = np.degrees(np.arcsin(np.sin(np.radians(R2))*np.sin(np.radians(P2)))) #Sun Declin (deg)
    U2 = np.tan(np.radians(R2/2))*np.tan(np.radians(R2/2))# var y
    V2 = 4*np.degrees(U2*np.sin(2*np.radians(I2))-2*K2*np.sin(np.radians(J2))+4*K2*U2*np.sin(np.radians(J2))*np.cos(2*np.radians(I2))-0.5*U2*U2*np.sin(4*np.radians(I2))-1.25*K2*K2*np.sin(2*np.radians(J2))) #Eq of Time (minutes)
    W2 = np.degrees(np.arccos(np.cos(np.radians(90.833))/(np.cos(np.radians(LAT))*np.cos(np.radians(T2)))-np.tan(np.radians(LAT))*np.tan(np.radians(T2)))) #HA Sunrise (deg)

    X2 = (720-4*LON-V2+TZ*60)/1440 #Solar Noon (LST)
    Y2 = (X2*1440-W2*4)/1440 #Sunrise Time (LST)
    Z2 = (X2*1440+W2*4)/1440 #Sunset Time (LST)

    AA2=8*W2 #Sunlight Duration (minutes)
    AB2=(TIME*1440+V2+4*LON-60*TZ)%1440 # True Solar Time (min)

    AC2 = AB2*1
    AC2[AB2/4<0] = AB2[AB2/4<0]/4+180
    AC2[AB2/4>0] = AB2[AB2/4>00]/4+180

    AD2 = np.degrees(np.arccos(np.sin(np.radians(LAT))*np.sin(np.radians(T2))+np.cos(np.radians(LAT))*np.cos(np.radians(T2))*np.cos(np.radians(AC2))))# Solar Zenith Angle (deg)

    AE2 = 90-AD2 #Solar Elevation Angle (deg)
    AF2 = AE2*0

    AF2[AE2<=85] = 58.1/np.tan(np.radians(AE2[AE2<85]))-0.07/((np.tan(np.radians(AE2[AE2<85])))**3)+0.000086/(np.tan(np.radians(AE2[AE2<85]))**5)
    # AF2[AE2<=5] = 1735+AE2[AE2<5]*(-518.2+AE2[AE2<5]*(103.4+AE2[AE2<5]*(-12.79+AE2[AE2<5]*0.711)))
    # ,IF(AE8>-0.575,1735+AE8*(-518.2+AE8*(103.4+AE8*(-12.79+AE8*0.711))),
    AF2[AE2<=5] = 1735+AE2[AE2<5]*(-518.2)+(AE2[AE2<5]**2)*(103.4)+(AE2[AE2<5]**3)*(-12.79)+((AE2[AE2<5])**4)*0.711
    AF2[AE2<=-0.575] = -20.772/np.tan(np.radians(AE2[AE2<=-0.575]))

    AF2/=3600#pprox Atmospheric Refraction (deg)
    Angle_Corr = AE2+AF2 #Solar Elevation corrected for atm refraction (deg)

    Azimuth = AC2*0
    Azimuth[AC2>0] = (np.degrees(np.arccos(((np.sin(np.radians(LAT[AC2>0]))*np.cos(np.radians(AD2[AC2>0])))-np.sin(np.radians(T2[AC2>0])))/(np.cos(np.radians(LAT[AC2>0]))*np.sin(np.radians(AD2[AC2>0])))))+180)%360
    Azimuth[AC2<=0] = (np.degrees(np.arccos(((np.sin(np.radians(LAT[AC2<=0]))*np.cos(np.radians(AD2[AC2<=0])))-np.sin(np.radians(T2[AC2<=0])))/(np.cos(np.radians(LAT[AC2<=0]))*np.sin(np.radians(AD2[AC2<=0])))))+180)%360

    Zenith=AD2
    Angle=AE2
    Sunrise=Y2
    Sunset=Z2

    return(Zenith,Angle,Angle_Corr,Azimuth,Sunrise,Sunset)
    