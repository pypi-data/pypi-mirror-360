#!/usr/bin/env python3
"""
BitFieldRW 使用示例
展示基本的位字段读写功能
"""

from bitfieldrw import BitFieldMixin, Float, Int, Uint, bitfield


@bitfield
class NetworkPacket(BitFieldMixin):
    """网络数据包示例"""

    version: Uint[4]  # 4位版本号
    header_len: Uint[4]  # 4位头长度
    type_of_service: Uint[8]  # 8位服务类型
    total_length: Uint[16]  # 16位总长度
    identification: Uint[16]  # 16位标识符
    flags: Uint[3]  # 3位标志
    fragment_offset: Uint[13]  # 13位片偏移


@bitfield
class NestedExample(BitFieldMixin):
    """嵌套结构示例"""

    header: NetworkPacket  # 嵌套的网络包头
    payload_size: Uint[16]  # 负载大小
    checksum: Uint[32]  # 校验和


def main():
    print("=== BitFieldRW 使用示例 ===\n")

    # 1. 基本使用
    print("1. 基本网络包示例:")
    packet = NetworkPacket()
    packet.version = 4
    packet.header_len = 5
    packet.type_of_service = 0
    packet.total_length = 1500
    packet.identification = 12345
    packet.flags = 2  # Don't Fragment
    packet.fragment_offset = 0

    print(f"版本: {packet.version}")
    print(f"头长度: {packet.header_len}")
    print(f"总长度: {packet.total_length}")
    print(f"标识符: {packet.identification}")
    print(f"标志: {packet.flags}")
    print(f"片偏移: {packet.fragment_offset}")

    # 2. 序列化为字节
    print("\n2. 序列化为字节:")
    data = packet.to_bytes()
    print(f"字节数据 (十六进制): {data.hex()}")
    print(f"字节长度: {len(data)} bytes")
    print(f"位长度: {packet.get_bit_length()} bits")

    # 3. 从字节反序列化
    print("\n3. 从字节反序列化:")
    new_packet = NetworkPacket()
    new_packet.from_bytes(data)
    print(f"版本: {new_packet.version}")
    print(f"头长度: {new_packet.header_len}")
    print(f"总长度: {new_packet.total_length}")
    print(f"标识符: {new_packet.identification}")

    # 4. 嵌套结构示例
    print("\n4. 嵌套结构示例:")
    nested = NestedExample()
    nested.header = packet  # 使用之前创建的包作为头部
    nested.payload_size = 1480
    nested.checksum = 0xABCDEF12

    print(f"嵌套结构位长度: {nested.get_bit_length()} bits")
    print(f"嵌套结构字节长度: {nested.get_byte_length()} bytes")

    # 5. 字节序示例
    print("\n5. 字节序示例:")
    big_endian_data = packet.to_bytes(byteorder="big")
    little_endian_data = packet.to_bytes(byteorder="little")

    print(f"大端序: {big_endian_data.hex()}")
    print(f"小端序: {little_endian_data.hex()}")

    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    main()
