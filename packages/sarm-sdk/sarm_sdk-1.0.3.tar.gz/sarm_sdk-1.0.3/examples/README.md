# SARM SDK 示例代码

这个目录包含了 SARM SDK 的使用示例，帮助您快速上手。

## 文件说明

### `quick_start.py`
快速入门示例，演示了基本的 SDK 使用方法：
- 客户端初始化
- 创建组织架构
- 管理安全能力
- 处理漏洞数据
- 基本的错误处理

### `complete_example.py`
完整的使用示例，展示了一个端到端的安全管理流程：
- 搭建完整的组织架构
- 配置安全扫描能力
- 管理业务系统和应用
- 处理载体和组件数据
- 管理漏洞和安全问题

## 使用方法

1. 确保已安装 SARM SDK：
   ```bash
   pip install sarm-sdk
   ```

2. 配置您的 API 信息：
   ```python
   client = SARMClient(
       base_url="https://your-platform.com",
       token="your-api-token"
   )
   ```

3. 运行示例：
   ```bash
   python quick_start.py
   python complete_example.py
   ```

## 前提条件

- Python 3.7+
- 有效的 SARM 平台 API 访问权限
- 正确的 API 端点和认证令牌

## 获取帮助

如果在运行示例时遇到问题，请：
1. 检查 API 端点和令牌是否正确
2. 查看完整的 SDK 文档
3. 查看故障排除指南

## 贡献

欢迎提交更多的示例代码，帮助其他开发者更好地使用 SARM SDK。 