# Readme

This file contains gap-filled CO2 & CH4 fluxes for the Fish Island Flux Station from the 2017 field season, as described in Skeeter et al. (2022): https://doi.org/10.1139/as-2021-0034

Please contact june.skeeter@ubc.ca if you have any questions about the data.

NME_Gapfilled_nmol_m2_s - gap filled CH4 fluxes in nmol m2 s-1
* ch4_flux (observed - eddy pro output) filtered as describe in Skeeter et al. (2022), filled with NME_est (NN estimates) as described in Skeeter et al. 2022

NEE_Gapfilled_umol_m2_s - gap filled CO2 fluxes in umol m2 s-1
* co2_flux (observed - eddy pro output) filtered as describe in Skeeter et al. (2022), filled with NME_est (NN estimates) as described in Skeeter et al. 2022

Weather data include:

* wind_speed
* wind_dir
* u*
* VPD
* AirTC_ (Avg,Max,Min,Std)
* RH_ (Max, Min, Samp)
* Rain_mm_Tot
* NR_Wm2 (Avg,Max,Min,Std)
* PPFD (Avg,Max,Min,Std)

Flux Source Areas (relative %):

* Polygon
* Rim
* Collapse (collapsed rim)
* FarField (>150 m - beyond landscape classification)

Sub-surface data include:

* Soil temperatures (Temp) in degrees C at 2.5, 5, and 15 centimeters in polygon centers (1) and rims (2): e.g.,
	* Temp_2_5_1 (Soil Temp in Polygon centers at 2.5cm)
	* Temp_5_2 (Soil Temp in Polygon rims at 5cm)

* Water table depth in polygon centers (1) & rims (2)

* VWC in polygon centers (1) & rims (2)
	* Not calibrated, don't use for more than relative reference

* Active Layer depth in Polygon centers (1)



