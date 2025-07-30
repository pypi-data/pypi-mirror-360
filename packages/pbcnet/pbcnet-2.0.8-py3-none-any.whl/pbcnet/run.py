# PBCNet2.0 预测工具 - 主程序文件
# 功能：从配体SDF文件和蛋白质PDB文件进行蛋白质-配体结合亲和力预测
# 作者：PBCNet团队
# 版本：2.0

import os
import argparse  # 命令行参数解析
import pandas as pd  # 数据处理
import numpy as np  # 数值计算
from rdkit import Chem  # 化学分子处理
from rdkit.Chem import AllChem
from tqdm import tqdm  # 进度条显示
import warnings
warnings.filterwarnings('ignore')  # 忽略警告信息
from scipy.spatial import distance_matrix  # 距离矩阵计算
from Bio.PDB import *  # 蛋白质结构处理
from Bio.PDB.PDBIO import Select
from rdkit.Chem.rdchem import BondType as BT  # 化学键类型
from rdkit.Chem import BRICS  # 分子片段分解
import torch  # PyTorch深度学习框架
import multiprocessing
import dgl  # 深度图学习库
from Bio.PDB.PDBParser import PDBParser
from rdkit import DataStructs
from sklearn.metrics import mean_absolute_error, mean_squared_error  # 评估指标
from torch.utils.data import DataLoader  # 数据加载器
import sys
from model_code.Dataloader.dataloader import LeadOptDataset, collate_fn  # 自定义数据集
from model_code.utilis.utilis import pkl_load  # 工具函数
from model_code.predict.predict import predict  # 预测函数
import scipy.stats as stats  # 统计分析
import pickle  # 序列化
import matplotlib.pyplot as plt  # 绘图


# ==================== 蛋白质口袋提取模块 ====================

def extract(ligand, pdb):
    """
    从蛋白质结构中提取与配体相互作用的口袋区域
    
    参数:
        ligand: 配体分子列表
        pdb: 蛋白质PDB文件路径
    
    返回:
        None (直接保存口袋PDB文件)
    """
    parser = PDBParser()
    if not os.path.exists(pdb):
        print("The path of PDB is not available.")
        return None

    # 解析蛋白质结构
    structure = parser.get_structure("protein", pdb)

    # 获取所有配体原子的坐标
    lp = []
    for l in ligand:
        lp.append(l.GetConformer().GetPositions())
    ligand_positions = np.concatenate(lp)

    # 定义残基选择类：选择距离配体8埃以内的残基
    class ResidueSelect(Select):
        def accept_residue(self, residue):
            # 获取残基中所有非氢原子的坐标
            residue_positions = np.array([np.array(list(atom.get_vector())) \
                for atom in residue.get_atoms() if "H" not in atom.get_id()])
            if len(residue_positions.shape) < 2:
                print(residue)
                return 0
            # 计算残基与配体的最小距离
            min_dis = np.min(distance_matrix(residue_positions, ligand_positions))
            if min_dis < 8.0:  # 8埃截断距离
                return 1
            else:
                return 0
    
    # 保存口袋结构
    io = PDBIO()
    io.set_structure(structure)
    fn = pdb.replace('protein.pdb', 'pocket.pdb')
    io.save(fn, ResidueSelect())


def pocket_extract(sdf_files, protein_file):
    """
    批量处理SDF文件，提取对应的蛋白质口袋
    
    参数:
        sdf_files: SDF文件路径列表
        protein_file: 蛋白质PDB文件路径
    """
    ligands = []
    # 读取所有配体分子
    for a in sdf_files:
        mol = Chem.MolFromMolFile(a)
        if mol is not None:
            ligands.append(mol)
        else:
            print(f"{a} connot be read by rdkit!")

    # 提取口袋
    extract(ligands, protein_file)
    print("The pocket has been extracted successfully.")


# ==================== 图数据生成模块 ====================

def setup_cpu(cpu_num):
    """
    设置CPU线程数，优化计算性能
    
    参数:
        cpu_num: CPU线程数
    """
    os.environ['OMP_NUM_THREADS'] = str(cpu_num)
    os.environ['OPENBLAS_NUM_THREADS'] = str(cpu_num)
    os.environ['MKL_NUM_THREADS'] = str(cpu_num)
    os.environ['VECLIB_MAXIMUM_THREADS'] = str(cpu_num)
    os.environ['NUMEXPR_NUM_THREADS'] = str(cpu_num)

warnings.filterwarnings('ignore')

# 原子特征的可能取值范围定义
allowable_features = {
    'possible_chirality_list': ['CHI_UNSPECIFIED',
                                'CHI_TETRAHEDRAL_CW',
                                'CHI_TETRAHEDRAL_CCW',
                                'CHI_OTHER'],
    'possible_degree_list': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 'misc'],
    'possible_numring_list': [0, 1, 2, 3, 4, 5, 6, 'misc'],
    'possible_implicit_valence_list': [0, 1, 2, 3, 4, 5, 6, 'misc'],
    'possible_formal_charge_list': [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 'misc'],
    'possible_numH_list': [0, 1, 2, 3, 4, 5, 6, 7, 8, 'misc'],
    'possible_number_radical_e_list': [0, 1, 2, 3, 4, 'misc'],
    'possible_hybridization_list': ['SP', 'SP2', 'SP3', 'SP3D', 'SP3D2', 'misc'],
    'possible_is_aromatic_list': [False, True],
    'possible_is_in_ring3_list': [False, True],
    'possible_is_in_ring4_list': [False, True],
    'possible_is_in_ring5_list': [False, True],
    'possible_is_in_ring6_list': [False, True],
    'possible_is_in_ring7_list': [False, True],
    'possible_is_in_ring8_list': [False, True]
}


def safe_index(l, e):
    """
    安全地获取元素在列表中的索引，如果不存在则返回最后一个索引
    
    参数:
        l: 列表
        e: 要查找的元素
    
    返回:
        元素的索引或最后一个索引
    """
    try:
        return l.index(e)
    except:
        return len(l) - 1


# ==================== 蛋白质残基信息处理 ====================
# 注意：残基信息在PBCNet2.0中未使用，保留用于扩展

# 单字母到三字母氨基酸代码转换表
one_to_three = {"A": "ALA", "C": "CYS", "D": "ASP", "E": "GLU", "F": "PHE",
                "G": "GLY", "H": "HIS", "I": "ILE", "K": "LYS", "L": "LEU",
                "M": "MET", "N": "ASN", "P": "PRO", "Q": "GLN", "R": "ARG",
                "S": "SER", "T": "THR", "V": "VAL", "W": "TRP", "Y": "TYR",
                "B": "ASX", "Z": "GLX", "X": "UNK", "*": " * "}

# 构建反向转换表
three_to_one = {}
for _key, _value in one_to_three.items():
    three_to_one[_value] = _key
three_to_one["SEC"] = "C"
three_to_one["MSE"] = "M"

# 氨基酸分类表
pro_res_table = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y', 'X']
pro_res_aliphatic_table = ['A', 'I', 'L', 'M', 'V']  # 脂肪族氨基酸
pro_res_aromatic_table = ['F', 'W', 'Y']  # 芳香族氨基酸
pro_res_polar_neutral_table = ['C', 'N', 'Q', 'S', 'T']  # 极性中性氨基酸
pro_res_acidic_charged_table = ['D', 'E']  # 酸性带电氨基酸
pro_res_basic_charged_table = ['H', 'K', 'R']  # 碱性带电氨基酸


def prop(residue):
    """
    根据氨基酸类型生成属性向量
    
    参数:
        residue: 氨基酸单字母代码
    
    返回:
        属性向量 [脂肪族, 芳香族, 极性中性, 酸性带电, 碱性带电, 常数1]
    """
    res_property1 = [1 if residue in pro_res_aliphatic_table else 0,
                     1 if residue in pro_res_aromatic_table else 0,
                     1 if residue in pro_res_polar_neutral_table else 0,
                     1 if residue in pro_res_acidic_charged_table else 0,
                     1 if residue in pro_res_basic_charged_table else 0, 1]
    return res_property1


def res_pocket(p):
    """
    解析蛋白质口袋文件，提取残基信息
    
    参数:
        p: 蛋白质口袋PDB文件路径
    
    返回:
        atom2res_idx: 原子到残基的映射索引
        res_type: 残基类型编码
        res_prop: 残基属性向量
    """
    parser = PDBParser(PERMISSIVE=1)
    s = parser.get_structure('a', p)
   
    atom2res_idx = []
    res_name = []
    count = -1
    
    # 遍历所有残基和原子
    for model in s:
        for chain in model:
            for residue in chain:
                count += 1
                name = residue.get_resname()
                for atom in residue:
                    # 只处理非氢原子
                    if atom.get_fullname()[0] != 'H' and atom.get_fullname()[1] != 'H':
                        atom2res_idx.append(count)
                        res_name.append(name)

    # 转换残基名称为单字母代码
    res3 = [three_to_one[i] if i in three_to_one.keys() else 'X' for i in res_name]
    
    # 生成残基类型编码和属性
    res_type = [pro_res_table.index(i) for i in res3]
    res_prop = [prop(i) for i in res3]
    
    assert len(atom2res_idx) == len(res_type) == len(res_prop)
    return atom2res_idx, res_type, res_prop


# ==================== 原子特征提取 ====================

def lig_atom_featurizer(mol):
    """
    提取分子中每个原子的特征向量
    
    参数:
        mol: RDKit分子对象
    
    返回:
        原子特征列表，每个原子对应一个特征向量
    """
    ringinfo = mol.GetRingInfo()
    atom_features_list = []
    
    for idx, atom in enumerate(mol.GetAtoms()):
        atom_features_list.append([
            safe_index(allowable_features['possible_chirality_list'], str(atom.GetChiralTag())),  # 手性
            safe_index(allowable_features['possible_degree_list'], atom.GetTotalDegree()),  # 度数
            safe_index(allowable_features['possible_formal_charge_list'], atom.GetFormalCharge()),  # 形式电荷
            safe_index(allowable_features['possible_numH_list'], atom.GetTotalNumHs()),  # 氢原子数
            safe_index(allowable_features['possible_hybridization_list'], str(atom.GetHybridization())),  # 杂化类型
            allowable_features['possible_is_aromatic_list'].index(atom.GetIsAromatic()),  # 是否芳香
            safe_index(allowable_features['possible_implicit_valence_list'], atom.GetImplicitValence()),  # 隐式价
            safe_index(allowable_features['possible_number_radical_e_list'], atom.GetNumRadicalElectrons()),  # 自由基电子数
            safe_index(allowable_features['possible_numring_list'], ringinfo.NumAtomRings(idx)),  # 环数
        ])

    return atom_features_list


# ==================== 分子分组和复合物处理 ====================

def group_complex(ligand, pocket_dir):
    """
    为复合物中的原子分配分组信息
    
    参数:
        ligand: 配体分子
        pocket_dir: 蛋白质口袋文件路径
    
    返回:
        group_index: 分组索引张量
        group_type: 分组类型张量
        group_prop: 分组属性张量
    """
    # 使用BRICS分解配体
    brics_index = brics_decomp(ligand)
    group_index = [0 for _ in range(len(ligand.GetAtoms()))]
    group_type = [0 for _ in range(len(ligand.GetAtoms()))]  # 配体原子类型为0
    group_prop = [[0,0,0,0,0,0] for _ in range(len(ligand.GetAtoms()))]  # 配体属性为0

    if type(brics_index) == type(tuple(('a', 'b', 'c'))):
        brics_index = brics_index[0]

    # 为配体原子分配分组索引
    for i, idx in enumerate(brics_index):
        for idx_ in idx:
            group_index[idx_] = i

    # 处理蛋白质残基信息
    atom2res_idx, res_type, res_prop = res_pocket(pocket_dir)
    
    # 调整蛋白质原子的分组索引（避免与配体重叠）
    atom2res_idx = [i+len(brics_index) for i in atom2res_idx]
    res_type = [i+1 for i in res_type]  # 蛋白质残基类型从1开始

    # 合并配体和蛋白质信息
    group_index.extend(atom2res_idx)
    group_type.extend(res_type)
    group_prop.extend(res_prop)

    return torch.tensor(group_index, dtype=torch.float32), torch.tensor(group_type, dtype=torch.float32), torch.tensor(group_prop, dtype=torch.float32)


def atom_type(ligand, pocket):
    """
    获取复合物中所有原子的类型信息
    
    参数:
        ligand: 配体分子
        pocket: 蛋白质口袋分子
    
    返回:
        z: 原子序数张量
        type_for_mask: 原子类型掩码（1为配体，0为蛋白质）
    """
    # 获取配体原子序数
    l_atom = np.array([i.GetAtomicNum() for i in ligand.GetAtoms()])
    lig_atom = [1 for _ in l_atom]  # 配体标记为1
    
    # 获取蛋白质原子序数
    p_atom = np.array([i.GetAtomicNum() for i in pocket.GetAtoms()])
    pock_atom = [0 for _ in p_atom]  # 蛋白质标记为0
    
    # 合并原子信息
    complex_atom = torch.tensor(np.concatenate([l_atom, p_atom]))
    type_for_mask = torch.tensor(np.concatenate([lig_atom, pock_atom]))
    z = complex_atom
    return z, type_for_mask


# ==================== 化学键特征提取 ====================

# 化学键类型映射
bonds = {BT.SINGLE: 0, BT.DOUBLE: 1, BT.TRIPLE: 2, BT.AROMATIC: 3}
# 4: 分子内部距离边; 5: 蛋白内部边; 6: 蛋白-配体边


def bond_featurizer(ligand, pocket, index):
    """
    为化学键生成特征向量
    
    参数:
        ligand: 配体分子
        pocket: 蛋白质口袋分子
        index: 边的索引对
    
    返回:
        化学键类型张量
    """
    bond_type = []
    num_atoms = len(ligand.GetAtoms())
    
    for a1, a2 in zip(index[0], index[1]):
        if a1 < num_atoms and a2 < num_atoms:  # 配体内部的键
            bond = ligand.GetBondBetweenAtoms(a1, a2)
            if bond is None:
                bond_type.append(4)  # 距离键
            else:
                bond_type.append(bonds[bond.GetBondType()])
        elif a1 >= num_atoms and a2 >= num_atoms:  # 蛋白质内部的键
            a1 = a1 - num_atoms
            a2 = a2 - num_atoms
            bond = pocket.GetBondBetweenAtoms(a1, a2)
            if bond is None:
                bond_type.append(4)  # 距离键
            else:
                bond_type.append(bonds[bond.GetBondType()])
        else:  # 蛋白质-配体间的键
            bond_type.append(4)
    
    return torch.tensor(bond_type, dtype=torch.float32)


# ==================== 分子分解模块 ====================
# R-group信息，在PBCNet2.0中未使用

def brics_decomp(mol):
    """
    使用BRICS算法分解分子为片段
    
    参数:
        mol: RDKit分子对象
    
    返回:
        分子片段列表
    """
    n_atoms = mol.GetNumAtoms()
    if n_atoms == 1:
        return [[0]], []

    cliques = []
    breaks = []
    
    # 初始化：每个键作为一个团
    for bond in mol.GetBonds():
        a1 = bond.GetBeginAtom().GetIdx()
        a2 = bond.GetEndAtom().GetIdx()
        cliques.append([a1, a2])

    # 找到BRICS断裂键
    res = list(BRICS.FindBRICSBonds(mol))
    if len(res) == 0:
        return [list(range(n_atoms))], []
    else:
        # 处理断裂键
        for bond in res:
            if [bond[0][0], bond[0][1]] in cliques:
                cliques.remove([bond[0][0], bond[0][1]])
            else:
                cliques.remove([bond[0][1], bond[0][0]])
            cliques.append([bond[0][0]])
            cliques.append([bond[0][1]])

    # 合并重叠的团
    for c in range(len(cliques) - 1):
        if c >= len(cliques):
            break
        for k in range(c + 1, len(cliques)):
            if k >= len(cliques):
                break
            if len(set(cliques[c]) & set(cliques[k])) > 0:
                cliques[c] = list(set(cliques[c]) | set(cliques[k]))
                cliques[k] = []
        cliques = [c for c in cliques if len(c) > 0]
    cliques = [c for c in cliques if len(c) > 0]

    # 生成边信息
    edges = []
    for bond in res:
        for c in range(len(cliques)):
            if bond[0][0] in cliques[c]:
                c1 = c
            if bond[0][1] in cliques[c]:
                c2 = c
        edges.append((c1, c2))
    for bond in breaks:
        for c in range(len(cliques)):
            if bond[0] in cliques[c]:
                c1 = c
            if bond[1] in cliques[c]:
                c2 = c
        edges.append((c1, c2))

    return cliques


# ==================== 图信息构建 ====================

def Graph_Information(ligand_file, pocket_file):
    """
    从配体和蛋白质口袋文件构建异构图
    
    参数:
        ligand_file: 配体SDF文件路径
        pocket_file: 蛋白质口袋PDB文件路径
    
    返回:
        DGL异构图对象，包含所有节点和边的特征
    """
    # 读取分子文件
    ligand = Chem.MolFromMolFile(ligand_file)
    ligand = Chem.RemoveAllHs(ligand)  # 移除氢原子
    pocket = Chem.MolFromPDBFile(pocket_file)
    pocket = Chem.RemoveAllHs(pocket)

    # 创建异构图结构
    graph_data = {
        ('atom', 'int', 'atom'): ([], []),  # 相互作用边
        ('atom', 'ind', 'atom'): ([], [])   # 独立边（在PBCNet2.0中未使用）
    }
    G = dgl.heterograph(graph_data)

    # ====== 原子类型信息 ======
    x, type_for_mask = atom_type(ligand, pocket)
    G.add_nodes(x.shape[0])
    
    # ====== 化学信息特征 ======
    lig_atom_feature = lig_atom_featurizer(ligand)
    pock_atom_feature = lig_atom_featurizer(pocket)
    atom_scalar = torch.tensor(np.concatenate([lig_atom_feature, pock_atom_feature]), dtype=torch.float32)

    # ====== 分组信息 ======
    index, g_type, g_prop = group_complex(ligand, pocket_file)

    # ====== 坐标信息 ======
    coor_lig = ligand.GetConformer().GetPositions()  # 配体坐标
    coor_pock = pocket.GetConformer().GetPositions()  # 蛋白质坐标
    pos = np.concatenate([coor_lig, coor_pock])
    pos = torch.tensor(pos, dtype=torch.float32)
    G.nodes['atom'].data['pos'] = pos
    
    # ====== 类型1：配体内部边（距离和共价键） ======
    for i in range(len(coor_lig)):
        for j in range(i + 1, len(coor_lig)):
            dist = np.linalg.norm(coor_lig[i] - coor_lig[j])
            if dist <= 5 and dist > 0:  # 5埃截断距离
                G.add_edges(i, j, etype='int')
                G.add_edges(j, i, etype='int')
                continue

    # ====== 类型2：蛋白质内部共价键 ======
    for bond in pocket.GetBonds():
        start_atom = bond.GetBeginAtomIdx()
        end_atom = bond.GetEndAtomIdx()
        G.add_edges(start_atom + len(coor_lig), end_atom + len(coor_lig), etype='int')
        G.add_edges(end_atom + len(coor_lig), start_atom + len(coor_lig), etype='int')
        continue

    # ====== 类型3：配体-蛋白质相互作用边 ======
    for i in range(len(coor_lig)):
        for j in range(len(coor_pock)):
            dist = np.linalg.norm(coor_lig[i] - coor_pock[j])
            if dist <= 5 and dist > 0:  # 5埃截断距离
                G.add_edges(i, len(coor_lig) + j, etype='int')
                G.add_edges(len(coor_lig) + j, i, etype='int')
                continue
    
    # ====== 类型4：蛋白质内部距离边 ======
    # 找到与配体相互作用的蛋白质原子
    connected_protein_atoms = set(j for i in range(len(coor_lig)) for j in G.successors(i, etype='int') if j >= len(coor_lig))
    
    # 为相互作用的蛋白质原子添加局部距离边
    for i in connected_protein_atoms:
        for j in range(len(coor_pock)):
            dist = np.linalg.norm(coor_pock[i - len(coor_lig)] - coor_pock[j])
            if (dist <= 3) and (dist > 0) and (G.has_edges_between(i, len(coor_lig) + j, etype='int').item() is False):
                G.add_edges(i, len(coor_lig) + j, etype='int')
                G.add_edges(len(coor_lig) + j, i, etype='int')
                continue

    # ====== 边特征提取 ======
    edge_index_int = [G.edges(etype='int')[0].detach().numpy().tolist(), G.edges(etype='int')[1].detach().numpy().tolist()]
    edge_index_ind = [G.edges(etype='ind')[0].detach().numpy().tolist(), G.edges(etype='ind')[1].detach().numpy().tolist()]

    bond_type_int = bond_featurizer(ligand, pocket, edge_index_int)
    bond_type_ind = bond_featurizer(ligand, pocket, edge_index_ind)
    
    # ====== 将所有特征添加到图中 ======
    G.nodes['atom'].data['res_idx'] = index      # 残基索引
    G.nodes['atom'].data['res_type'] = g_type    # 残基类型
    G.nodes['atom'].data['res_prop'] = g_prop    # 残基属性
    G.nodes['atom'].data['x'] = x                # 原子序数
    G.nodes['atom'].data['pos'] = pos            # 原子坐标
    G.nodes['atom'].data['type'] = type_for_mask # 原子类型掩码
    G.nodes['atom'].data['atom_scalar'] = atom_scalar  # 原子标量特征
    G.edges['ind'].data['bond_scalar'] = bond_type_ind # 独立边特征
    G.edges['int'].data['bond_scalar'] = bond_type_int # 相互作用边特征
    
    return G


def graph_save(ligand_file, pock_file, pickle_save):
    """
    生成图数据并保存为pickle文件
    
    参数:
        ligand_file: 配体文件路径
        pock_file: 蛋白质口袋文件路径
        pickle_save: 输出pickle文件路径
    """
    if not (os.path.exists(ligand_file) and os.path.exists(pock_file)):
        return None

    # 生成图数据
    data = Graph_Information(ligand_file, pock_file)
    
    # 保存为pickle文件
    pickle_save = open(pickle_save, 'wb')
    pickle.dump(data, pickle_save)
    pickle_save.close()


# ==================== 输入文件生成模块 ====================

def input_G(pickles, lab, dir_):
    """
    生成PBCNet2.0的输入CSV文件
    该函数将所有配体进行两两配对，计算pIC50差值
    
    参数:
        pickles: pickle文件路径列表
        lab: 对应的pIC50标签列表
        dir_: 输出目录
    """
    N1 = []  # 配体1名称
    N2 = []  # 配体2名称
    L1 = []  # 配体1标签
    L2 = []  # 配体2标签
    L = []   # 标签差值
    D1 = []  # 配体1路径
    D2 = []  # 配体2路径
    data_list = []
    
    # 生成所有配体对的组合
    for i, pkl1 in enumerate(pickles):
        l1 = lab[i]
        if i == len(pickles) - 1:
            break
        for j, pkl2 in enumerate(pickles):
            l2 = lab[j]

            N1.append(pkl1.split('/')[-1])  # 提取文件名
            D1.append(pkl1)
            N2.append(pkl2.split('/')[-1])
            D2.append(pkl2)
            L1.append(l1)
            L2.append(l2)
            L.append(l1 - l2)  # 计算pIC50差值

        # 创建数据框
        data_list.append(pd.DataFrame({
            'lig1': N1,
            'lig2': N2,
            'Label': L,
            'Label1': L1,
            'Label2': L2,
            'dir_1': D1,
            'dir_2': D2
        }))

    # 保存为CSV文件
    pd.concat(data_list).to_csv(os.path.join(dir_, 'predict.csv'), index=0)


# ==================== 预测和评估模块 ====================

def test(logger_writer, model, device, code_path, batch_size, dir_):
    """
    使用训练好的模型进行预测
    
    参数:
        logger_writer: 日志记录器（可为None）
        model: 训练好的模型
        device: 计算设备（'cpu'或'cuda'）
        code_path: 代码路径
        batch_size: 批处理大小
        dir_: 数据目录
    
    返回:
        预测结果列表
    """
    rmse_gs = []
    model.to(device)
    
    # 读取预测数据
    df_file = pd.read_csv(os.path.join(dir_, "predict.csv"))

    # 创建数据集和数据加载器
    test_dataset = LeadOptDataset(os.path.join(dir_, "predict.csv"))
    test_dataloader = DataLoader(test_dataset,
                                 collate_fn=collate_fn,
                                 batch_size=batch_size,
                                 drop_last=False,
                                 shuffle=False,
                                 pin_memory=False)
    
    # 进行预测
    mae, rmse, mae_g, rmse_g, valid_prediction, valid_prediction_G, valid_labels, ref_1_label, val_2_label = predict(model, test_dataloader, device)
    
    return valid_prediction


# ==================== 统计分析函数 ====================

def S(X, Y):
    """计算Spearman相关系数"""
    return stats.spearmanr(X, Y)[0]


def R(X, Y):
    """计算Pearson相关系数"""
    return stats.pearsonr(X, Y)[0]


def RMSE(X, Y):
    """计算均方根误差"""
    return mean_squared_error(X, Y) ** 0.5


# ==================== 可视化模块 ====================

def plt_scatter(x, y):
    """
    绘制预测值与实验值的散点图
    
    参数:
        x: 实验值
        y: 预测值
    
    返回:
        slope: 回归直线斜率
        intercept: 回归直线截距
        r_squared: R²值
    """
    fig, axs = plt.subplots(1, 1, figsize=(13, 10))
    fig.dpi = 600

    # 绘制散点图
    axs.scatter(x, y, alpha=1, s=100, c=['#138787'], zorder=2)

    # 计算线性回归参数
    parameter = np.polyfit(x, y, 1)
    y2 = parameter[0] * np.array(x) + parameter[1]
    slope = parameter[0]
    intercept = parameter[1]
    
    # 计算R²值
    from scipy.stats import pearsonr
    r_value = pearsonr(x, y)[0]
    r_squared = r_value ** 2
    
    # 打印统计信息
    print(f"斜率: {slope:.4f}")
    print(f"截距: {intercept:.4f}")
    print(f"R²: {r_squared:.4f}")
    print(f"回归方程: y = {slope:.4f}x + {intercept:.4f}")

    # 绘制回归直线
    axs.plot(x, y2, ls="-", linewidth=2, alpha=0.6, c='k')
    axs.tick_params(labelsize=12)

    # 在图上显示R²和回归方程
    equation_text = f'y = {slope:.3f}x + {intercept:.3f}\nR² = {r_squared:.3f}'
    axs.text(0.05, 0.95, equation_text, transform=axs.transAxes, 
             fontsize=16, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # 设置坐标轴标签和标题
    axs.set_ylabel("Pred. pIC50", fontsize=40)
    axs.set_xlabel("Exp. pIC50", fontsize=40)
    axs.set_title('Toy data', fontsize=40)

    plt.tight_layout()
    plt.style.use("ggplot")
    plt.show()
    
    # 返回统计值供后续使用
    return slope, intercept, r_squared


# ==================== 主程序入口 ====================

def main():
    """
    主函数：解析命令行参数并执行完整的预测流程
    
    使用方法:
        python run.py <data_directory> [--code_path <path>] [--batch_size <size>]
    
    示例:
        python run.py ./toy_data --code_path ./PBCNet2.0 --batch_size 8
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='PBCNet2.0 蛋白质-配体结合亲和力预测工具')
    parser.add_argument('dir', help='数据目录路径，包含 .sdf 和 .pdb 文件')
    parser.add_argument('--code_path', default='c:/Users/ErickTom/PBCNet2.0', 
                       help='代码路径，包含模型文件 (默认: c:/Users/ErickTom/PBCNet2.0)')
    parser.add_argument('--batch_size', type=int, default=8, 
                       help='批处理大小 (默认: 8)')
    
    args = parser.parse_args()
    
    # ====== 输入验证 ======
    if not os.path.exists(args.dir):
        print(f"错误：目录 {args.dir} 不存在")
        return
    
    model_path = os.path.join(args.code_path, 'PBCNet2.0.pth')
    if not os.path.exists(model_path):
        print(f"错误：模型文件 {model_path} 不存在")
        return
    
    print(f"开始处理目录: {args.dir}")
    print(f"使用模型路径: {args.code_path}")
    print(f"批处理大小: {args.batch_size}")
    
    # ====== 设置系统路径 ======
    sys.path.append(f"{args.code_path}/model_code/")
    
    # ====== 步骤1: 提取蛋白质口袋 ======
    print("\n步骤 1: 提取蛋白质口袋...")
    sdfs = [os.path.join(args.dir, i) for i in os.listdir(args.dir) if i.endswith('.sdf')]
    for sdf in sdfs:
        pocket_extract([sdf], os.path.join(args.dir, 'protein.pdb'))
    
    # ====== 步骤2: 生成图数据 ======
    print("\n步骤 2: 生成图数据...")
    data_list = []
    for sdf in sdfs:
        data_list.append([sdf, os.path.join(args.dir, 'pocket.pdb'), sdf.replace('.sdf', '.pkl')])

    for ligand_file, pock_file, pickle_save in data_list:
        graph_save(ligand_file, pock_file, pickle_save)
    
    # ====== 步骤3: 生成输入CSV ======
    print("\n步骤 3: 生成输入 CSV...")
    names = [os.path.join(args.dir, i) for i in os.listdir(args.dir) if i.endswith('.pkl')]
    ic50 = [7.47, 8.52, 8.3, 7.77, 7.6, 8.1]  # 示例pIC50值，实际使用时需要动态获取
    input_G(names, ic50, args.dir)
    
    # ====== 步骤4: 加载模型并预测 ======
    print("\n步骤 4: 加载模型并进行预测...")
    model = torch.load(model_path, map_location=torch.device('cpu'))
    pre = test(None, model, 'cpu', args.code_path, args.batch_size, args.dir)
    
    # ====== 步骤5: 保存预测结果 ======
    print("\n步骤 5: 保存预测结果...")
    df_file = pd.read_csv(os.path.join(args.dir, "predict.csv"))
    df_file['pre'] = pre
    df_file.to_csv(os.path.join(args.dir, "predict.csv"), index=0)
    
    # ====== 步骤6: 显示统计信息 ======
    print("\n预测完成！统计信息：")
    print(f"Spearman 相关系数: {S(df_file['Label'], df_file['pre']):.4f}")
    print(f"Pearson 相关系数: {R(df_file['Label'], df_file['pre']):.4f}")
    print(f"RMSE: {RMSE(df_file['Label'], df_file['pre']):.4f}")
    
    # ====== 步骤7: 生成散点图 ======
    print("\n生成预测结果散点图...")
    plt_scatter(df_file['Label'], df_file['pre'])
    
    print(f"\n结果已保存到: {os.path.join(args.dir, 'predict.csv')}")
    print("预测流程完成！")


# ==================== 程序入口点 ====================
if __name__ == '__main__':
    """
    程序入口点
    
    当直接运行此脚本时，将执行main()函数
    支持命令行参数：
    - 位置参数：数据目录路径
    - --code_path：模型和代码路径（可选）
    - --batch_size：批处理大小（可选）
    """
    main()