# 安全配置指南

## 配置传递方案

本项目采用**多层次安全配置策略**，按优先级顺序：

### 1. .env文件（推荐 ⭐）
```bash
# 生成.env文件
python generate_debug_config.py env

# 自动加载，无需额外配置
# 支持Windows、Linux、macOS
```

.env文件示例：
```bash
# 加密配置
WATER_QUALITY_ENCRYPTION_KEY=64个十六进制字符
WATER_QUALITY_SALT=32个十六进制字符  
WATER_QUALITY_IV=32个十六进制字符

# 调试配置（可选）
DEBUG_ZIP_PATH=/path/to/test.zip
DEBUG_CSV_PATH=/path/to/test.csv
```

### 2. 环境变量
```bash
# 直接设置环境变量（覆盖.env文件）
export WATER_QUALITY_ENCRYPTION_KEY="your_32_byte_key_here"
export WATER_QUALITY_SALT="your_16_byte_salt"
export WATER_QUALITY_IV="your_16_byte_iv"
```

### 3. JSON配置文件
```bash
# 指定配置文件路径
export WATER_QUALITY_CONFIG_FILE="/path/to/config.json"
```

配置文件格式 (`config.json`):
```json
{
  "encryption_key": "64个十六进制字符代表32字节密钥",
  "salt": "32个十六进制字符代表16字节盐值",
  "iv": "32个十六进制字符代表16字节初始化向量",
  "created_time": "2025-01-01 00:00:00",
  "note": "请在生产环境中使用更强的密钥生成方法"
}
```

### 3. 二进制密钥文件
```bash
# 指定密钥文件路径
export WATER_QUALITY_KEY_FILE="/path/to/secret.key"
```

密钥文件格式：64字节二进制文件
- 前32字节：加密密钥
- 中间16字节：盐值
- 后16字节：初始化向量

### 4. 动态生成（最低优先级）
如果以上都未配置，系统将动态生成临时密钥，但**数据无法在重启后解密**。

## 使用方法

### 生成配置文件

#### 一键生成（推荐）
```bash
# 生成.env文件（包含所有配置）
python generate_debug_config.py env

# 生成所有类型的配置文件
python generate_debug_config.py security
```

#### 编程方式生成
```python
from model_finetune.utils import ConfigManager

# 生成.env文件
ConfigManager.generate_env_file(".env")

# 生成JSON配置文件
ConfigManager.generate_sample_config_file("./config.json")

# 生成二进制密钥文件
ConfigManager.generate_key_file("./secret.key")
```

### 在生产环境中使用

#### 方案A：.env文件（推荐 ⭐）
```bash
# 1. 生成.env文件
python generate_debug_config.py env

# 2. 验证配置
cat .env

# 3. 运行程序（自动加载.env）
python interface.py
```

#### 方案B：环境变量
```bash
# 1. 生成强密钥
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('SALT=' + secrets.token_hex(16))"
python -c "import secrets; print('IV=' + secrets.token_hex(16))"

# 2. 设置环境变量
export WATER_QUALITY_ENCRYPTION_KEY="生成的密钥"
export WATER_QUALITY_SALT="生成的盐值"
export WATER_QUALITY_IV="生成的IV"

# 3. 运行程序
python interface.py
```

#### 方案C：JSON配置文件
```bash
# 1. 生成配置文件
python generate_debug_config.py security

# 2. 设置配置文件路径
export WATER_QUALITY_CONFIG_FILE="./security_config.json"

# 3. 设置文件权限（Linux/Mac）
chmod 600 ./security_config.json

# 4. 运行程序
python interface.py
```

#### 方案D：密钥文件
```bash
# 1. 生成密钥文件
python generate_debug_config.py security

# 2. 设置密钥文件路径
export WATER_QUALITY_KEY_FILE="./security.key"

# 3. 运行程序
python interface.py
```

## 安全建议

### ✅ 推荐做法
1. **生产环境必须使用环境变量或独立配置文件**
2. **定期轮换密钥**
3. **限制配置文件访问权限** (`chmod 600`)
4. **备份密钥到安全位置**
5. **使用密钥管理服务**（如AWS KMS、Azure Key Vault）

### ❌ 避免做法
1. **不要在代码中硬编码密钥**
2. **不要将配置文件提交到版本控制**
3. **不要在日志中输出密钥信息**
4. **不要使用相同密钥于不同环境**

### 🔐 企业级部署
```bash
# 使用Docker时的密钥注入
docker run -e WATER_QUALITY_ENCRYPTION_KEY="$(cat /secure/key.txt)" \
           -e WATER_QUALITY_SALT="$(cat /secure/salt.txt)" \
           -e WATER_QUALITY_IV="$(cat /secure/iv.txt)" \
           your-app:latest

# 使用Kubernetes Secret
kubectl create secret generic water-quality-secrets \
  --from-literal=encryption-key="your-key" \
  --from-literal=salt="your-salt" \
  --from-literal=iv="your-iv"
```

## 故障排除

### 常见问题
1. **"使用动态生成的临时加密密钥"警告**
   - 原因：未配置任何加密密钥
   - 解决：按上述方案配置密钥

2. **"从配置文件加载加密配置失败"**
   - 检查文件路径是否正确
   - 检查JSON格式是否有效
   - 检查文件权限

3. **"数据无法解密"**
   - 确认使用相同的密钥、盐值和IV
   - 检查密钥长度是否正确

### 密钥规范
- **加密密钥**：32字节（256位）
- **盐值**：16字节（128位）
- **初始化向量**：16字节（128位）

## 示例：完整的生产部署脚本

```bash
#!/bin/bash
# production_deploy.sh

# 1. 创建安全目录
mkdir -p /opt/water-quality/secrets
chmod 700 /opt/water-quality/secrets

# 2. 生成密钥
python3 -c "
import secrets
import json
config = {
    'encryption_key': secrets.token_hex(32),
    'salt': secrets.token_hex(16), 
    'iv': secrets.token_hex(16)
}
with open('/opt/water-quality/secrets/config.json', 'w') as f:
    json.dump(config, f)
"

# 3. 设置权限
chmod 600 /opt/water-quality/secrets/config.json

# 4. 设置环境变量
export WATER_QUALITY_CONFIG_FILE="/opt/water-quality/secrets/config.json"

# 5. 启动应用
cd /opt/water-quality
python3 interface.py

echo "✅ 生产环境部署完成，密钥已安全配置"
```

这种多层次配置策略既保证了安全性，又提供了灵活性，适合不同的部署场景。