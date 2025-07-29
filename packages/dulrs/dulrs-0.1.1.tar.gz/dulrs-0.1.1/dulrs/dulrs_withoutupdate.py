import torch
import torch.nn as nn
import numpy as np
import scipy.io as scio
import cv2
import matplotlib.pyplot as plt
from torch.autograd import Variable
from export import get_model  # 确保 models.py 存在
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
    """ 用于提取特定层的特征图 """
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
    def __init__(self, model_name,model_path, use_cuda=True):
        """
        初始化热力图生成器

        :param model_path: 预训练模型路径 (.pth)
        :param use_cuda: 是否使用 GPU 计算
        """
        self.device = torch.device("cuda" if use_cuda and torch.cuda.is_available() else "cpu")
        self.model = self.load_model(model_name,model_path)
        
    def load_model(self, model_name ,model_path):
        """
        加载模型

        :param model_path: 预训练模型路径
        :return: 加载的 PyTorch 模型
        """
        print(f"Loading model from {model_path}...")
        net = get_model(model_name)  # 你可以更改模型架构
        checkpoint = torch.load(model_path, map_location=self.device)
        net.load_state_dict(checkpoint)
        net.to(self.device)
        net.eval()
        print("Model loaded successfully!")
        return net
    
    def preprocess_image(self, img_path):
        """
        预处理输入图像

        :param img_path: 输入图像路径
        :return: 预处理后的 PyTorch Tensor
        """
        img = cv2.resize(cv2.imread(osp.join(img_path), 0), (256, 256)).astype(int)
        org = img.reshape((1, 1, 256, 256))

        img = np.float32(cv2.resize(img, (256, 256))) / 255.
        tmp = img.reshape((1, 1, 256, 256))
        input = torch.from_numpy(tmp)
        return input, org

    def extract_layer_features(self, input_tensor, layer):
        """
        通过 LayerActivations 提取指定层的特征图

        :param input_tensor: 预处理后的图像 Tensor
        :param layer: 需要提取的模型层
        :return: 该层的输出特征图
        """
        activation_extractor = LayerActivations(layer)
        with torch.no_grad():
            _ = self.model(input_tensor)  # 进行前向传播
        activation_extractor.remove()
        return activation_extractor.features.numpy().squeeze()  # 转换为 numpy 格式
    
    def heatmap(self, img_path, data_name ,output_mat=None, output_png=None):
        """
        生成热力图并保存

        :param img_path: 输入图像路径
        :param data_name: 测试数据名
        :param output_mat: 输出 .mat 文件路径（可选）
        :param output_png: 输出 .png 文件路径（可选）
        """
        input_tensor, org = self.preprocess_image(img_path)

        # 提取不同层的特征图
        heatmaps_back = []
        heatmaps_sparse = []
        heatmaps_merge = []
        #这里额外做了变动
        for i in range(6):  # 提取 6 层的特征 
            feature_map_back = self.extract_layer_features(input_tensor, self.model.decos[i].lowrank)
            feature_map_sparse = self.extract_layer_features(input_tensor, self.model.decos[i].sparse)
            feature_map_merge = self.extract_layer_features(input_tensor, self.model.decos[i].merge)
            heatmaps_back.append(feature_map_back)
            heatmaps_sparse.append(feature_map_sparse)
            heatmaps_merge.append(feature_map_merge)
        
        print(f"Process data: {img_path}")

        #这里额外做了变动
        for i in range(6):
            # 取第一层特征作为热力图
            heatmap_back = heatmaps_back[i]
            heatmap_back = np.maximum(heatmap_back, 0)  # ReLU 处理，防止负值
            heatmap_back = np.flipud(heatmap_back)  # 翻转，使方向一致
            heatmap_sparse = heatmaps_sparse[i]
            heatmap_sparse = np.maximum(heatmap_sparse, 0)  # ReLU 处理，防止负值
            heatmap_sparse = np.flipud(heatmap_sparse)  # 翻转，使方向一致
            heatmap_merge = heatmaps_merge[i]
            heatmap_merge = np.maximum(heatmap_merge, 0)  # ReLU 处理，防止负值
            heatmap_merge = np.flipud(heatmap_merge)  # 翻转，使方向一致

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
                #plt.colorbar()
                path_back = osp.join(output_png,f"{data_name}/back-{i}.png")
                plt.savefig(path_back, bbox_inches='tight', pad_inches=0)
                plt.close()
                print(f"Saved heatmap as .png: {path_back}")

                plt.figure(figsize=(6, 6))
                plt.pcolor(heatmap_sparse, cmap='jet', shading='auto')
                plt.axis('off')
                #plt.colorbar()
                path_sparse = osp.join(output_png,f"{data_name}/sparse-{i}.png")
                plt.savefig(path_sparse, bbox_inches='tight', pad_inches=0)
                plt.close()
                print(f"Saved heatmap as .png: {path_sparse}")

                plt.figure(figsize=(6, 6))
                plt.pcolor(heatmap_merge, cmap='jet', shading='auto')
                plt.axis('off')
                #plt.colorbar()
                path_merge = osp.join(output_png,f"{data_name}/merge-{i}.png")
                plt.savefig(path_merge, bbox_inches='tight', pad_inches=0)
                plt.close()
                print(f"Saved heatmap as .png: {path_merge}")

    def lowrank_cal(self, img_path,model_name, data_name, save_dir):
        y = range(7)
        matrix = [[] for _ in y]
        path = osp.join(img_path,f"*.png")
        f = glob.iglob(path)
        print(f)
        
        for png in f:
            print(png)
            input, org = self.preprocess_image(png)
            # backs, bh, bc, sparses, merges = [], [], [], [], []
            backs, sparses, merges = [], [], []
            for i in range(6):
                # back, bh, bc, = mid_rst(net, net.decos[i].lowrank, input)
                back = self.extract_layer_features(input, self.model.decos[i].lowrank)
                back[back < 0] = 0
                u,s,v = np.linalg.svd(back)
                matrix[i].append(s)
            u, s, v = np.linalg.svd(org)
            matrix[6].append(s) #最后一位用来储存原始图片的奇艺值
        
        save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        #这里额外做了变动
        m1 = np.mean(matrix[0], axis=0)
        scio.savemat('{}/{}_{}_svd_m1.mat'.format(save_dir,model_name,data_name), {'s': m1})
        m2 = np.mean(matrix[1], axis=0)
        scio.savemat('{}/{}_{}_svd_m2.mat'.format(save_dir,model_name,data_name), {'s': m2})
        m3 = np.mean(matrix[2], axis=0)
        scio.savemat('{}/{}_{}_svd_m3.mat'.format(save_dir,model_name,data_name), {'s': m3})
        m4 = np.mean(matrix[3], axis=0)
        scio.savemat('{}/{}_{}_svd_m4.mat'.format(save_dir,model_name,data_name), {'s': m4})
        m5 = np.mean(matrix[4], axis=0)
        scio.savemat('{}/{}_{}_svd_m5.mat'.format(save_dir,model_name,data_name), {'s': m5})
        m6 = np.mean(matrix[5], axis=0)
        scio.savemat('{}/{}_{}_svd_m6.mat'.format(save_dir,model_name,data_name), {'s': m6})
        m7 = np.mean(matrix[6], axis=0)
        scio.savemat('{}/{}_{}_svd_m7.mat'.format(save_dir,model_name,data_name), {'s': m7})

        std1 = np.std(matrix[0], axis=0)
        scio.savemat('{}/{}_{}_svd_std1.mat'.format(save_dir,model_name,data_name), {'s': std1})
        std2 = np.std(matrix[1], axis=0)
        scio.savemat('{}/{}_{}_svd_std2.mat'.format(save_dir,model_name,data_name), {'s': std2})
        std3 = np.std(matrix[2], axis=0)
        scio.savemat('{}/{}_{}_svd_std3.mat'.format(save_dir,model_name,data_name), {'s': std3})
        std4 = np.std(matrix[3], axis=0)
        scio.savemat('{}/{}_{}_svd_std4.mat'.format(save_dir,model_name,data_name), {'s': std4})
        std5 = np.std(matrix[4], axis=0)
        scio.savemat('{}/{}_{}_svd_std5.mat'.format(save_dir,model_name,data_name), {'s': std5})
        std6 = np.std(matrix[5], axis=0)
        scio.savemat('{}/{}_{}_svd_std6.mat'.format(save_dir,model_name,data_name), {'s': std6})
        std7 = np.std(matrix[6], axis=0)
        scio.savemat('{}/{}_{}_svd_std7.mat'.format(save_dir,model_name,data_name), {'s': std7})

    def lowrank_draw(self,model_name, data_name,mat_dir, save_dir):
        # Load data from .mat files
        mat_data = sio.loadmat('{}/{}_{}_svd_m1.mat'.format(mat_dir,model_name,data_name))
        s0 = mat_data['s'].squeeze()
        mat_data = sio.loadmat('{}/{}_{}_svd_m2.mat'.format(mat_dir,model_name,data_name))
        s1 = mat_data['s'].squeeze()
        mat_data = sio.loadmat('{}/{}_{}_svd_m3.mat'.format(mat_dir,model_name,data_name))
        s2 = mat_data['s'].squeeze()
        mat_data = sio.loadmat('{}/{}_{}_svd_m4.mat'.format(mat_dir,model_name,data_name))
        s3 = mat_data['s'].squeeze()
        mat_data = sio.loadmat('{}/{}_{}_svd_m5.mat'.format(mat_dir,model_name,data_name))
        s4 = mat_data['s'].squeeze()
        mat_data = sio.loadmat('{}/{}_{}_svd_m6.mat'.format(mat_dir,model_name,data_name))
        s5 = mat_data['s'].squeeze()
        mat_data = sio.loadmat('{}/{}_{}_svd_m7.mat'.format(mat_dir,model_name,data_name))
        org1 = mat_data['s'].squeeze()
        # Create data frame for main plot
        data_main = pd.DataFrame({
            'Rank': list(range(1, len(s0) + 1)) + list(range(1, len(s1) + 1)) + list(range(1, len(s2) + 1)) +
                    list(range(1, len(s3) + 1)) + list(range(1, len(s4) + 1)) + list(range(1, len(s5) + 1)) + list(range(1, len(org1) + 1)),
            'Singular Value': list(s0) + list(s1) + list(s2) + list(s3) + list(s4) + list(s5) + list(org1),
            'Stage': ['Stage 1'] * len(s0) + ['Stage 2'] * len(s1) + ['Stage 3'] * len(s2) +
                     ['Stage 4'] * len(s3) + ['Stage 5'] * len(s4) + ['Stage 6'] * len(s5) + ['Org'] * len(org1)
        })

        # Create data frame for inset plot
        data_inset = pd.DataFrame({
            'Rank': list(range(1, len(s0) + 1)) + list(range(1, len(s1) + 1)) + list(range(1, len(s2) + 1)) + list(range(1, len(s3) + 1)),
            'Singular Value': list(s0) + list(s1) + list(s2) + list(s3),
            'Stage': ['Stage 1'] * len(s0) + ['Stage 2'] * len(s1) + ['Stage 3'] * len(s2) + ['Stage 4'] * len(s3)
        })

        # Define the colors and the correct order of the legend
        colors = ['#4daf4a', '#e41a1c', '#377eb8', '#cd79ff', '#ffd927', '#999999', '#ff7400']
        stage_order = ['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'Stage 5', 'Stage 6', 'Org']

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
                         text=element_text(size=16,family='Times New Roman'),
                         plot_title=element_text(size=20, family='Times New Roman', ha='center'),
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
                      labs(title='Zoom In For Initial Four Stages') +
                      scale_color_manual(values=colors, breaks=stage_order) +
                      theme_void() +
                      theme(
                          plot_title=element_text(size=20, family='Times New Roman', ha='center'),
                          panel_grid_major=element_line(color='grey', linetype='--', size=0.5),
                          panel_grid_minor=element_line(color='grey', linetype=':', size=0.25),
                          axis_text=element_text(size=18),
                          legend_position='none'
                      ))

        # Save the plots as images
        main_plot.save("main_plot.png", dpi=400)
        inset_plot.save("inset_plot.png", dpi=400)

        # Combine the images using PIL and matplotlib
        main_img = Image.open("main_plot.png")
        inset_img = Image.open("inset_plot.png")

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
        plt.show()
    
    def sparsity_cal(self, img_path,model_name, data_name, save_dir):
        y = range(6)
        matrix = [[] for _ in y]
        path = osp.join(img_path,f"*.png")
        f = glob.iglob(path)
        print(f)
        
        for png in f:
            print(png)
            input, org = self.preprocess_image(png)
            # backs, bh, bc, sparses, merges = [], [], [], [], []
            backs, sparses, merges = [], [], []
            for i in range(6):
                # back, bh, bc, = mid_rst(net, net.decos[i].lowrank, input)
                sparsity = self.extract_layer_features(input, self.model.decos[i].sparse)
                sparsity[sparsity < 0] = 0
                l0_norms = np.sum(sparsity != 0)/ (256*256)
                matrix[i].append(l0_norms)
            

        m1 = statistics.mean(matrix[0])
        m2 = statistics.mean(matrix[1])
        m3 = statistics.mean(matrix[2])
        m4 = statistics.mean(matrix[3])
        m5 = statistics.mean(matrix[4])
        m6 = statistics.mean(matrix[5])

        std_1 = statistics.stdev(matrix[0])
        std_2 = statistics.stdev(matrix[1])
        std_3 = statistics.stdev(matrix[2])
        std_4 = statistics.stdev(matrix[3])
        std_5 = statistics.stdev(matrix[4])
        std_6 = statistics.stdev(matrix[5])
        
        print(m1)
        print(m2)
        print(m3)
        print(m4)
        print(m5)
        print(m6)
        print('----------')

        print(std_1)
        print(std_2)
        print(std_3)
        print(std_4)
        print(std_5)
        print(std_6)

        save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        scio.savemat('{}/{}_{}_svd_m1.mat'.format(save_dir,model_name,data_name), {'sparsity': m1})
        scio.savemat('{}/{}_{}_svd_m2.mat'.format(save_dir,model_name,data_name), {'sparsity': m2})
        scio.savemat('{}/{}_{}_svd_m3.mat'.format(save_dir,model_name,data_name), {'sparsity': m3})
        scio.savemat('{}/{}_{}_svd_m4.mat'.format(save_dir,model_name,data_name), {'sparsity': m4})
        scio.savemat('{}/{}_{}_svd_m5.mat'.format(save_dir,model_name,data_name), {'sparsity': m5})
        scio.savemat('{}/{}_{}_svd_m6.mat'.format(save_dir,model_name,data_name), {'sparsity': m6})

        scio.savemat('{}/{}_{}_svd_std1.mat'.format(save_dir,model_name,data_name), {'sparsity': std_1})
        scio.savemat('{}/{}_{}_svd_std2.mat'.format(save_dir,model_name,data_name), {'sparsity': std_2})
        scio.savemat('{}/{}_{}_svd_std3.mat'.format(save_dir,model_name,data_name), {'sparsity': std_3})
        scio.savemat('{}/{}_{}_svd_std4.mat'.format(save_dir,model_name,data_name), {'sparsity': std_4})
        scio.savemat('{}/{}_{}_svd_std5.mat'.format(save_dir,model_name,data_name), {'sparsity': std_5})
        scio.savemat('{}/{}_{}_svd_std6.mat'.format(save_dir,model_name,data_name), {'sparsity': std_6})