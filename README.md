# 交错战线 Assets 工具

这是一个用于处理交错战线游戏资源文件的工具，提供了资源文件的加密、解密功能，以及图像透明度处理功能。

## 功能特性

- **资源文件加密/解密**：支持游戏资源文件的加密和解密操作
- **图像透明度处理**：支持图像的直通透明和预乘透明之间的转换
- **主题切换**：支持多种界面主题，可以根据个人喜好进行切换

## 开发者指南

### 项目结构

```
交错战线 Assets 工具/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── README.md               # 项目说明文档
├── CHANGELOG.md            # 更新日志
├── LICENSE                 # 许可证文件
├── cache/                  # 缓存目录
├── src/                    # 源代码目录
│   ├── __init__.py         # 包初始化文件
│   ├── config/             # 配置管理模块
│   │   ├── __init__.py
│   │   └── config_manager.py
│   ├── core/               # 核心功能模块
│   │   ├── __init__.py
│   │   ├── crypto.py       # 加密解密核心功能
│   │   └── image_processor.py # 图像处理核心功能
│   ├── ui/                 # 用户界面模块
│   │   ├── __init__.py
│   │   ├── crypto_tab.py   # 加密解密标签页
│   │   ├── image_tab.py    # 图像处理标签页
│   │   └── settings_tab.py # 设置标签页
│   └── utils/              # 工具函数模块
│       └── __init__.py
└── .github/                # GitHub配置
    └── workflows/          # GitHub Actions工作流
        └── release.yml     # 自动发布配置
```

### 版本发布流程

本项目使用GitHub Actions自动构建和发布应用程序。发布流程如下：

1. 在CHANGELOG.md的"未发布"部分添加新版本的更改内容
2. 运行版本更新脚本：`python create_release.py <版本号> [发布说明]`
   例如：`python create_release.py 1.0.0 "第一个正式版本"`
3. 脚本会自动更新版本号、更新日志，并创建Git标签
4. 当标签推送到GitHub后，GitHub Actions会自动构建应用程序并创建发布

### 手动构建

如果需要手动构建应用程序，可以使用以下命令：

```bash
# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 使用PyInstaller打包应用程序
pyinstaller --noconfirm --name "交错战线Assets工具" --windowed --add-data "README.md;." --add-data "LICENSE;." main.py

# 创建必要的目录
mkdir -p dist/交错战线Assets工具/cache
mkdir -p dist/交错战线Assets工具/output_预乘透明
mkdir -p dist/交错战线Assets工具/output_直通透明

# 复制README和LICENSE文件到dist目录
copy README.md dist\交错战线Assets工具\
copy LICENSE dist\交错战线Assets工具\
```

## 安装与使用

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

## 使用说明

### 资源文件加密/解密

1. 在"加密/解密"标签页中，选择需要处理的资源文件目录
2. 点击"解密"按钮进行解密操作，解密后会生成一个索引缓存文件
3. 点击"加密"按钮进行加密操作，需要选择之前生成的索引缓存文件

### 图像透明度处理

1. 在"图片处理"标签页中，选择需要处理的图像文件
2. 根据需要点击"直通透明转预乘透明"或"预乘透明转直通透明"按钮
3. 处理后的图像会保存在相应的输出目录中

### 设置

在"设置"标签页中，可以：
- 切换应用程序主题
- 清除缓存文件

## 版本历史

- V0.7.0: 重构项目结构，优化代码可维护性
- V0.6.0: 添加图像透明度处理功能
- V0.5.0: 添加资源文件加密解密功能

## 许可证

本项目基于 MIT 许可证发布，详情请参阅 LICENSE 文件。