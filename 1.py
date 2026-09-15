"""记账本

数据存在 records.json：一个列表，每项形如 {"备注": "买菜", "金额": 300}
"""

import json
import os

FILE = "records.json"


# ==================== 读写文件 ====================

def load_records():
    """读记录。文件不存在、是空的、内容坏了，都当作空账本，不让程序崩掉。"""
    try:
        # utf-8-sig 而不是 utf-8：记事本另存的文件开头可能带 BOM，
        # 用 utf-8 读会把这个 BOM 当成内容，json 直接解析失败。
        with open(FILE, "r", encoding="utf-8-sig") as f:
            text = f.read()
    except FileNotFoundError:
        return []

    if not text.strip():
        return []          # 空文件就是空账本，没什么可警告的

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # 文件被改坏了。先备份再当空账本，免得后面保存时把原数据彻底覆盖掉。
        backup = FILE + ".bak"
        try:
            os.replace(FILE, backup)
            print(f"警告：{FILE} 不是合法的 JSON，已备份为 {backup}")
        except OSError:
            print(f"警告：{FILE} 不是合法的 JSON，本次当作空账本")
        return []

    if not isinstance(data, list):
        print(f"警告：{FILE} 里不是一个列表，本次当作空账本")
        return []

    # 逐条检查，跳过被手改坏的记录，而不是整份丢掉
    good = []
    for item in data:
        if isinstance(item, dict) and isinstance(item.get("金额"), (int, float)):
            good.append(item)
        else:
            print(f"警告：跳过一条看不懂的记录：{item!r}")
    return good


def save_records(records):
    """整体覆盖写入。每次改动后立刻调用，所以中途 Ctrl+C 也不会丢数据。"""
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# ==================== 金额 ====================

def parse_amount(text):
    """把输入转成金额，支持整数和小数。转不了返回 None。

    先试 int 再试 float：这样 300 会存成整数 300，而不是 300.0。
    """
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return None


def format_amount(money):
    """300 -> '300'，12.5 -> '12.50'，显示整齐一点。"""
    if isinstance(money, float):
        if money.is_integer():
            return str(int(money))
        return f"{money:.2f}"
    return str(money)


# ==================== 界面 ====================

def show_menu():
    print()
    print("1 记一笔")
    print("2 看全部")
    print("3 看合计")
    print("4 删一笔")
    print("5 退出")


def show_all(records):
    if not records:
        print("还没有记录")
        return
    for i, r in enumerate(records, start=1):
        print(f"{i}. {format_amount(r['金额'])} 元   {r['备注']}")


def show_total(records):
    if not records:
        print("还没有记录")
        return
    total = 0
    for r in records:
        total += r["金额"]
    print(f"共 {len(records)} 笔，合计 {format_amount(total)} 元")


def ask_record():
    """问一次输入，返回 (备注, 金额)；想取消就返回 None。"""
    line = input("输入 [金额 备注]（直接回车取消）: ").strip()
    if not line:
        return None

    parts = line.split()
    if len(parts) < 2:
        print("要两项：金额和备注，中间用空格隔开")
        return None

    money = parse_amount(parts[0])
    if money is None:
        print(f"金额必须是数字，你输入的是「{parts[0]}」")
        return None

    # 关键：把第 2 项之后的全部拼回来，备注里有空格也不会被丢掉
    tip = " ".join(parts[1:])
    return tip, money


def delete_record(records):
    """按编号删一笔。真删掉了返回 True。"""
    if not records:
        print("还没有记录")
        return False

    show_all(records)
    raw = input("删第几笔？（直接回车取消）: ").strip()
    if not raw:
        return False

    try:
        index = int(raw) - 1
    except ValueError:
        print("请输入一个编号数字")
        return False

    if not 0 <= index < len(records):
        print(f"编号要在 1 到 {len(records)} 之间")
        return False

    removed = records.pop(index)
    print(f"已删除：{format_amount(removed['金额'])} 元   {removed['备注']}")
    return True


# ==================== 主流程 ====================

def main():
    # records 是 main 的局部变量，靠参数传给别的函数，不靠全局变量
    records = load_records()
    print(f"已载入 {len(records)} 笔记录")

    while True:
        show_menu()
        choice = input("请选择: ").strip()

        if choice == "1":
            got = ask_record()
            if got is None:
                continue
            tip, money = got
            records.append({"备注": tip, "金额": money})
            save_records(records)          # 一改就存，不等到退出
            print("已记录")

        elif choice == "2":
            show_all(records)

        elif choice == "3":
            show_total(records)

        elif choice == "4":
            if delete_record(records):
                save_records(records)

        elif choice == "5":
            print("再见")
            break

        else:
            print("输入不对，请重来")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n已退出")
