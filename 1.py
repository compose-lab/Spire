records = []

import json

FILE = "records.json"

def load_records():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_records(rs):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(rs, f, ensure_ascii=False, indent=2)

def show_menu():
    print("1 记一笔")
    print("2 看全部")
    print("3 退出")

def main():
    records = load_records()
    while True:
        show_menu()
        choice = input("请选择: ")
        if choice == "3":
            save_records(records)
            break
        elif choice == "1":
            parts = input("请输入金额与备注:").split()
            if len(parts) < 2:
                print("请按 [金额 备注] 输入两项，中间用空格隔开")
                continue
            try:
                money = int(parts[0])
            except ValueError:
                print("金额必须是数字")
                continue
            tips = parts[1]
            records.append({"备注":tips, "金额":money})
            save_records(records)
            print("已记录")
            pass
        elif choice == "2":
            if not records:
                print("还没有记录")
            else:
                for i in records:
                    print(i["金额"], i["备注"])
        else:
            print("输入不对，请重来")

main()