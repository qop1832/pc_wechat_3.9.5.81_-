import pymem

db = {
    "friend_info": {
        "wxid": 0x40,  # 微信ID # Unicode
        "微信号": 0x60,  # 微信号 # Unicode
        # "V3数据": [0x80],  # V3数据 # Unicode  # 不知道有什么用
        "备注": 0xB0,  # 备注名 # Unicode
        "昵称": 0xD0,  # 昵称 # Unicode
        "昵称简拼": 0x138,  # 昵称简拼 # Unicode
        "昵称全拼": 0x158,  # 昵称全拼 # Unicode
        "备注简拼": 0x178,  # 备注简拼 # Unicode
        "备注全拼": 0x198,  # 备注全拼 # Unicode
        "大头像": 0x1B8,  # 大头像 # Unicode # 需在会话列表中
        "小头像": 0x1D8,  # 小头像 # Unicode # 需在会话列表中
        # "性别": [0x230, 0xE],  # 性别
        "签名": 0x2B0,  # 签名 # Unicode # 需在会话列表中
        "国家": 0x2D0,  # 国家 # Unicode # 需在会话列表中
        "省份": 0x308,  # 省份 # Unicode # 需在会话列表中
        "城市": 0x328,  # 城市 # Unicode # 需在会话列表中
        "朋友圈背景": 0x420,  # 朋友圈背景 # Unicode # 需在会话列表中
    }
}




def read_unicode_string(address):
    if address == 0: return ''
    if not pm.process_handle:
        raise pymem.exception.ProcessError('You must open a process before calling this method')

    buffer = bytearray()
    length = 0

    while True:
        data = pm.read_bytes(address + length, 2)  # 读取2个字节
        buffer += data
        length += 2
        # print(chr(buffer))
        # 检查读取的字节是否构成合法的 UTF-16 代理项
        if len(data) < 2 or (data[1] == 0x00 and data[0] == 0x00):
            break

    unicode_string = buffer.decode('utf-16-le', errors='ignore')  # 使用 'utf-16-le' 解码
    unicode_string = unicode_string.rstrip('\x00')
    return unicode_string


def read_friend_info(entry, max_counter=1):
    global gender
    counter = 0
    while counter < max_counter:
        friend_info = {}
        for key, offset in db["friend_info"].items():
            value = read_unicode_string(pm.read_longlong(entry + offset))
            gender_code = pm.read_int(pm.read_longlong(entry + 0x230) + 0xE)
            gender = "男" if gender_code == 1 else "女" if gender_code == 2 else "未知"
            friend_info[key] = value
        print(f"count > {str(counter)} entry > {hex(entry)} >> 好友信息: {str(friend_info)} 性别：{gender}")
        entry = pm.read_longlong(entry)
        counter += 1


if __name__ == '__main__':
    pm = pymem.Pymem("WeChat.exe")
    module_name = 'WeChatWin.dll'
    txl_addr_bast = 0x3A6F8C8  # "7e 48 a1 ?? ?? ?? ?? 85 c0 75 ?? 68 ?? ?? ?? ?? e8,3"   --- Version：3.9.2.23
    txl_entry_offset = 0xd8
    txl_size_offset = 0xd0
    module_addr = pymem.process.module_from_name(pm.process_handle, module_name).lpBaseOfDll
    txl_base = pm.read_longlong(module_addr + txl_addr_bast)
    txl_size = pm.read_int(txl_base + txl_size_offset)
    entry_addr = pm.read_longlong(pm.read_longlong(pm.read_longlong(txl_base + txl_entry_offset)))
    print('txl_size: ', txl_size)
    print('entry: ', hex(entry_addr))
    read_friend_info(entry_addr, txl_size)

