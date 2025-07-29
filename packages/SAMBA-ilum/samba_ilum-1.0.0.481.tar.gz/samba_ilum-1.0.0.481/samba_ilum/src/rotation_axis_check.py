# SAMBA_ilum Copyright (C) 2024 - Closed source



from pymatgen.io.vasp import Poscar
from pymatgen.core import Structure
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
#--------------------------------------------------------
import numpy as np
import sys  
import os

# Listando os arquivos dentro do diretório "dir_poscar"
files0 = [name for name in os.listdir(dir_files + '/' + dir_poscar + '/') if os.path.isfile(os.path.join(dir_files + '/' + dir_poscar + '/', name))]

print(files0)

#------------
stop_code = 0
#------------
for name in files0:
    Lattice = dir_files + '/' + dir_poscar + '/' + name

    print(Lattice)

    try:
        estrutura = Structure.from_file(Lattice)
        sga = SpacegroupAnalyzer(estrutura, symprec=1e-3)
        operacoes_0 = sga.get_symmetry_operations()
        operacoes_1 = sga.get_symmetry_operations(cartesian=True)
        
        angulos_z = []
        angulos_z_na_origem = []
        # =========================================================
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
        # =========================================================
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
        # =========================================================

        temp_name = name.replace('_',' ').split()
        menor_0 = min(angulos_z) if angulos_z else 0.0
        menor_1 = min(angulos_z_na_origem) if angulos_z_na_origem else 0.0

        # Se houver diferença, calcula, corrige e salva o new file.
        if (menor_0 != menor_1 and menor_0 != 0.0):
            stop_code += 1

            if (stop_code == 1):
               print(" ")
               print(f"-------------------------------------------------------------")
 
            print(f"POSCAR file: {name}")
            print(f"Discrepância encontrada em relação ao ângulo de rotação em torno do eixo Z")
            print(f"Menor ângulo geral: {int(menor_0)}°, Menor ângulo na origem: {int(menor_1)}°")
            
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
            
            if op_alvo:
                R = op_alvo.rotation_matrix
                t = op_alvo.translation_vector
                celula = estrutura.lattice.matrix.T

                try:
                    M = R - np.eye(3)
                    p_cart, *_ = np.linalg.lstsq(M, -t, rcond=None)
                    p_direto = np.linalg.solve(celula, p_cart)
                    
                    deslocamento_frac = np.array([-p_direto[0], -p_direto[1], 0.0])
                    print(f"Coordenadas diretas do eixo de rotação apropriado: ({p_direto[0]:.9f}, {p_direto[1]:.9f})")

                    estrutura_corrigida = estrutura.copy()
                    indices_dos_sites = list(range(len(estrutura_corrigida)))
                    estrutura_corrigida.translate_sites(indices_dos_sites, deslocamento_frac, frac_coords=True)
                    
                    name_base, extensao = os.path.splitext(name)
                    if not extensao: extensao = '.vasp'
                    new_name_file = f"{name_base}_fixed{extensao}"
                    Lattice_new_file = os.path.join(dir_files + '/' + dir_poscar + '/' , new_name_file)

                    estrutura_corrigida.to(fmt="poscar", filename=Lattice_new_file)
                    print(f"Estrutura corrigida salva como '{new_name_file}'")
                    print(f"-------------------------------------------------------------")

                except np.linalg.LinAlgError:
                    print("ERRO: Não foi possível calcular o deslocamento devido a um erro numérico.")

    except Exception as e:
        print(f"ERRO CRÍTICO ao processar o file {name}: {e}")

if (stop_code == 1):
   print(" ")
   print(f"Remova a versão anterior do arquivo POSCAR corrigido")
   print(f"Faça um Backup da versão corrigida do arquivo POSCAR para evitar ambiguidades em relação ao cálculo do xy-scan")
   print(f"Após isso, reinicie a execução do código")
   confirmacao = input (" "); confirmacao = str(confirmacao)
   sys.exit() 

if (stop_code > 1):
   print(" ")
   print(f"Remova a versão anterior dos arquivos POSCAR corrigidos")
   print(f"Faça um Backup da versão corrigida dos arquivos POSCAR para evitar ambiguidades em relação ao cálculo do xy-scan")
   print(f"Após isso, reinicie a execução do código")
   confirmacao = input (" "); confirmacao = str(confirmacao)
   sys.exit() 

