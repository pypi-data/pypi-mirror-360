# 配置使用示例

本文档提供了Model Finetune项目各种配置方式的详细示例。

## 🚀 快速开始

### 1. 一键配置（推荐新手）

```bash
# 生成完整的.env配置文件
python setup_config.py env

# 检查生成的配置
cat .env

# 直接运行程序（自动加载.env）
python interface.py
```

### 2. 为调试添加测试数据

编辑生成的`.env`文件，取消注释并修改测试路径：

```bash
# 编辑.env文件
nano .env

# 修改以下行（去掉#注释）
DEBUG_ZIP_PATH=/path/to/your/test_data.zip
DEBUG_CSV_PATH=/path/to/your/test_measure.csv
```

## 📋 详细配置示例

### .env文件配置（⭐ 推荐）

**.env文件内容示例：**
```bash
# 必需的安全配置
WATER_QUALITY_ENCRYPTION_KEY=1855da07b41ca0d263e3a47a744edf25edda6722069d5b26d6cccd1dae822a17
WATER_QUALITY_SALT=b0e8621b6201b1a715ac77f34da3fe45
WATER_QUALITY_IV=54464157adc56655b441d2b1efd38a32

# 调试配置（开发环境）
DEBUG_ZIP_PATH=D:/data/test_sample.zip
DEBUG_CSV_PATH=D:/data/test_measure.csv

# 输出目录（可选）
OUTPUT_DIR=./my_model_output

# 日志级别（可选）
LOG_LEVEL=INFO
```

**特点：**
- ✅ 跨平台（Windows/Linux/macOS）
- ✅ 自动加载，无需手动设置环境变量
- ✅ 支持注释和分组
- ✅ 可以版本控制（记得加入.gitignore）

### 环境变量配置

#### Windows (PowerShell)
```powershell
# 设置环境变量
$env:WATER_QUALITY_ENCRYPTION_KEY="your_encryption_key_here"
$env:WATER_QUALITY_SALT="your_salt_here"
$env:WATER_QUALITY_IV="your_iv_here"

# 调试配置
$env:DEBUG_ZIP_PATH="C:\data\test.zip"
$env:DEBUG_CSV_PATH="C:\data\test.csv"

# 运行程序
python interface.py
```

#### Windows (CMD)
```cmd
REM 设置环境变量
set WATER_QUALITY_ENCRYPTION_KEY=your_encryption_key_here
set WATER_QUALITY_SALT=your_salt_here
set WATER_QUALITY_IV=your_iv_here

REM 调试配置
set DEBUG_ZIP_PATH=C:\data\test.zip
set DEBUG_CSV_PATH=C:\data\test.csv

REM 运行程序
python interface.py
```

#### Linux/macOS (Bash)
```bash
# 设置环境变量
export WATER_QUALITY_ENCRYPTION_KEY="your_encryption_key_here"
export WATER_QUALITY_SALT="your_salt_here"
export WATER_QUALITY_IV="your_iv_here"

# 调试配置
export DEBUG_ZIP_PATH="/path/to/test.zip"
export DEBUG_CSV_PATH="/path/to/test.csv"

# 运行程序
python interface.py
```

### JSON配置文件

**security_config.json:**
```json
{
  "encryption_key": "1855da07b41ca0d263e3a47a744edf25edda6722069d5b26d6cccd1dae822a17",
  "salt": "b0e8621b6201b1a715ac77f34da3fe45",
  "iv": "54464157adc56655b441d2b1efd38a32",
  "created_time": "2025-07-02 15:47:36",
  "note": "请妥善保管此配置文件"
}
```

**使用方式：**
```bash
# 生成配置文件
python setup_config.py security

# 指定配置文件路径
export WATER_QUALITY_CONFIG_FILE="./security_config.json"

# 运行程序
python interface.py
```

### 调试配置文件

**debug_config.json:**
```json
{
  "file_url": "./downloads/sample_data.zip",
  "measure_data": "./downloads/sample_measure.csv",
  "note": "调试模式配置文件",
  "usage": {
    "environment_variables": {
      "DEBUG_ZIP_PATH": "ZIP文件路径",
      "DEBUG_CSV_PATH": "CSV文件路径"
    }
  }
}
```

## 🔧 不同场景的配置方案

### 场景1：开发环境

```bash
# 1. 生成.env文件
python setup_config.py env

# 2. 编辑.env添加测试数据路径
echo "DEBUG_ZIP_PATH=./test_data/sample.zip" >> .env
echo "DEBUG_CSV_PATH=./test_data/measure.csv" >> .env

# 3. 调试运行
python src/model_finetune/main.py --debug
```

### 场景2：生产环境

```bash
# 1. 生成强密钥
python setup_config.py security

# 2. 设置环境变量（不使用.env文件）
export WATER_QUALITY_CONFIG_FILE="/secure/path/security_config.json"

# 3. 设置文件权限
chmod 600 /secure/path/security_config.json

# 4. 运行程序
python interface.py
```

### 场景3：Docker容器

**Dockerfile:**
```dockerfile
FROM python:3.10

WORKDIR /app
COPY . .

# 安装依赖
RUN pip install -e .

# 设置默认环境变量
ENV LOG_LEVEL=INFO
ENV OUTPUT_DIR=/app/output

CMD ["python", "interface.py"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  model-finetune:
    build: .
    environment:
      - WATER_QUALITY_ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - WATER_QUALITY_SALT=${SALT}
      - WATER_QUALITY_IV=${IV}
    volumes:
      - ./data:/app/data
      - ./output:/app/output
    env_file:
      - .env
```

### 场景4：CI/CD管道

**GitHub Actions示例：**
```yaml
name: Test Model Finetune
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Generate test config
      run: python setup_config.py env
    
    - name: Run tests
      env:
        DEBUG_ZIP_PATH: ./tests/fixtures/test.zip
        DEBUG_CSV_PATH: ./tests/fixtures/test.csv
      run: |
        pip install -e .
        python -m pytest
```

## 🛠️ 故障排除

### 问题1：配置文件未找到

```bash
# 检查当前目录
ls -la .env

# 检查环境变量
env | grep WATER_QUALITY

# 重新生成配置
python setup_config.py env
```

### 问题2：权限问题

```bash
# Linux/macOS
chmod 600 .env
chmod 600 security_config.json

# Windows (PowerShell管理员)
icacls .env /inheritance:r /grant:r "$env:USERNAME:F"
```

### 问题3：编码问题

```bash
# 确保文件是UTF-8编码
file .env
head -c 3 .env | od -c  # 检查BOM

# 重新生成配置文件
rm .env
python setup_config.py env
```

### 问题4：调试模式无法找到测试文件

```bash
# 检查路径是否正确
ls -la "$DEBUG_ZIP_PATH"
ls -la "$DEBUG_CSV_PATH"

# 使用绝对路径
export DEBUG_ZIP_PATH="/full/path/to/test.zip"
export DEBUG_CSV_PATH="/full/path/to/test.csv"
```

## 📚 配置优先级

配置项按以下优先级生效（高优先级覆盖低优先级）：

1. **环境变量** (最高)
2. **.env文件**
3. **JSON配置文件**
4. **二进制密钥文件**
5. **动态生成** (最低，仅临时使用)

## 🔒 安全最佳实践

1. **永远不要提交敏感配置到版本控制**
   ```bash
   # 确保.gitignore包含：
   .env
   *.env
   security_config.json
   security.key
   ```

2. **生产环境使用强密钥**
   ```bash
   # 使用密码学安全的随机生成器
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **定期轮换密钥**
   ```bash
   # 备份旧配置
   cp .env .env.backup.$(date +%Y%m%d)
   
   # 生成新配置
   python setup_config.py env
   ```

4. **限制文件访问权限**
   ```bash
   # 仅所有者可读写
   chmod 600 .env security_config.json security.key
   ```

5. **使用专业的密钥管理服务**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Kubernetes Secrets

这些配置方案可以满足从开发到生产的各种需求，选择最适合你环境的方案即可。