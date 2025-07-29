# SAMBA_ilum Copyright (C) 2024 - Closed source


import os

cut_off_energy = open('cut_off_energy.py', "w")

#---------------------------------------------------------
# Listando os arquivos presentes no diretório 'POTCAR' ---
#---------------------------------------------------------
files = os.listdir()
#-------------------


for i in range(len(files)):
    #---------------------------
    potcar = open(files[i], "r")
    X = files[i].replace('POTCAR_', '')
    #------------------------------------------------------------
    if ((X != '_info_pseudo.py') and (X != 'cut_off_energy.py')):
       test = '@#$%¨&*()'
       while (test != 'ENMAX'):
             VTemp = potcar.readline().split()
             if (len(VTemp) > 0):  test = str(VTemp[0])
       #-----------------------------------------------
       ENMAX = float(VTemp[2].replace(';', ''))
       cut_off_energy.write(f'ENCUT_{X} = {ENMAX} \n')
    #-------------------------------------------------
    potcar.close()
#---------------------
cut_off_energy.close()
#---------------------


