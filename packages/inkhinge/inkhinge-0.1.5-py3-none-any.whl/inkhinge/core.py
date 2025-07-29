"""inkhinge包的核心功能模块"""
import os
import numpy as np
import pandas as pd
from spectrochempy_omnic import OMNICReader as read
from decimal import Decimal, Context, ROUND_HALF_UP

"read_to_csv模块："
def read_to_csv(input_path, output_path=None, background_path=None, overwrite=False, recursive=False, precision=20, merge_output=None):
    """
    读取Omnic SPA文件并转换为CSV格式，可选择性合并所有转换后的CSV文件

    参数:
        input_path (str): 输入SPA文件路径或包含这些文件的目录路径
        output_path (str): 输出CSV文件路径或目录路径
        background_path (str): 背景BG.spa文件路径
        overwrite (bool): 是否覆盖已存在的文件
        recursive (bool): 是否递归处理子目录(仅在处理目录时有效)
        precision (int): 输出数据的小数位数精度
        merge_output (str): 合并所有CSV文件的输出路径，默认为None表示不合并

    返回:
        处理结果信息(成功转换的文件数量或单个文件的输出路径)
    """
    def float_to_fixed_str(value, precision=20):
        """将浮点数转换为指定精度的定点小数表示字符串"""
        if np.isnan(value):
            return 'nan'
        try:
            ctx = Context(prec=max(25, precision + 5), rounding=ROUND_HALF_UP)
            dec = ctx.create_decimal(str(value))
            return f"{dec:.{precision}f}"
        except:
            return str(value)

    def detect_data_type(reader):
        """检测数据类型并返回相应的标题和单位"""
        data_type_mapping = {
            0: ("Absorbance", "AU"),
            1: ("Transmittance", "%"),
            2: ("Reflectance", "%"),
            3: ("Single Beam", ""),
            4: ("Kubelka-Munk", "KM units"),
        }

        if hasattr(reader, 'data_type') and reader.data_type in data_type_mapping:
            return data_type_mapping[reader.data_type]

        if hasattr(reader, 'title'):
            title = reader.title.lower()
            if "absorbance" in title:
                return "Absorbance", "AU"
            elif "transmittance" in title or "透过率" in title:
                return "Transmittance", "%"
            elif "reflectance" in title:
                return "Reflectance", "%"
            elif "single beam" in title or "单光束" in title:
                return "Single Beam", ""
            elif "kubelka-munk" in title or "km" in title:
                return "Kubelka-Munk", "KM units"

        y_title = reader.y_title or "Intensity"
        y_units = reader.y_units or ""

        if "kubelka" in y_title.lower() or "km" in y_title.lower():
            return "Kubelka-Munk", "KM units"

        return y_title, y_units

    def calculate_kubelka_munk(reflectance):
        """计算Kubelka-Munk值"""
        reflectance = np.clip(reflectance, 0.0001, 0.9999)
        return ((1 - reflectance) **2) / (2 * reflectance)

    def extract_spectral_data(reader):
        """从读取器中提取光谱数据和对应的X轴数据"""
        data = reader.data
        x = reader.x

        x_units = reader.x_units or "cm^-1"
        x_title = reader.x_title or "Wavelength"

        if data.ndim == 1:
            spectral_data = data.reshape(1, -1)
        elif data.ndim >= 2:
            spectral_dim = None

            if data.shape[-1] == len(x):
                spectral_dim = -1
            elif data.shape[0] == len(x):
                spectral_dim = 0

            if spectral_dim is None:
                for i in range(data.ndim):
                    if data.shape[i] == len(x):
                        spectral_dim = i
                        break

            if spectral_dim is None:
                spectral_dim = np.argmin(np.abs(np.array(data.shape) - len(x)))
                print(f"警告: 无法确定光谱数据维度，假设为维度 {spectral_dim}")

            if spectral_dim != -1:
                axes = list(range(data.ndim))
                axes.remove(spectral_dim)
                axes.append(spectral_dim)
                data = data.transpose(axes)

            spectral_data = data.reshape(-1, len(x))
        else:
            raise ValueError(f"不支持的数据维度: {data.ndim}")

        return spectral_data, x, x_title, x_units

    def apply_background_correction(sample_data, background_data, x_sample, x_bg):
        """应用背景校正"""
        if np.array_equal(x_sample, x_bg):
            corrected_data = sample_data / background_data
        else:
            corrected_data = np.zeros_like(sample_data)
            for i, spectrum in enumerate(sample_data):
                bg_interp = np.interp(x_sample, x_bg, background_data[0])
                corrected_data[i] = spectrum / bg_interp

        return corrected_data

    def convert_spa_to_csv(input_file, output_file=None, background_path=None, overwrite=False, precision=20):
        """将Omnic SPA文件转换为CSV格式"""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        if not output_file:
            base_name, _ = os.path.splitext(input_file)
            output_file = f"{base_name}_converted.csv"

        if os.path.exists(output_file) and not overwrite:
            raise FileExistsError(f"输出文件已存在: {output_file}")

        try:
            print(f"正在读取样本文件: {input_file}")
            sample_reader = read(input_file)

            sample_data, x_sample, x_title, x_units = extract_spectral_data(sample_reader)
            y_title, y_units = detect_data_type(sample_reader)

            if background_path:
                if not os.path.exists(background_path):
                    raise FileNotFoundError(f"背景文件不存在: {background_path}")

                print(f"正在读取背景文件: {background_path}")
                bg_reader = read(background_path)
                bg_data, x_bg, _, _ = extract_spectral_data(bg_reader)

                if y_title == "Reflectance":
                    corrected_data = apply_background_correction(sample_data, bg_data, x_sample, x_bg)
                    y_title = "Corrected Reflectance"
                elif y_title == "Transmittance":
                    corrected_data = sample_data - bg_data
                    y_title = "Corrected Transmittance"
                else:
                    corrected_data = apply_background_correction(sample_data, bg_data, x_sample, x_bg)
                    y_title = f"Corrected {y_title}"

                spectral_data = corrected_data
            else:
                spectral_data = sample_data

            print(f"数据维度: {spectral_data.shape}")
            print(f"X轴: {x_title} ({x_units})")
            print(f"数据类型: {y_title} ({y_units})")

            # 创建DataFrame列数据（解决碎片化问题）
            columns_data = {
                f"{x_title} ({x_units})": [float_to_fixed_str(val, precision) for val in x_sample]
            }

            if y_title == "Reflectance" or y_title == "Corrected Reflectance":
                km_data = calculate_kubelka_munk(spectral_data)
                km_title = "Kubelka-Munk"
                km_units = "KM units"

                if km_data.shape[0] == 1:
                    columns_data[f"{km_title} ({km_units})"] = [float_to_fixed_str(val, precision) for val in km_data[0]]
                else:
                    for i in range(km_data.shape[0]):
                        columns_data[f"{km_title}_{i} ({km_units})"] = [float_to_fixed_str(val, precision) for val in km_data[i]]

            if spectral_data.shape[0] == 1:
                columns_data[f"{y_title} ({y_units})"] = [float_to_fixed_str(val, precision) for val in spectral_data[0]]
            else:
                if hasattr(sample_reader, 'spectra_titles') and len(sample_reader.spectra_titles) == spectral_data.shape[0]:
                    for i, title in enumerate(sample_reader.spectra_titles):
                        clean_title = title.strip() or f"{y_title}_{i}"
                        columns_data[f"{clean_title} ({y_units})"] = [float_to_fixed_str(val, precision) for val in spectral_data[i]]
                else:
                    for i in range(spectral_data.shape[0]):
                        columns_data[f"{y_title}_{i} ({y_units})"] = [float_to_fixed_str(val, precision) for val in spectral_data[i]]

            df = pd.DataFrame(columns_data)
            df.to_csv(output_file, index=False, na_rep='nan')
            print(f"成功转换并保存至: {output_file}")
            return output_file

        except Exception as e:
            print(f"转换失败: {str(e)}")
            return None

    def batch_convert_spa_to_csv(input_dir, output_dir=None, background_path=None, overwrite=False, recursive=False,
                                 precision=20, merge_output=None):
        """批量转换目录中的SPA文件为CSV格式，并可选择性合并所有CSV文件"""
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        spa_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.spa'):
                    spa_files.append(os.path.join(root, file))

            if not recursive:
                break

        if not spa_files:
            print(f"在目录 {input_dir} 中未找到SPA文件")
            return []

        # 按文件名排序
        spa_files.sort()
        output_files = []
        for spa_file in spa_files:
            try:
                if output_dir:
                    rel_path = os.path.relpath(spa_file, input_dir)
                    base_name, _ = os.path.splitext(rel_path)
                    output_file = os.path.join(output_dir, f"{base_name}.csv")
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                else:
                    output_file = None

                result = convert_spa_to_csv(spa_file, output_file, background_path, overwrite, precision)
                if result:
                    output_files.append(result)
            except Exception as e:
                print(f"处理文件 {spa_file} 时出错: {str(e)}")

        print(f"批量转换完成: 成功 {len(output_files)}/{len(spa_files)}")

        # 合并CSV文件
        if merge_output and output_files:
            merge_csv_files(output_files, merge_output, overwrite, precision)

        return output_files

    def merge_csv_files(csv_files, output_path, overwrite=False, precision=20):
        """
        按顺序合并多个CSV文件，解决性能警告并使列名从0开始计数

        参数:
            csv_files (list): CSV文件路径列表(按顺序排列)
            output_path (str): 合并后的输出文件路径
            overwrite (bool): 是否覆盖已存在的文件
            precision (int): 输出数据的小数位数精度
        """
        if not csv_files:
            print("没有CSV文件可合并")
            return

        # 检查输出文件是否存在
        if os.path.exists(output_path) and not overwrite:
            raise FileExistsError(f"合并输出文件已存在: {output_path}")

        print(f"开始合并 {len(csv_files)} 个CSV文件...")

        # 读取所有数据框并准备合并
        data_frames = []
        x_column = None

        for i, csv_file in enumerate(csv_files):
            df = pd.read_csv(csv_file)

            # 验证X轴列
            current_x_col = df.columns[0]
            if i == 0:
                x_column = current_x_col
                # 保留第一个文件的X轴列，并重命名数据列添加后缀_0
                rename_map = {col: f"{col}_0" for col in df.columns[1:]}
                renamed_df = df.rename(columns=rename_map)
                data_frames.append(renamed_df)
            else:
                if current_x_col != x_column:
                    print(f"警告: 文件 {csv_file} 的X轴列名与第一个文件不一致: {current_x_col} vs {x_column}")
                    continue

                # 重命名后续文件的数据列，从1开始计数
                file_suffix = f"_{i}"
                rename_map = {col: f"{col}{file_suffix}" for col in df.columns[1:]}
                renamed_df = df.rename(columns=rename_map)
                # 移除后续文件的X轴列
                data_frames.append(renamed_df.drop(columns=[current_x_col]))

            print(f"已准备文件 {i+1}/{len(csv_files)}: {csv_file}")

        # 一次性合并所有数据框（解决性能警告）
        merged_df = pd.concat(data_frames, axis=1)

        # 使用自定义格式化函数保存CSV，确保定点小数精度
        float_format = lambda x: float_to_fixed_str(x, precision)
        merged_df.to_csv(output_path, index=False, na_rep='nan', float_format=float_format)

        print(f"成功合并并保存至: {output_path}")
        return output_path

    # 判断输入是文件还是目录
    if os.path.isfile(input_path):
        # 确保输入是.spa文件
        if not input_path.lower().endswith('.spa'):
            raise ValueError(f"输入文件不是SPA文件: {input_path}")
        # 处理单个文件
        result = convert_spa_to_csv(input_path, output_path, background_path, overwrite, precision)
        if merge_output:
            return [result] if result else []
        return result
    elif os.path.isdir(input_path):
        # 处理目录
        return batch_convert_spa_to_csv(input_path, output_path, background_path, overwrite, recursive, precision, merge_output)
    else:
        raise ValueError(f"输入路径不存在: {input_path}")