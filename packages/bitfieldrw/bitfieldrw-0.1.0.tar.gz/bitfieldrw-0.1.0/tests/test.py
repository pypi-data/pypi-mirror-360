import struct
import unittest

from bitfieldrw import BitFieldMixin, Float, Int, Uint, bitfield


class BitFieldRWTestCase(unittest.TestCase):
    """测试BitField读写库的全面功能测试案例"""

    def test_basic_unsigned_integers(self):
        """测试基本无符号整数类型"""

        @bitfield
        class BasicUint(BitFieldMixin):
            a: Uint[8]  # 8位无符号整数
            b: Uint[4]  # 4位无符号整数
            c: Uint[2]  # 2位无符号整数
            d: Uint[2]  # 2位无符号整数

        # 创建实例并设置值
        s = BasicUint()
        s.a = 0xFF  # 255 (8位最大值)
        s.b = 0xF  # 15 (4位最大值)
        s.c = 3  # 3 (2位最大值)
        s.d = 2  # 2

        # 验证值的正确性
        assert s.a == 255
        assert s.b == 15
        assert s.c == 3
        assert s.d == 2

        # 验证位长度
        assert s.get_bit_length() == 16
        assert s.get_byte_length() == 2

    def test_signed_integers(self):
        """测试有符号整数类型"""

        @bitfield
        class SignedInt(BitFieldMixin):
            positive: Int[8]  # 正数
            negative: Int[8]  # 负数
            zero: Int[4]  # 零值

        s = SignedInt()
        s.positive = 127  # 8位有符号最大正值
        s.negative = -128  # 8位有符号最小负值
        s.zero = 0  # 零值

        assert s.positive == 127
        assert s.negative == -128
        assert s.zero == 0

        # 测试范围检查
        with self.assertRaises(ValueError):
            s.positive = 128  # 超出范围
        with self.assertRaises(ValueError):
            s.negative = -129  # 超出范围

    def test_float_type(self):
        """测试32位浮点数类型"""

        @bitfield
        class FloatStruct(BitFieldMixin):
            value: Float[32]  # 32位浮点数
            flag: Uint[8]  # 8位标志位

        s = FloatStruct()

        # 测试正常浮点数
        s.value = 3.14159
        s.flag = 0xAA

        # 由于浮点数精度，使用近似比较
        self.assertAlmostEqual(s.value, 3.14159, places=5)
        assert s.flag == 0xAA

        # 测试特殊值
        s.value = 0.0
        assert s.value == 0.0

        # 测试负数
        s.value = -123.456
        self.assertAlmostEqual(s.value, -123.456, places=3)

    def test_endianness_big_endian(self):
        """测试大端序字节序列化和反序列化"""

        @bitfield
        class EndianTest(BitFieldMixin):
            high_byte: Uint[8]  # 高字节
            low_byte: Uint[8]  # 低字节

        s = EndianTest()
        s.high_byte = 0x12
        s.low_byte = 0x34

        # 大端序：高字节在前
        big_endian_bytes = s.to_bytes(byteorder="big")
        # 验证字节数组：high_byte=0x12, low_byte=0x34，大端序应为 0x12 0x34
        expected_big = b"\x12\x34"
        assert big_endian_bytes == expected_big, (
            f"大端序序列化不符合预期: {big_endian_bytes.hex()} != {expected_big.hex()}"
        )

        # 从大端序字节恢复
        s2 = EndianTest()
        s2.from_bytes(b"\x56\x78", byteorder="big")
        assert s2.high_byte == 0x56
        assert s2.low_byte == 0x78

    def test_endianness_little_endian(self):
        """测试小端序字节序列化和反序列化"""

        @bitfield
        class EndianTest(BitFieldMixin):
            high_byte: Uint[8]  # 高字节
            low_byte: Uint[8]  # 低字节

        s = EndianTest()
        s.high_byte = 0x12
        s.low_byte = 0x34

        # 小端序：低字节在前
        little_endian_bytes = s.to_bytes(byteorder="little")
        # 验证字节数组：high_byte=0x12, low_byte=0x34，小端序应为 0x34 0x12
        expected_little = b"\x34\x12"
        assert little_endian_bytes == expected_little, (
            f"小端序序列化不符合预期: {little_endian_bytes.hex()} != {expected_little.hex()}"
        )

        # 从小端序字节恢复
        s2 = EndianTest()
        s2.from_bytes(b"\x78\x56", byteorder="little")
        assert s2.high_byte == 0x56
        assert s2.low_byte == 0x78

    def test_hex_read_write(self):
        """测试十六进制数据的读写操作"""

        @bitfield
        class HexStruct(BitFieldMixin):
            addr: Uint[16]  # 16位地址
            cmd: Uint[8]  # 8位命令
            data: Uint[8]  # 8位数据

        s = HexStruct()

        # 设置十六进制值
        s.addr = 0x1234
        s.cmd = 0xAB
        s.data = 0xCD

        # 验证十六进制值
        assert s.addr == 0x1234
        assert s.cmd == 0xAB
        assert s.data == 0xCD

        # 转换为字节并验证
        bytes_data = s.to_bytes()
        # 验证字节数组：addr=0x1234, cmd=0xAB, data=0xCD
        # 大端序（默认）：0x12 0x34 0xAB 0xCD
        expected_hex = b"\x12\x34\xab\xcd"
        assert bytes_data == expected_hex, (
            f"十六进制序列化不符合预期: {bytes_data.hex()} != {expected_hex.hex()}"
        )

        # 从十六进制字节数据恢复
        s2 = HexStruct()
        s2.from_bytes(b"\xff\xee\xdd\xcc")
        assert s2.addr == 0xFFEE
        assert s2.cmd == 0xDD
        assert s2.data == 0xCC

    def test_nested_structures(self):
        """测试嵌套结构体"""

        # 定义内层结构
        @bitfield
        class InnerStruct(BitFieldMixin):
            x: Uint[4]  # 4位X坐标
            y: Uint[4]  # 4位Y坐标

        # 定义外层结构，包含嵌套结构
        @bitfield
        class OuterStruct(BitFieldMixin):
            position: InnerStruct  # 嵌套的位置结构
            flags: Uint[8]  # 8位标志
            value: Uint[8]  # 8位值

        # 创建外层结构实例
        outer = OuterStruct()

        # 创建内层结构实例并设置值
        inner = InnerStruct()
        inner.x = 5
        inner.y = 10

        # 设置嵌套结构
        outer.position = inner
        outer.flags = 0x55
        outer.value = 0xAA

        # 验证嵌套结构的访问
        assert outer.position.x == 5
        assert outer.position.y == 10
        assert outer.flags == 0x55
        assert outer.value == 0xAA

        # 验证总位长度
        assert outer.get_bit_length() == 24  # 8 + 8 + 8 = 24位
        assert outer.get_byte_length() == 3  # 3字节

        # 测试嵌套结构的序列化
        nested_bytes = outer.to_bytes()
        # position: x=5, y=10 -> 0x5A (5<<4 | 10)
        # flags: 0x55
        # value: 0xAA
        expected_nested = b"\x5a\x55\xaa"
        assert nested_bytes == expected_nested, (
            f"嵌套结构序列化不符合预期: {nested_bytes.hex()} != {expected_nested.hex()}"
        )

        # 测试从字节数据恢复嵌套结构
        outer2 = OuterStruct()
        outer2.from_bytes(b"\x3c\x99\xbb")
        # 0x3C = 0011 1100 -> x=3, y=12
        assert outer2.position.x == 3
        assert outer2.position.y == 12
        assert outer2.flags == 0x99
        assert outer2.value == 0xBB

    def test_nested_structures_deep(self):
        """测试深层嵌套结构体"""

        # 最内层结构
        @bitfield
        class Level3(BitFieldMixin):
            data: Uint[4]

        # 中间层结构
        @bitfield
        class Level2(BitFieldMixin):
            inner: Level3
            flag: Uint[2]

        # 最外层结构
        @bitfield
        class Level1(BitFieldMixin):
            nested: Level2
            value: Uint[8]

        # 创建深层嵌套结构
        level1 = Level1()
        level3 = Level3()
        level3.data = 0xF

        level2 = Level2()
        level2.inner = level3
        level2.flag = 2

        level1.nested = level2
        level1.value = 0x99

        # 验证深层访问
        assert level1.nested.inner.data == 0xF
        assert level1.nested.flag == 2
        assert level1.value == 0x99

    def test_bit_precision(self):
        """测试精确的二进制位数测试"""

        @bitfield
        class BitPrecision(BitFieldMixin):
            single_bit: Uint[1]  # 1位
            two_bits: Uint[2]  # 2位
            three_bits: Uint[3]  # 3位
            four_bits: Uint[4]  # 4位
            six_bits: Uint[6]  # 6位

        s = BitPrecision()

        # 测试1位字段
        s.single_bit = 1
        assert s.single_bit == 1
        with self.assertRaises(ValueError):
            s.single_bit = 2  # 超出1位范围

        # 测试2位字段
        s.two_bits = 3  # 最大值
        assert s.two_bits == 3
        with self.assertRaises(ValueError):
            s.two_bits = 4  # 超出2位范围

        # 测试3位字段
        s.three_bits = 7  # 最大值
        assert s.three_bits == 7
        with self.assertRaises(ValueError):
            s.three_bits = 8  # 超出3位范围

        # 测试4位字段
        s.four_bits = 15  # 最大值
        assert s.four_bits == 15

        # 测试6位字段
        s.six_bits = 63  # 最大值
        assert s.six_bits == 63

        # 验证总位数
        assert s.get_bit_length() == 16  # 1+2+3+4+6=16位

    def test_bit_layout_order(self):
        """测试位布局顺序（大端序布局）"""

        @bitfield
        class BitLayout(BitFieldMixin):
            first: Uint[4]  # 第一个字段（高4位）
            second: Uint[4]  # 第二个字段（低4位）

        s = BitLayout()
        s.first = 0xA  # 1010
        s.second = 0x5  # 0101

        # 验证整数表示：应该是0xA5 (10100101)
        assert s.to_int() == 0xA5

        # 从整数恢复
        s2 = BitLayout()
        s2.from_int(0xB7)  # 10110111
        assert s2.first == 0xB  # 高4位：1011
        assert s2.second == 0x7  # 低4位：0111

    def test_float_special_values(self):
        """测试浮点数特殊值"""

        @bitfield
        class FloatSpecial(BitFieldMixin):
            value: Float[32]

        s = FloatSpecial()

        # 测试正无穷大
        s.value = float("inf")
        assert s.value == float("inf")

        # 测试负无穷大
        s.value = float("-inf")
        assert s.value == float("-inf")

        # 测试NaN
        s.value = float("nan")
        assert str(s.value) == "nan"

    def test_complex_mixed_structure(self):
        """测试复杂混合结构（包含所有类型）"""

        @bitfield
        class Header(BitFieldMixin):
            version: Uint[4]  # 版本号
            type: Uint[4]  # 类型

        @bitfield
        class ComplexStruct(BitFieldMixin):
            header: Header  # 嵌套头部结构
            signed_val: Int[8]  # 有符号整数
            unsigned_val: Uint[8]  # 无符号整数
            float_val: Float[32]  # 浮点数
            flags: Uint[8]  # 标志位

        # 创建复杂结构
        s = ComplexStruct()

        # 设置头部
        header = Header()
        header.version = 2
        header.type = 5
        s.header = header

        # 设置其他字段
        s.signed_val = -50
        s.unsigned_val = 200
        s.float_val = 123.456
        s.flags = 0b11110000

        # 验证所有字段
        assert s.header.version == 2
        assert s.header.type == 5
        assert s.signed_val == -50
        assert s.unsigned_val == 200
        # 对于浮点数，保持原有的 assertAlmostEqual 比较方式
        self.assertAlmostEqual(s.float_val, 123.456, places=3)
        assert s.flags == 0b11110000

        # 验证总长度
        assert s.get_bit_length() == 64  # 8+8+8+32+8=64位
        assert s.get_byte_length() == 8  # 8字节

    def test_serialization_roundtrip(self):
        """测试序列化往返转换的完整性"""

        @bitfield
        class SerialTest(BitFieldMixin):
            a: Uint[8]
            b: Int[8]
            c: Uint[16]

        # 原始数据
        original = SerialTest()
        original.a = 0x12
        original.b = -45
        original.c = 0x3456

        # 序列化为字节（大端序）
        big_bytes = original.to_bytes(byteorder="big")

        # 验证大端序字节数组是否符合预期
        # a=0x12, b=-45(0xD3), c=0x3456
        # 大端序: 0x12 0xD3 0x34 0x56
        expected_big = b"\x12\xd3\x34\x56"
        assert big_bytes == expected_big, (
            f"大端序序列化结果不符合预期: {big_bytes.hex()} != {expected_big.hex()}"
        )

        # 反序列化
        restored_big = SerialTest()
        restored_big.from_bytes(big_bytes, byteorder="big")

        # 验证数据完整性
        assert restored_big.a == original.a
        assert restored_big.b == original.b
        assert restored_big.c == original.c

        # 序列化为字节（小端序）
        little_bytes = original.to_bytes(byteorder="little")

        # 验证小端序字节数组是否符合预期
        # a=0x12, b=-45(0xD3), c=0x3456
        # 小端序: 0x12 0xD3 0x56 0x34 (c字段的字节顺序颠倒)
        expected_little = b"\x56\x34\xd3\x12"
        assert little_bytes == expected_little, (
            f"小端序序列化结果不符合预期: {little_bytes.hex()} != {expected_little.hex()}"
        )

        # 反序列化
        restored_little = SerialTest()
        restored_little.from_bytes(little_bytes, byteorder="little")

        # 验证数据完整性
        assert restored_little.a == original.a
        assert restored_little.b == original.b
        assert restored_little.c == original.c

    def test_error_handling(self):
        """测试错误处理和边界条件"""

        @bitfield
        class ErrorTest(BitFieldMixin):
            small_field: Uint[4]

        s = ErrorTest()

        # 测试类型错误
        with self.assertRaises(TypeError):
            s.small_field = "not_a_number"

        # 测试范围错误
        with self.assertRaises(ValueError):
            s.small_field = 16  # 超出4位无符号整数范围

        # 测试负数给无符号字段
        with self.assertRaises(ValueError):
            s.small_field = -1

    def test_repr_string(self):
        """测试字符串表示"""

        @bitfield
        class ReprTest(BitFieldMixin):
            a: Uint[8]
            b: Uint[4]

        s = ReprTest()
        s.a = 100
        s.b = 5

        # 验证字符串表示包含字段名和值
        repr_str = repr(s)
        assert "ReprTest" in repr_str
        assert "a=100" in repr_str
        assert "b=5" in repr_str


if __name__ == "__main__":
    unittest.main()
