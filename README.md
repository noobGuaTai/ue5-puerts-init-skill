# UE5-PuerTS-Init-Skill

用于在 UE5 中快速集成 PuerTS 的Skill。

## 使用前说明

在使用本 skill 前，请确保你的项目满足以下条件：

### 1. 项目类型要求
- **蓝图项目已引入 C++ 支持**
  - 如果是纯蓝图项目，需要在 UE 编辑器中添加 C++ 代码支持

### 2. 环境要求
- **Python**
- **Git**
- **Node.js**
- **Unreal Engine 5.0+**
- **建议开启代理以加速下载**

### 在初始化完成后，需编译项目且在UE编辑器中点击PuerTS的小蓝标，生成*.d.ts说明文件后，运行游戏在控制台看到以下信息表示项目加载PuerTS成功:
```
Puerts: (0x000001D21AEE75F0) ========================================
Puerts: (0x000001D21AEE75F0) Puerts TypeScript Loaded Successfully!
Puerts: (0x000001D21AEE75F0) GameInstance:,[object Object]
Puerts: (0x000001D21AEE75F0) ========================================
```

## 快速开始

1. **向智能体提问**
   ```
   使用 your_dowloaded_path/ue5-puerts-init/SKILL.md 初始化PuerTS
   ```

2. **智能体将自动执行**
   - 安装 Puerts 插件和 V8 引擎
   - 配置 C++ 模块依赖
   - 创建并配置 GameInstance
   - 设置 TypeScript 环境


## 文件说明

### SKILL.md
主要的 skill 定义文件，包含完整的初始化指南。

### assets/
包含所有需要的模板文件：

| 文件 | 说明 | 复制位置 |
|------|------|----------|
| `MyGameInstance.h` | GameInstance 头文件模板 | `Source/[Project]/Public/` |
| `MyGameInstance.cpp` | GameInstance 实现模板 | `Source/[Project]/Private/` |
| `tsconfig.json` | TypeScript 编译配置 | `Typescript/` |
| `package.json` | NPM 包配置 | `Typescript/` |
| `global.d.ts` | 全局类型声明 | `Typescript/` |
| `Main.ts` | JavaScript 入口示例 | `Typescript/` |
| `gitignore` | Git 忽略规则 | 项目根目录 `.gitignore` |
| `typings/puerts/` | Puerts 核心类型定义 | `Typing/puerts/` |
| `typings/ue/` | 最小化 UE 类型定义 | `Typing/ue/` |

### scripts/
包含自动化辅助脚本：

| 脚本 | 说明 |
|------|------|
| `install_puerts.py` | 自动下载和安装 Puerts 插件及 V8 引擎 |
| `replace_api_macro.py` | 自动替换 API 宏占位符并配置 GameInstance 类 |


## PuerTS项目地址

- [Puerts GitHub](https://github.com/Tencent/puerts)
