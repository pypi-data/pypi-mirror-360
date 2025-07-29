# SAMBA_ilum Copyright (C) 2024 - Closed source


import os

#===============================================
# Obtendo o caminho e o nome do diretório atual:
path_dir, name_dir = os.path.split(os.getcwd())
#===============================================

if os.path.isfile('../energy_scan.txt'):  energy = open('../energy_scan.txt', "a")
else:  energy = open('../energy_scan.txt', "w")

with open('OSZICAR') as file:
    lines = file.readlines()
VTemp = lines[-1].strip()

energia = VTemp.replace('=',' ').split()

energy.write(f'{name_dir} {energia[4]} \n')

temp_name = name_dir.replace('_', ' ').split()
t_temp_name = temp_name
#------------------------
if (len(temp_name) == 2):
   if (temp_name[0] == '0.0'): temp_name[0] = '1.0'
   if (temp_name[1] == '0.0'): temp_name[1] = '1.0'
   if (temp_name[0] == '1.0' or temp_name[1] == '1.0'):
      new_name_dir = str(temp_name[0]) + '_' + str(temp_name[1])
      energy.write(f'{new_name_dir} {energia[4]} \n')
   if (t_temp_name[0] == '1.0' and t_temp_name[1] == '1.0'):
      energy.write(f'1.0_0.0 {energia[4]} \n')
      energy.write(f'0.0_1.0 {energia[4]} \n')

energy.close()
