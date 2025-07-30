# BitFieldRW 发布说明

## 版本 0.1.1

### 改进

- ✅ 抑制设置 int 或 float 值到类属性时的警告信息

## 版本 0.1.0 (首次发布)

### 新功能

- ✅ 基本位字段读写功能
- ✅ 支持类型注解的位字段定义
- ✅ 多种数据类型支持：无符号整数、有符号整数、浮点数
- ✅ 嵌套结构体支持
- ✅ 大端序和小端序字节序支持
- ✅ 完整的单元测试覆盖

### 支持的数据类型

- `Uint[n]` - n 位无符号整数 (1-64 位)
- `Int[n]` - n 位有符号整数 (1-64 位)
- `Float[32]` - 32 位 IEEE 754 浮点数

### 主要特性

- **类型安全**: 使用 Python 类型注解
- **灵活布局**: 支持任意位宽的字段
- **字节序控制**: 支持大端序和小端序
- **嵌套支持**: 位字段结构可以嵌套
- **完整测试**: 包含全面的测试用例

### 使用示例

```python
from bitfieldrw import bitfield, BitFieldMixin, Uint, Int

@bitfield
class Packet(BitFieldMixin):
    version: Uint[4]
    header_len: Uint[4]
    total_length: Uint[16]

packet = Packet()
packet.version = 4
packet.header_len = 5
packet.total_length = 1500

# 序列化为字节
data = packet.to_bytes()

# 从字节反序列化
new_packet = Packet()
new_packet.from_bytes(data)
```

### 安装方法

```bash
pip install bitfieldrw
```

### 依赖项

- Python 3.8+
- 无外部依赖

### 项目链接

- GitHub: https://github.com/DawnMagnet/bitfieldrw
- PyPI: https://pypi.org/project/bitfieldrw/

### 下一步计划

- 添加更多数据类型支持 (如字符串、数组)
- 性能优化
- 更多实用工具函数
- 文档完善

---

感谢使用 BitFieldRW！如果遇到任何问题，请在 GitHub 上提交 issue。
