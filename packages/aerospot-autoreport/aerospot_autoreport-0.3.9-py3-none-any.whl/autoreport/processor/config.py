"""
配置生成器模块 - 用于生成报告配置文件

此模块负责根据输入数据生成完整的报告配置，包括：
- 公司信息
- 报告结构
- 数据分析章节
- 污染源标记章节
"""

import os
import json
import logging
import pandas as pd
from .data.utils import get_indicator_unit

logger = logging.getLogger(__name__)
 

def create_updated_config(updated_data, report_structure_file=None):
    """创建更新后的配置文件
    
    Args:
        source_config: 原始配置（字典或配置文件路径）
        updated_data: 更新的数据
        merged_data: 合并后的数据（可选）
        data_root: 数据根目录（可选）
    
    Returns:
        str: 更新后的配置文件路径
    """
    logging.info("创建更新后的配置文件")
    
    
    company_info = updated_data.get('company_info', {})
    image_resources = updated_data.get('image_resources', {})
    DEFAULT_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "images")

    # 构建报告结构
    report_structure = {
        "title": "智能小型机载光谱指数基站AeroSpot分析报告",
        "chapters": []
    }
    
    # 添加第一章和第二章（固定结构）
    report_structure["chapters"].extend([
        {   
            "chapter_num": 1,
            "title": "智能小型机载光谱指数分析机载AeroSpot简介",
            "sections": [
                {
                    "name": "系统介绍",
                    "items": [
                        {
                            "type": "text",
                            "content": [
                                f"{company_info.get('name', '')}积极响应国家政策，根据不同领域的市场需求，推出了智能小型机载光谱指数分析基站AeroSpot,其灵活性、低成本、便于部署等特点，在许多应用场景中展现出显著优势。",
                                "目前多数行业无人机应用采用手动或半自动作业模式，作业过程需要人员介入，人力要求较高，操作门槛也较高，基于上述应用痛点，AeroSpot在生态环境监测中极具优势，综合利用无人机与光谱科技，通过无人机机场，可轻松实现非现场无人化生态监测，解决实际场景应用难题，提高生态管理效率，为打造\"低空+治理\"增添助力。",
                                f"{company_info.get('name', '')}智能小型机载光谱指数分析基站AeroSpot通过获取高精度的点光谱数据，采用\"以点带面\"的方式，能够实现对全湖或重点区域的全局可视化监测。这种技术不仅弥补了卫星遥感因天气条件、时空分辨率限制而无法按需获取整湖或重点区域水质可视化数据的缺陷，还可以解决无人机高光谱成像技术在大面积水域拼接中的技术难题。"
                            ]
                        }
                    ]
                },
                {
                    "name": "设备展示",
                    "items": [
                        {
                            "type": "text",
                            "content": "机载光谱指数分析仪 AeroSpot实体图如下所示。"
                        },
                        {
                            "type": "image",
                            "path": os.path.join(DEFAULT_IMAGES_DIR, "uav.png"),
                            "caption": "机载光谱指数分析仪 AeroSpot实体图"
                        },
                        {
                            "type": "image",
                            "path": os.path.join(DEFAULT_IMAGES_DIR, "airport.png"),
                            "caption": "智能小型机载光谱指数分析基站AeroSpot实体图"
                        }
                    ]
                },
                {
                    "name": "技术参数",
                    "items": [
                        {
                            "type": "text",
                            "content": "智能小型机载光谱指数分析基站 AeroSpot 参数如下表所示。"
                        },
                        {
                            "type": "table",
                            "name": "智能小型机载光谱指数分析基站 AeroSpot 参数",
                            "data": [
                                ["大疆机场2参数", ""],
                                ["尺寸（长×宽×高）", "舱盖开启：长 1228 mm，宽 583 mm，高 412 mm\n舱盖闭合：长 570 mm，宽 583 mm，高 465 mm"],
                                ["整机重量", "34kg（不包含飞行器）"],
                                ["输入电压", "100V 至 240V（交流电）, 50/60 Hz"],
                                ["工作环境温度", "−25℃ 至 45℃"],
                                ["无人机参数大疆M3D", ""],
                                ["裸机重量", "1410 克"],
                                ["最大起飞重量", "不大于 1500 克"],
                                ["尺寸", "长 335 mm，宽 398 mm，高 153 mm（不含桨叶）"],
                                ["广角相机", "具备测绘相机，相机CMOS不低于4/3英寸"],
                                ["长焦相机", "1200 万"],
                                ["小型机载单点光谱指数分析仪 AeroSpot", ""],
                                ["光谱范围", "400 nm - 850 nm"],
                                ["光谱分辨率", "1 nm"],
                                ["视场角", "2.3°"],
                                ["探测器类型", "CMOS线阵探测器"],
                                ["重量", "180g"],
                                ["适配无人机", "大疆 M3D、M4D 等"],
                                ["可实时反演指数", "水环境方向：叶绿素a、浊度、悬浮物、化学需氧量、总磷、氨氮、色度、蓝绿藻等级等\n农林方向：NDVI、EVI、SIPI、PSRI、mLICI、物候指数、叶锈病程度指数、叶面积指数等多种植被指数和农学参数"]
                            ],
                            "merge_cells": [
                                {"row": 0, "col": 0, "row_span": 1, "col_span": 2, "bold": True},
                                {"row": 5, "col": 0, "row_span": 1, "col_span": 2, "bold": True},
                                {"row": 11, "col": 0, "row_span": 1, "col_span": 2, "bold": True}
                            ],
                            "column_widths": ["33%", "67%"]
                        }
                    ]
                }
            ]
        },
        {
            "chapter_num": 2,
            "title": "飞行区域介绍",
            "sections": [
                {
                    "name": "飞行区域资料介绍",
                    "items": [
                        {
                            "type": "text",
                            "content": "（用户手动添加）"
                        }
                    ]
                },
                {
                    "name": "智能小型机载光谱指数分析基站AeroSpot现场采集照片",
                    "items": [
                        {
                            "type": "image",
                            "path": "",
                            "caption": "智能小型机载光谱指数分析基站AeroSpot现场采集照片"
                        }
                    ]
                },
                {
                    "name": "水样采集现场照片",
                    "items": [
                        {
                            "type": "image",
                            "path": "",
                            "caption": "水样采集现场照片"
                        }
                    ]
                },
                {
                    "name": "智能小型机载光谱指数分析基站AeroSpot航点规划图",
                    "items": [
                        {
                            "type": "image",
                            "path": f"{image_resources['wayline_img']}",
                            "caption": "智能小型机载光谱指数分析基站AeroSpot航点规划图"
                        }
                    ]
                }
            ]
        }
    ])
    
    logging.info(f"已添加基础章节（第1-2章）")
    
    measure_data = updated_data.get('measure_data', pd.DataFrame())
    pred_data = updated_data.get('pred_data', updated_data.get('uav_data'))  # 无实测值情况下无反演值，则用无人机数据代替
    comparison_data = updated_data.get('comparison_data', {})
    maps = updated_data.get('maps', {})
    pollution_source = updated_data.get('pollution_source', {})
    

    # 添加第三章（如果存在测量数据）
    if isinstance(measure_data, pd.DataFrame) and not measure_data.empty:
        # 从测量数据中提取指标列表（除去经纬度列）
        indicators = [col for col in measure_data.columns if col not in ['index', 'latitude', 'longitude']]
        logging.info(f"从测量数据中提取的指标列表: {indicators}")
        
        # 创建第三章：数据分析
        data_analysis_chapter = {
            "chapter_num": 3,
            "title": "数据分析",
            "sections": [
                {
                    "name": "实测数据",
                    "items": [
                        {
                            "type": "text",
                            "content": "地面采样点的经纬度坐标及各项指标如下表所示"
                        },
                        {
                            "type": "table",
                            "name": "地面采样点的经纬度坐标及各项指标",
                            "headers": ["编号"] + [indicator if indicator in ['longitude', 'latitude'] else f"{indicator}\n({get_indicator_unit(indicator)})" for indicator in measure_data.columns.tolist()],
                            "data": [[str(i+1)] + row.tolist() for i, row in enumerate(measure_data.values)]
                        }
                    ]
                },
                {
                    "name": "实测值与反演值对比分析",
                    "items": [
                        {
                            "type": "text",
                            "content": "根据采样点的经纬度位置绘制在卫星影像的底图上，其空间分布图如下。"
                        },
                        {
                            "type": "image",
                            "path": maps.get('distribution_map', ''),
                            "caption": "采样点分布图"
                        },
                        {
                            "type": "text",
                            "content": "绝对误差=反演值-真实值（即反演值与真实值之差）；相对误差=（反演值-真实值）/真实值（即绝对误差所占真实值的百分比）。相对误差指的是反演所造成的绝对误差与真实值之比乘以100%所得的数值，以百分数表示。一般来说，相对误差更能反映反演结果的可信程度。根据《光谱法水质在线监测系统技术导则》和《光谱法水质在线快速监测系统》等行业标准和团体标准，光谱法用于水质检测，其相对误差小于30%则认为有效。"
                        }
                    ]
                }
            ]
        }
        
        # 获取数据分析章节的items列表
        analysis_items = data_analysis_chapter["sections"][1]["items"]
        
        # 为每个检测到的指标创建subsection
        for indicator in indicators:
            try:
                # 准备表格数据
                table_data = []
                
                # 如果有比较数据，优先使用比较数据
                if comparison_data and 'matches' in comparison_data:
                    for idx, match in enumerate(comparison_data['matches']):
                        if indicator in match['indicators']:
                            ind_data = match['indicators'][indicator]
                            # 添加行数据
                            table_data.append([
                                str(idx + 1),  # 编号
                                str(round(ind_data['measure_value'], 3)),  # 实测值
                                str(round(ind_data['pred_value'], 3)),  # 反演值
                                str(round(ind_data['pred_diff'], 3)),  # 绝对误差
                                str(round(ind_data['pred_rel_diff'], 3))  # 相对误差
                            ])
                
                subsection = {
                    "type": "subsection",
                    "name": indicator,
                    "items": [
                        {
                            "type": "table",
                            "name": f"{indicator}误差分析",
                            "headers": ["编号", f"实测值\n({get_indicator_unit(indicator)})", f"反演值({get_indicator_unit(indicator)})", f"绝对误差({get_indicator_unit(indicator)})", "相对误差(%)"],
                            "data": table_data
                        }
                    ]
                }
                analysis_items.append(subsection)
                logging.info(f"已添加 {indicator} 的误差分析表")
            except Exception as e:
                logging.error(f"生成{indicator}误差分析表时出错: {str(e)}")
                continue
            
        report_structure['chapters'].append(data_analysis_chapter)
        logging.info("已添加第3章：数据分析")
    else:
        logging.warning("未找到测量数据，跳过第3章生成")
    
    # 添加第4章：水质分布
    if pred_data is not None and not pred_data.empty:
        # 添加指标描述映射
        INDICATOR_DESCRIPTIONS = {
            "氨氮": "氨氮（NH3-N）指水中以游离氨（NH3）和铵离子（NH4+）形式存在的氮。氨氮是水体中的营养素，可导致水富营养化现象产生，是水体中的主要耗氧污染物，对鱼类及某些水生生物有毒害。",
            "总磷": "总磷（TP）是水体中各种形态磷的总量。总磷是水体富营养化的主要限制性营养元素，其浓度的高低直接影响水体的富营养化程度。",
            "总氮": "总氮（TN）是水体中各种形态氮的总量。总氮是水体富营养化的重要营养元素，其含量可反映水体的富营养化程度。",
            "COD": "化学需氧量（COD）是在一定条件下，水中能被强氧化剂氧化的物质所消耗的氧化剂量。COD是衡量水体受机体污染程度的重要指标。",
            "叶绿素a": "叶绿素a是浮游植物生物量的重要指标，其含量可反映水体的初级生产力和富营养化程度。",
            "透明度": "透明度是指光线能透过水体的深度，是表征水体清澈程度的重要指标。透明度的高低直接影响水生态系统的光合作用。",
            "浊度": "浊度是指水体中悬浮物质对光的遮蔽程度。浊度越高，表明水中悬浮物质含量越多，水质越差。",
            "溶解氧": "溶解氧（DO）是指溶解在水中的氧气含量。溶解氧是维持水生生物生存的必要条件，也是衡量水体自净能力的重要指标。"
        }

        water_quality_chapter = {
            "chapter_num": 4,
            "title": "水质参数反演结果",
            "content": "根据云端内置的水质AI大模型对选定的水体参数进行反演，并依据《地表水环境质量标准》（GB 3838-2002）对水质进行划分。",
            "sections": []
        }
        # 为每个指标创建section
        indicators = [col for col in pred_data.columns if col not in ['index', 'latitude', 'longitude']]
        for indicator in indicators:
            # 获取该指标的所有反演值
            values = []
            min_val = 0
            max_val = 0
            
            if isinstance(pred_data, pd.DataFrame) and indicator in pred_data.columns:
                # 安全地获取数值并过滤无效值
                values = pred_data[indicator].dropna().tolist()
                if values:  # 确保有有效值
                    valid_values = [float(v) for v in values if str(v).strip() and str(v).lower() != 'nan']
                    if valid_values:
                        min_val = min(valid_values)
                        max_val = max(valid_values)
            
            # 获取指标对应的图片路径
            indicator_maps_dict = maps.get(indicator, {})

            section = {
                "name": indicator,
                "items": [
                    {
                        "type": "text",
                        "content": INDICATOR_DESCRIPTIONS.get(indicator, f"{indicator}是水质监测的重要指标之一，其含量变化反映了水体的污染状况。")
                    },
                    {
                        "type": "image",
                        "path": indicator_maps_dict.get('distribution', ''),
                        "caption": f"AeroSpot航点水质指标{indicator}分布图"
                    },
                    {
                        "type": "image",
                        "path": indicator_maps_dict.get('interpolation', ''),
                        "caption": f"AeroSpot以点带面反演{indicator}水质指标"
                    },
                    {
                        "type": "image",
                        "path": indicator_maps_dict.get('level', 'skip'),
                        "caption": f"AeroSpot分析{indicator}水质等级分布"
                    },
                    {
                        "type": "text",
                        "content": f"从反演结果可知，区域内{indicator}的数值分布范围为 {min_val:.2f} ~ {max_val:.2f} mg/L， 空间分布差异显著。"
                    }
                ]
            }
            water_quality_chapter["sections"].append(section)
            logging.info(f"已添加 {indicator} 的水质分析")
        
        report_structure["chapters"].append(water_quality_chapter)
        logging.info(f"已添加第4章：水质参数反演结果，包含 {len(water_quality_chapter['sections'])} 个指标分析")

    else:
        logging.warning("未找到合并数据，跳过第4章生成")
    
    # 添加第5章：疑似污染源标记
    if pollution_source:
        pollution_source_chapter = {
            "chapter_num": 5,
            "title": "疑似污染源标记",
            "content": [
                "在高光谱水质监测中，根据机载高光谱相机采集数据和相应水质指标反演结果，标识出一些疑似污染源点位。这些点位可能是与水质异常相关的区域，提示可能存在的污染物质，并识别可能的污染来源。这些点位可能受到多种因素影响，包括但不限于：",
                "- 工业排放：附近工业活动可能导致废水排放，其中可能含有化学物质或颗粒物，对水体产生负面影响。",
                "- 农业活动：农业用地周边可能存在农药、化肥等农业排放物的输入，对水质产生一定的压力。",
                "- 城市污水排放：城市污水系统的排放口可能导致有机物、氮、磷等物质输入水体，影响水体的营养状态。",
                "- 土壤侵蚀：陡峭坡地、裸露土地等可能引发土壤侵蚀，将泥沙等颗粒物质输送到水体中。",
                "高光谱技术能够在数据中识别出异常的光谱反演特征，这些特征往往与化学需氧量、总氮、总磷、氨氮、高锰酸盐指数等水质指标相关。因此，疑似污染源点位的标定有助于进一步的现场调查和采样分析，以验证是否存在污染物质，并识别可能的污染来源。",
                "为了维护水体生态平衡和保护水资源，下一步的工作将包括深入的现场研究，针对这些疑似污染源点位进行详细的水质监测和污染因素溯源，为环保决策提供科学依据。"
            ],
            "sections": []
        }
        
        # 为每个检测到的污染源指标创建section
        for indicator, source_points in pollution_source.items():
            if source_points:  # 只有当有污染源点位时才添加该指标的section
                section = {
                    "name": indicator,
                    "items": [
                        {
                            "type": "text",
                            "content": f"该指标共检测出{len(source_points)}处疑似污染源，其点位坐标及高清图像如下。"
                        },
                        {
                            "type": "table",
                            "name": f"{indicator}疑似污染源信息",
                            "headers": ["序号", "经度", "纬度"],
                            "data": source_points
                        }
                    ]
                }
                pollution_source_chapter["sections"].append(section)
        
        # 只有当有sections时才添加这一章
        if pollution_source_chapter["sections"]:
            report_structure["chapters"].append(pollution_source_chapter)
        logging.info(f"已添加第5章：疑似污染源标记")
    else:
        logging.warning("缺少污染源数据，跳过第5章生成")
    
    # 保存报告结构到JSON文件
    try:
        with open(report_structure_file, 'w', encoding='utf-8') as f:
            json.dump(report_structure, f, ensure_ascii=False, indent=2)
        logging.info(f"报告结构已保存到: {report_structure_file}")
    except Exception as e:
        logging.error(f"保存报告结构时出错: {str(e)}")

    # 保存更新后的数据到同路径下
    try:
        updated_data_file = os.path.join(os.path.dirname(report_structure_file), "updated_data.json")

        def convert_df_to_length(obj):
            if isinstance(obj, pd.DataFrame):
                return len(obj)
            elif isinstance(obj, dict):
                return {k: convert_df_to_length(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_df_to_length(i) for i in obj]
            else:
                return obj

        serializable_data = convert_df_to_length(updated_data)
        with open(updated_data_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)

        logging.info(f"更新后的数据已保存到: {updated_data_file}")
    except Exception as e:
        logging.error(f"保存更新后的数据时出错: {str(e)}")
    
    return report_structure_file