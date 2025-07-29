# SAMBA_ilum Copyright (C) 2024 - Closed source


print("==================================")
print("Espere um momento ================")
print("==================================")
print("")


from pymatgen.io.vasp import Poscar
from pymatgen.core import Structure
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
#--------------------------------------------------------
import numpy as np
import shutil
import sys
import os


# Listando os arquivos dentro do diretório "dir_poscar"
poscar_dir_path = os.path.join(dir_files, dir_poscar)
files0 = [name for name in os.listdir(poscar_dir_path) if os.path.isfile(os.path.join(poscar_dir_path, name))]


#===================================================
# Testando a compatibilidade dos arquivos POSCAR ===
#===================================================
A1x0 = [];  A1y0 = [];  A2x0 = [];  A2y0 = []  
#--------------------------------------------
for k in range(len(files0)):
    #-----------------------
    Lattice = dir_files + '/' + dir_poscar + '/' + files0[k]
    poscar = open(Lattice, "r")
    #-------------------------------------------
    for i in range(2): VTemp = poscar.readline()
    param = float(VTemp)
    #-------------------------------------------
    A1 = poscar.readline().split();  A1x = float(A1[0])*param;  A1y = float(A1[1])*param;  A1z = float(A1[2])*param  
    A2 = poscar.readline().split();  A2x = float(A2[0])*param;  A2y = float(A2[1])*param;  A2z = float(A2[2])*param  
    A3 = poscar.readline().split();  A3x = float(A3[0])*param;  A3y = float(A3[1])*param;  A3z = float(A3[2])*param  
    #--------------------------------------------------------------------------------------------------------------
    A1x0.append(A1x);  A1y0.append(A1y);  A2x0.append(A2x);  A2y0.append(A2y)   # Armazenando os vetores A1 e A2 de cada rede
    #------------------------------------------------------------------------------------------------------------------------
    if ((A1z != 0.0) or (A2z != 0.0) or (A3x != 0.0) or (A3y != 0.0)):
       print(f'========================================')
       print(f'Verifique os arquivos POSCAR utilizados!')
       print(f'Incompatibilidade com o código detectada')
       print(f'Somente redes 2D no plano XY são aceitos')
       print(f'----------------------------------------')
       print(f'Os vetores de rede devem possuir a forma')
       print(f'A1 = [A1x, A1y, 0.0]')
       print(f'A2 = [A2x, A2y, 0.0]')
       print(f'A3 = [0.0, 0.0, A3z]')
       print(f'========================================')
       print(f' ')
       #-------------
       poscar.close()
       sys.exit()   
    #-------------
    poscar.close()  
    #-------------


#=====================================================================
# Testando se os arquivos POSCAR correspondem há células unitárias ===
#=====================================================================
supercell_files = []
#-------------------------
for filename in files0:
    poscar_path = os.path.join(poscar_dir_path, filename)
    try:
        original_structure = Structure.from_file(poscar_path)
        primitive_structure = original_structure.get_primitive_structure()
        if (len(original_structure) > len(primitive_structure)): supercell_files.append(filename)
    except Exception as e: print(f"Aviso: Não foi possível analisar o arquivo '{filename}'.")
#----------------------------
if (len(supercell_files) > 0):
   print(f'========================================')
   print(f'Verifique os arquivos POSCAR utilizados!')
   print(f'Foram identificadas as seguinte células não-unitárias: {supercell_files}')
   print(f'----------------------------------------')
   print(f'Deseja prosseguir com estes arquivos?   ')
   print(f'Digite:  [0] para NÃO  e  [1] para SIM  ')
   print(f'========================================')
   print(f' ')
   selected_option = input(" "); selected_option = int(selected_option)
   if (selected_option != 1): sys.exit()    
   #------------------------------------


#======================================================
# Chegando/Corrigindo o eixo de rotação das células ===
#======================================================
axis_correction = 0
#------------------
for name in files0:
    Lattice = os.path.join(poscar_dir_path, name)
    #--------------------------------------------
    poscar = open(Lattice, 'r')
    VTemp = poscar.readline();  VTemp = str(VTemp)
    poscar.close()
    #-------------
    try:
        estrutura = Structure.from_file(Lattice)
        sga = SpacegroupAnalyzer(estrutura, symprec=1e-3)
        operacoes_0 = sga.get_symmetry_operations()
        operacoes_1 = sga.get_symmetry_operations(cartesian=True)
        #-------------
        angulos_z = []
        angulos_z_na_origem = []
        #--------------------------------------------------
        # Loop 1: Encontra todos os ângulos de rotação em Z
        for op in operacoes_0:
            R = op.rotation_matrix
            if int(round(np.linalg.det(R))) != 1: continue
            z = np.array([0, 0, 1])
            if np.allclose(R @ z, z, atol=1e-3):
                Rxy = R[:2, :2]
                trace = np.trace(Rxy)
                cos_theta = np.clip(trace / 2.0, -1.0, 1.0)
                angle = np.arccos(cos_theta)
                angle_deg = round(np.degrees(angle), 4)
                if 0.1 < angle_deg < 360.0 and angle_deg not in angulos_z:
                    angulos_z.append(angle_deg)
        #--------------------------------------------------
        # Loop 2: Encontra rotações em Z que fixam a origem
        z = np.array([0, 0, 1])
        for op in operacoes_1:
            R = op.rotation_matrix
            if not np.allclose(op.translation_vector, 0, atol=1e-3): continue
            if int(round(np.linalg.det(R))) != 1: continue
            if np.allclose(R @ z, z, atol=1e-3):
                trace_3d = np.trace(R)
                cos_theta_3d = np.clip((trace_3d - 1.0) / 2.0, -1.0, 1.0)
                angle = np.arccos(cos_theta_3d)
                angle_deg = round(np.degrees(angle), 4)
                if 0.1 < angle_deg < 360.0 and angle_deg not in angulos_z_na_origem:
                    angulos_z_na_origem.append(angle_deg)
        #------------------------------------------------
        temp_name = name.replace('_',' ').split()
        menor_0 = min(angulos_z) if angulos_z else 0.0
        menor_1 = min(angulos_z_na_origem) if angulos_z_na_origem else 0.0
        #----------------------------------------------------------
        # Se houver diferença, calcula, corrige e salva o new file.
        if (menor_0 != menor_1 and menor_0 != 0.0):
            axis_correction += 1
            #--------------------------------------------------------------
            # 1. Definindo os diretórios de backup e criando se necessário
            backup_dir = os.path.join(dir_files, 'POSCAR_original')
            os.makedirs(backup_dir, exist_ok=True)
            #---------------------------------------------------------
            # 2. Definindo os caminhos do arquivo original e do backup
            original_filepath = os.path.join(poscar_dir_path, name)
            backup_filepath = os.path.join(backup_dir, name)
            #-----------------------------------------------------
            # 3. Movendo o arquivo original para a pasta de backup
            shutil.move(original_filepath, backup_filepath)
            #----------------------------------------------
            if (axis_correction == 1):
                print(" ")
                print(f"-------------------------------------------------------------")
            print(f"POSCAR file: {name}")
            print(f"Discrepância encontrada em relação ao ângulo de rotação em torno do eixo Z")
            print(f"Min. Rotation Angle: {int(menor_0)}º / Angle at Origin: {int(menor_1)}º")
            #-------------
            op_alvo = None
            for op_cart in operacoes_1:
                R_cart = op_cart.rotation_matrix
                if int(round(np.linalg.det(R_cart))) != 1 or not np.allclose(R_cart @ z, z, atol=1e-3):
                    continue
                trace_3d = np.trace(R_cart)
                cos_theta_3d = np.clip((trace_3d - 1.0) / 2.0, -1.0, 1.0)
                if np.isclose(np.degrees(np.arccos(cos_theta_3d)), menor_0, atol=1e-4):
                    op_alvo = op_cart
                    break
            #------------
            if op_alvo:
                R = op_alvo.rotation_matrix
                t = op_alvo.translation_vector
                celula = estrutura.lattice.matrix.T
                #----------------------------------
                try:
                    M = R - np.eye(3)
                    p_cart, *_ = np.linalg.lstsq(M, -t, rcond=None)
                    p_direto = np.linalg.solve(celula, p_cart)
                    #--------------------------------------------------------------
                    deslocamento_frac = np.array([-p_direto[0], -p_direto[1], 0.0])
                    print(f"Coordenadas diretas do eixo de rotação apropriado: ({p_direto[0]:.9f}, {p_direto[1]:.9f})")
                    print(f"Movendo arquivo original para a pasta 'POSCAR_original' e criando versão corrigida.")
                    #------------------------------------
                    estrutura_corrigida = estrutura.copy()
                    indices_dos_sites = list(range(len(estrutura_corrigida)))
                    estrutura_corrigida.translate_sites(indices_dos_sites, deslocamento_frac, frac_coords=True)
                    #----------------------------------------------------------------------
                    # Salvar o arquivo corrigido com o nome_original no diretório original.
                    Lattice_new_file = os.path.join(poscar_dir_path, name)
                    estrutura_corrigida.to(fmt="poscar", filename=Lattice_new_file)
                    print(f"-------------------------------------------------------------")
                except np.linalg.LinAlgError:
                    print("ERRO: Não foi possível calcular o deslocamento devido a um erro numérico.")
            #-------------------------------------------------------
            with open(Lattice, 'r') as file: line = file.readlines()
            line[0] = VTemp
            with open(Lattice, 'w') as file: file.writelines(line)
    #---------------------
    except Exception as e:
        print(f"Erro Crítico ao processar o file {name}: {e}")
        if (axis_correction > 0): sys.exit()
