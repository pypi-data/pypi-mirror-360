import torch
import torch.nn as nn
import numpy as np
import scipy.io as scio
import cv2
import matplotlib.pyplot as plt
from torch.autograd import Variable
from models import get_model  # 确保 models.py 存在
import os.path as osp
import os
import glob

import pandas as pd
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from plotnine import *
from PIL import Image
import statistics

class LayerActivations:
    def __init__(self, model, layer_num=None):
        if layer_num is not None:
            self.hook = model[layer_num].register_forward_hook(self.hook_fn)
        else:
            self.hook = model.register_forward_hook(self.hook_fn)
        self.features = None

    def hook_fn(self, module, input, output):
        self.features = output[0].cpu()

    def remove(self):
        self.hook.remove()

class dulrs_class:
    def __init__(self, model_name,model_path, use_cuda=True, num_stages=6):
        """

        :param model_path: 预训练模型路径 (.pth)
        :param use_cuda: 是否使用 GPU 计算
        """
        self.device = torch.device("cuda" if use_cuda and torch.cuda.is_available() else "cpu")
        self.model = self.load_model(model_name,model_path)
        self.num_stages = num_stages  # 存储阶段数
        
    def load_model(self, model_name ,model_path):
        print(f"Loading model from {model_path}...")
        net = get_model(model_name)  # 你可以更改模型架构
        checkpoint = torch.load(model_path, map_location=self.device)
        net.load_state_dict(checkpoint)
        net.to(self.device)
        net.eval()
        print("Model loaded successfully!")
        return net
    
    def preprocess_image(self, img_path):
        img = cv2.resize(cv2.imread(osp.join(img_path), 0), (256, 256)).astype(int)
        org = img.reshape((1, 1, 256, 256))

        img = np.float32(cv2.resize(img, (256, 256))) / 255.
        tmp = img.reshape((1, 1, 256, 256))
        input = torch.from_numpy(tmp)
        input = input.to(self.device) 
        return input, org
    
    def get_img_norm_cfg(self,dataset_name ):
        if dataset_name == 'CHASEDB1':
            img_norm_cfg = {'mean': 59.87125015258789, 'std': 46.84417724609375}
        elif dataset_name == 'DRIVE':
            img_norm_cfg = {'mean': 83.59488677978516, 'std': 54.175140380859375}
        elif dataset_name == 'STARE':
            img_norm_cfg = {'mean': 98.16558837890625, 'std': 52.33002853393555}
        return img_norm_cfg

    def preprocess_image_vs(self, img_path,dataset_name, target_size=(256, 256), pad_to_multiple=32):
        """
    血管图像预处理，默认支持 STARE/DRIVE/CHASEDB1 格式
    参数：
        img_path: 图像路径
        target_size: 目标 resize 尺寸（宽，高）
        pad_to_multiple: 是否填充图像使其成为指定倍数（如32），若为None则不填充
    返回：
        input: torch.Tensor, shape: [1, 1, H, W]
        org: numpy.ndarray, shape: [1, 1, H, W]，原始未归一化图像
        """

        # 1. 读取为灰度图像
        img = cv2.imread(osp.join(img_path), 0).astype(np.float32)  # shape: [H, W]

        # 2. Resize 到 target_size（如 (256, 256)）
        img = cv2.resize(img, target_size)

        # 3. 保存原始图像（int型）
        org = img.astype(np.uint8).reshape((1, 1, target_size[1], target_size[0]))

        img_norm_cfg = self.get_img_norm_cfg(dataset_name)

        # 4. 归一化：/255 或标准化
        if img_norm_cfg is not None:
            mean = img_norm_cfg['mean']
            std = img_norm_cfg['std']
            img = (img - mean) / std
        else:
            img = img / 255.0

        # 5. Optional: Padding 到32的倍数
        if pad_to_multiple:
            h, w = img.shape
            pad_h = (pad_to_multiple - h % pad_to_multiple) % pad_to_multiple
            pad_w = (pad_to_multiple - w % pad_to_multiple) % pad_to_multiple
            img = np.pad(img, ((0, pad_h), (0, pad_w)), mode='constant')
            org = np.pad(org[0, 0], ((0, pad_h), (0, pad_w)), mode='constant')
            org = org.reshape((1, 1, img.shape[0], img.shape[1]))

        # 6. 转换为 Tensor，添加维度：[1, 1, H, W]
        img_tensor = torch.from_numpy(img).unsqueeze(0).unsqueeze(0).float().to(self.device)

        return img_tensor, org


    def extract_layer_features(self, input_tensor, layer):
        activation_extractor = LayerActivations(layer)
        with torch.no_grad():
            _ = self.model(input_tensor)  # 进行前向传播
        activation_extractor.remove()
        return activation_extractor.features.numpy().squeeze()  # 转换为 numpy 格式
    
    def heatmap(self, img_path, data_name,dataset_name=None, data_type=None, output_mat=None, output_png=None):
        if data_type is not None:
            input_tensor, org = self.preprocess_image_vs(img_path, dataset_name)
        else:
            input_tensor, org = self.preprocess_image(img_path)
        heatmaps_back = []
        heatmaps_sparse = []
        heatmaps_merge = []
        for i in range(self.num_stages):
            feature_map_back = self.extract_layer_features(input_tensor, self.model.decos[i].lowrank)
            feature_map_sparse = self.extract_layer_features(input_tensor, self.model.decos[i].sparse)
            feature_map_merge = self.extract_layer_features(input_tensor, self.model.decos[i].merge)
            heatmaps_back.append(feature_map_back)
            heatmaps_sparse.append(feature_map_sparse)
            heatmaps_merge.append(feature_map_merge)
        
        print(f"Process data: {img_path}")

        for i in range(self.num_stages):
            heatmap_back = heatmaps_back[i]
            heatmap_back = np.maximum(heatmap_back, 0)
            heatmap_back = np.flipud(heatmap_back)
            heatmap_sparse = heatmaps_sparse[i]
            heatmap_sparse = np.maximum(heatmap_sparse, 0)
            heatmap_sparse = np.flipud(heatmap_sparse)
            heatmap_merge = heatmaps_merge[i]
            heatmap_merge = np.maximum(heatmap_merge, 0)
            heatmap_merge = np.flipud(heatmap_merge)

            # 保存为 .mat 文件
            if output_mat:
                os.makedirs(osp.join(output_mat,f"{data_name}"), exist_ok= True)
                path_back = osp.join(output_mat,f"{data_name}/back-{i}.mat")
                scio.savemat(path_back, {'back': heatmap_back})

                path_sparse = osp.join(output_mat,f"{data_name}/sparse-{i}.mat")
                scio.savemat(path_sparse, {'sparse': heatmap_sparse})

                path_merge = osp.join(output_mat,f"{data_name}/merge-{i}.mat")
                scio.savemat(path_merge, {'merge': heatmap_merge})
                print(f"Saved heatmap as .mat: {output_mat}")

            # 可视化并保存 .png
            
            if output_png:
                os.makedirs(osp.join(output_png,f"{data_name}"), exist_ok= True)
                plt.figure(figsize=(6, 6))
                
                plt.pcolor(heatmap_back, cmap='jet', shading='auto')
                plt.axis('off')
                path_back = osp.join(output_png,f"{data_name}/back-{i}.png")
                plt.savefig(path_back, bbox_inches='tight', pad_inches=0)
                plt.close()
                print(f"Saved heatmap as .png: {path_back}")

                plt.figure(figsize=(6, 6))
                plt.pcolor(heatmap_sparse, cmap='jet', shading='auto')
                plt.axis('off')
                path_sparse = osp.join(output_png,f"{data_name}/sparse-{i}.png")
                plt.savefig(path_sparse, bbox_inches='tight', pad_inches=0)
                plt.close()
                print(f"Saved heatmap as .png: {path_sparse}")

                plt.figure(figsize=(6, 6))
                plt.pcolor(heatmap_merge, cmap='jet', shading='auto')
                plt.axis('off')
                path_merge = osp.join(output_png,f"{data_name}/merge-{i}.png")
                plt.savefig(path_merge, bbox_inches='tight', pad_inches=0)
                plt.close()
                print(f"Saved heatmap as .png: {path_merge}")

    def lowrank_cal(self, img_path,model_name, data_name, save_dir):
        y = range(self.num_stages + 1)
        matrix = [[] for _ in y]
        path = osp.join(img_path,f"*.png")
        f = glob.iglob(path)
        # print(f)
        
        for png in f:
            input, org = self.preprocess_image(png)
            backs, sparses, merges = [], [], []
            for i in range(self.num_stages):
                back = self.extract_layer_features(input, self.model.decos[i].lowrank)
                back[back < 0] = 0
                u,s,v = np.linalg.svd(back)
                matrix[i].append(s)
            u, s, v = np.linalg.svd(org)
            matrix[self.num_stages].append(s)
        
        save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for i in range(self.num_stages + 1):
            m = np.mean(matrix[i], axis=0)
            std = np.std(matrix[i], axis=0)
            
            # 保存均值
            scio.savemat('{}/{}_{}_svd_m{}.mat'.format(
                save_dir, model_name, data_name, i+1), 
                {'s': m}
            )
            
            # 保存标准差
            scio.savemat('{}/{}_{}_svd_std{}.mat'.format(
                save_dir, model_name, data_name, i+1), 
                {'s': std}
            )
    def generate_colors(self, num_stages):
        # 基础颜色列表
        base_colors = ['#4daf4a', '#e41a1c', '#377eb8', '#cd79ff', '#ffd927', '#999999', '#ff7400']
        if num_stages + 1 <= len(base_colors):
            return base_colors
        
        # 如果需要更多颜色，随机生成
        import random
        extra_colors = []
        for _ in range(num_stages + 1 - len(base_colors)):
            # 生成随机的RGB颜色
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            extra_colors.append('#{:02x}{:02x}{:02x}'.format(r, g, b))
        
        return base_colors + extra_colors
    def lowrank_draw(self, model_name, data_name,mat_dir, save_dir):
        # ✅ Step 0: 确保保存路径存在
        os.makedirs(save_dir, exist_ok=True)
        # Load data from .mat files
        stage_data = []
        for i in range(1, self.num_stages + 2):
            mat_data = sio.loadmat('{}/{}_{}_svd_m{}.mat'.format(mat_dir, model_name, data_name, i))
            stage_data.append(mat_data['s'].squeeze())
        
        # 创建主图数据框
        ranks = []
        values = []
        stages = []
        for i, data in enumerate(stage_data[:-1]):
            ranks.extend(range(1, len(data) + 1))
            values.extend(list(data))
            stages.extend(['Stage {}'.format(i + 1)] * len(data))
        # 添加原始数据
        ranks.extend(range(1, len(stage_data[-1]) + 1))
        values.extend(list(stage_data[-1]))
        stages.extend(['Org'] * len(stage_data[-1]))
        
        data_main = pd.DataFrame({
            'Rank': ranks,
            'Singular Value': values,
            'Stage': stages
        })

        inset_stages = min(4, self.num_stages)
        ranks_inset = []
        values_inset = []
        stages_inset = []
        for i in range(inset_stages):
            ranks_inset.extend(range(1, len(stage_data[i]) + 1))
            values_inset.extend(list(stage_data[i]))
            stages_inset.extend(['Stage {}'.format(i + 1)] * len(stage_data[i]))
        
        data_inset = pd.DataFrame({
            'Rank': ranks_inset,
            'Singular Value': values_inset,
            'Stage': stages_inset
        })
        
        colors = self.generate_colors(self.num_stages)
        stage_order = ['Stage {}'.format(i + 1) for i in range(self.num_stages)] + ['Org']
            # Create the main plot using plotnine
        main_plot = (ggplot(data_main, aes(x='Rank', y='Singular Value', color='Stage')) +
                     geom_point(size=3) +
                     geom_line(size=1.5) +
                     labs(title='Low-rankness Measurement Across Stages', x='Rank', y='Singular Value') +
                     scale_x_continuous(limits=(0.5, 10.5), breaks=list(range(1, 11))) +
                     scale_y_continuous(limits=(0, 4*10**4)) +
                     scale_color_manual(values=colors, breaks=stage_order) +
                     theme(
                         figure_size=(8, 6),
                         text=element_text(size=16,family='DejaVu Sans'),
                         plot_title=element_text(size=20, family='DejaVu Sans', ha='center'),
                         panel_grid_major=element_line(color='white', size=1, linetype='--'),
                         panel_grid_minor=element_line(color='white', size=0.5, linetype=':'),
                         axis_text=element_text(size=18),
                         axis_title=element_text(size=18),
                         legend_title=element_blank(),
                         legend_text=element_text(size=16),
                         legend_position=(0.85, 0.35),
                         legend_background=element_rect(fill='white', color='grey', alpha=0.4, size=0.7),
                         legend_direction='vertical',
                         legend_box_margin=5,
                     ))

        # Create the inset plot using plotnine without legend and setting xlim
        inset_plot = (ggplot(data_inset, aes(x='Rank', y='Singular Value', color='Stage')) +
                      geom_point(size=5) +
                      geom_line(size=3) +
                      scale_x_continuous(limits=(0.5, 10.5), breaks=list(range(1, 11))) +
                      labs(title='Zoom In For Initial Stages') +
                      scale_color_manual(values=colors[:inset_stages]) +
                      theme_void() +
                      theme(
                          plot_title=element_text(size=20, family='DejaVu Sans', ha='center'),
                          panel_grid_major=element_line(color='grey', linetype='--', size=0.5),
                          panel_grid_minor=element_line(color='grey', linetype=':', size=0.25),
                          axis_text=element_text(size=18),
                          legend_position='none'
                      ))

        # Save the plots as images
        main_plot.save("{}/{}_{}_main_plot.png".format(save_dir,model_name,data_name), dpi=400)
        inset_plot.save("{}/{}_{}_inset_plot.png".format(save_dir,model_name,data_name), dpi=400)

        # Combine the images using PIL and matplotlib
        main_img = Image.open("{}/{}_{}_main_plot.png".format(save_dir,model_name,data_name))
        inset_img = Image.open("{}/{}_{}_inset_plot.png".format(save_dir,model_name,data_name))

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(main_img, aspect='auto')
        ax.axis('off')

        # Create and position the inset plot
        left, bottom, width, height = [0.55, 0.5, 0.3, 0.3]
        ax_inset = fig.add_axes([left, bottom, width, height])
        ax_inset.imshow(inset_img, aspect='auto')
        ax_inset.axis('off')

        # Adjust y-axis to use scientific notation
        formatter = ScalarFormatter()
        formatter.set_powerlimits((0, 0))
        ax.yaxis.set_major_formatter(formatter)
        ax_inset.yaxis.set_major_formatter(formatter)

        save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        plt.savefig("{}/{}_{}_lowrankness.png".format(save_dir,model_name,data_name), dpi=400, bbox_inches='tight')
        # plt.show()
    
    def sparsity_cal(self, img_path, model_name, data_name, save_dir):
        # ✅ Step 0: 确保保存路径存在
        os.makedirs(save_dir, exist_ok=True)
        # 初始化矩阵以存储每个阶段的数据
        matrix = [[] for _ in range(self.num_stages)]
        path = osp.join(img_path, f"*.png")
        f = glob.iglob(path)
        print(f)
        
        # 收集每个图像的稀疏性数据
        for png in f:
            print(png)
            input, org = self.preprocess_image(png)
            backs, sparses, merges = [], [], []
            for i in range(self.num_stages):
                sparsity = self.extract_layer_features(input, self.model.decos[i].sparse)
                sparsity[sparsity < 0] = 0
                l0_norms = np.sum(sparsity != 0) / (256*256)
                matrix[i].append(l0_norms)
        
        # 计算每个阶段的均值和标准差
        means = []
        stdevs = []
        for i in range(self.num_stages):
            if len(matrix[i]) > 0:
                mean_val = statistics.mean(matrix[i])
            else:
                mean_val = 0
            if len(matrix[i]) > 0:
                std_val = statistics.stdev(matrix[i])
            else:
                std_val = 0
            means.append(mean_val)
            stdevs.append(std_val)
            print(f"Stage {i+1} - Mean: {mean_val}")
        
        print('----------')
        for i in range(self.num_stages):
            print(f"Stage {i+1} - Std: {stdevs[i]}")
        
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 保存每个阶段的均值和标准差
        for i in range(self.num_stages):
            # 保存均值
            scio.savemat(
                '{}/{}_{}_svd_m{}.mat'.format(save_dir, model_name, data_name, i+1),
                {'sparsity': means[i]}
            )
            # 保存标准差
            scio.savemat(
                '{}/{}_{}_svd_std{}.mat'.format(save_dir, model_name, data_name, i+1),
                {'sparsity': stdevs[i]}
            )