#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StrongSort ID映射功能调试脚本

该脚本用于测试和调试StrongSort追踪器中的目标ID映射功能
包含多种测试场景，帮助验证ID映射逻辑的正确性
"""

import numpy as np
import cv2
from pathlib import Path
import sys
import os

# 添加项目路径到sys.path
sys.path.append(str(Path(__file__).parent))

from boxmot.trackers.strongsort.strongsort import StrongSort


class IDMappingDebugger:
    """
    ID映射调试器类
    
    用于测试StrongSort的ID映射功能，提供多种测试场景
    """
    
    def __init__(self):
        """
        初始化调试器
        """
        self.tracker = None
        self.test_image = None
        
    def setup_tracker(self):
        """
        设置StrongSort追踪器
        
        Note:
            使用默认参数初始化追踪器，适用于调试测试
        """
        print("=== 初始化StrongSort追踪器 ===")
        
        # 创建虚拟的reid权重路径（用于测试）
        reid_weights = Path("./boxmot/appearance/reid/weights/osnet_x0_25_msmt17.pt")
        
        try:
            self.tracker = StrongSort(
                reid_weights=reid_weights,
                device='cpu',  # 使用CPU进行调试
                half=False,
                per_class=False,
                min_conf=0.1,
                max_cos_dist=0.2,
                max_iou_dist=0.7,
                max_age=30,
                n_init=3,
                nn_budget=100,
                mc_lambda=0.98,
                ema_alpha=0.9,
            )
            print("✓ 追踪器初始化成功")
        except Exception as e:
            print(f"✗ 追踪器初始化失败: {e}")
            print("提示: 请确保reid权重文件存在，或修改权重路径")
            return False
            
        return True
    
    def create_test_image(self, width=640, height=480):
        """
        创建测试图像
        
        Args:
            width (int): 图像宽度
            height (int): 图像高度
            
        Returns:
            np.ndarray: 测试图像
        """
        # 创建简单的测试图像（灰度渐变）
        self.test_image = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(height):
            self.test_image[i, :] = [i * 255 // height] * 3
        
        print(f"✓ 创建测试图像: {width}x{height}")
        return self.test_image
    
    def create_test_detections(self, scenario="single"):
        """
        创建测试检测数据
        
        Args:
            scenario (str): 测试场景类型
                - "single": 单个检测
                - "multiple": 多个检测
                - "mixed": 混合场景（部分有效ID）
                - "no_valid_id": 无有效ID
                
        Returns:
            np.ndarray: 检测数据，格式为 [x1, y1, x2, y2, conf, cls, target_id]
        """
        print(f"\n=== 创建测试检测数据: {scenario} ===")
        
        if scenario == "single":
            # 单个检测，有效目标ID
            dets = np.array([
                [100, 100, 200, 200, 0.9, 0, 1001]  # x1,y1,x2,y2,conf,cls,target_id
            ])
            print("场景: 单个检测，目标ID=1001")
            
        elif scenario == "multiple":
            # 多个检测，每个都有不同的有效目标ID
            dets = np.array([
                [100, 100, 200, 200, 0.9, 0, 1001],  # 目标1
                [300, 150, 400, 250, 0.8, 0, 1002],  # 目标2
                [150, 300, 250, 400, 0.85, 1, 1003], # 目标3（不同类别）
            ])
            print("场景: 多个检测，目标ID分别为1001, 1002, 1003")
            
        elif scenario == "mixed":
            # 混合场景：部分检测有有效ID，部分无效
            dets = np.array([
                [100, 100, 200, 200, 0.9, 0, 1001],  # 有效ID
                [300, 150, 400, 250, 0.8, 0, 0],     # 无效ID (0)
                [150, 300, 250, 400, 0.85, 1, 1003], # 有效ID
                [450, 200, 550, 300, 0.7, 0, -1],    # 无效ID (负数)
            ])
            print("场景: 混合检测，有效ID: 1001, 1003；无效ID: 0, -1")
            
        elif scenario == "no_valid_id":
            # 无有效ID场景
            dets = np.array([
                [100, 100, 200, 200, 0.9, 0, 0],   # 无效ID
                [300, 150, 400, 250, 0.8, 0, -1],  # 无效ID
            ])
            print("场景: 无有效目标ID")
            
        else:
            raise ValueError(f"未知的测试场景: {scenario}")
        
        print(f"检测数据形状: {dets.shape}")
        print(f"检测详情:\n{dets}")
        
        return dets
    
    def run_tracking_test(self, dets, test_name):
        """
        运行追踪测试
        
        Args:
            dets (np.ndarray): 检测数据
            test_name (str): 测试名称
            
        Returns:
            np.ndarray: 追踪结果
        """
        print(f"\n=== 运行追踪测试: {test_name} ===")
        
        if self.tracker is None or self.test_image is None:
            print("✗ 追踪器或测试图像未初始化")
            return None
        
        try:
            # 运行追踪更新
            print("调用tracker.update()...")
            results = self.tracker.update(dets, self.test_image)
            
            print(f"\n追踪结果:")
            if len(results) > 0:
                print(f"结果形状: {results.shape}")
                print(f"结果详情:\n{results}")
                
                # 解析结果
                for i, result in enumerate(results):
                    x1, y1, x2, y2, track_id, conf, cls, det_ind = result
                    print(f"轨迹 {i+1}: ID={int(track_id)}, 位置=({x1:.1f},{y1:.1f},{x2:.1f},{y2:.1f}), "
                          f"置信度={conf:.3f}, 类别={int(cls)}, 检测索引={int(det_ind)}")
            else:
                print("无追踪结果")
                
            return results
            
        except Exception as e:
            print(f"✗ 追踪测试失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_id_mapping_methods(self):
        """
        测试ID映射相关的私有方法
        
        Note:
            直接测试StrongSort类中的ID映射方法
        """
        print("\n=== 测试ID映射方法 ===")
        
        if self.tracker is None:
            print("✗ 追踪器未初始化")
            return
        
        # 测试数据
        target_ids = np.array([1001, 0, 1003, -1])  # 混合有效和无效ID
        
        # 测试 _has_valid_target_ids
        print("\n1. 测试 _has_valid_target_ids:")
        result = self.tracker._has_valid_target_ids(target_ids)
        print(f"输入: {target_ids}")
        print(f"结果: {result} (期望: True，因为包含有效ID)")
        
        # 测试空数组
        empty_ids = np.array([])
        result_empty = self.tracker._has_valid_target_ids(empty_ids)
        print(f"空数组测试: {result_empty} (期望: False)")
        
        # 测试全无效ID
        invalid_ids = np.array([0, -1, 0])
        result_invalid = self.tracker._has_valid_target_ids(invalid_ids)
        print(f"全无效ID测试: {result_invalid} (期望: False)")
    
    def run_comprehensive_test(self):
        """
        运行综合测试
        
        包含多个测试场景，全面验证ID映射功能
        """
        print("\n" + "="*60)
        print("开始StrongSort ID映射功能综合测试")
        print("="*60)
        
        # 1. 初始化
        if not self.setup_tracker():
            return
        
        self.create_test_image()
        
        # 2. 测试ID映射方法
        self.test_id_mapping_methods()
        
        # 3. 测试不同场景
        test_scenarios = [
            ("single", "单个检测场景"),
            ("multiple", "多个检测场景"),
            ("mixed", "混合ID场景"),
            ("no_valid_id", "无有效ID场景")
        ]
        
        for scenario, description in test_scenarios:
            try:
                dets = self.create_test_detections(scenario)
                results = self.run_tracking_test(dets, description)
                
                # 分析结果
                self.analyze_results(dets, results, scenario)
                
            except Exception as e:
                print(f"✗ 场景 {scenario} 测试失败: {e}")
        
        print("\n" + "="*60)
        print("测试完成")
        print("="*60)
    
    def analyze_results(self, dets, results, scenario):
        """
        分析测试结果
        
        Args:
            dets (np.ndarray): 输入检测数据
            results (np.ndarray): 追踪结果
            scenario (str): 测试场景
        """
        print(f"\n--- 结果分析: {scenario} ---")
        
        if results is None or len(results) == 0:
            print("⚠️  无追踪结果")
            return
        
        # 提取输入的目标ID
        input_target_ids = dets[:, 6]
        valid_input_ids = input_target_ids[input_target_ids > 0]
        
        # 提取输出的轨迹ID
        output_track_ids = results[:, 4].astype(int)
        
        print(f"输入有效目标ID: {valid_input_ids}")
        print(f"输出轨迹ID: {output_track_ids}")
        
        # 检查ID映射是否正确
        if len(valid_input_ids) > 0:
            mapped_correctly = any(tid in valid_input_ids for tid in output_track_ids)
            if mapped_correctly:
                print("✓ ID映射成功：输出轨迹ID包含输入的有效目标ID")
            else:
                print("⚠️  ID映射可能有问题：输出轨迹ID与输入目标ID不匹配")
        else:
            print("ℹ️  无有效输入目标ID，使用默认轨迹ID")


def main():
    """
    主函数：运行ID映射调试测试
    """
    print("StrongSort ID映射功能调试工具")
    print("作者: AI Assistant")
    print("用途: 测试和调试目标ID映射功能\n")
    
    # 创建调试器并运行测试
    debugger = IDMappingDebugger()
    debugger.run_comprehensive_test()
    
    print("\n调试建议:")
    print("1. 检查追踪器初始化是否成功")
    print("2. 观察不同场景下的ID映射结果")
    print("3. 验证有效目标ID是否正确映射到轨迹")
    print("4. 确认无效ID场景下的处理逻辑")
    print("5. 如有问题，检查StrongSort类中的ID映射方法")


if __name__ == "__main__":
    main()