import subprocess
import json
import unicodedata

# 定义计算显示宽度的函数
def display_width(s):
    """计算字符串的显示宽度，中文占2，英文/数字占1"""
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2  # 全宽字符
        else:
            width += 1  # 半宽字符
    return width

# 定义要执行的 fio 测试列表
tests = [
    {
        "name": "小文件随机读",
        "command": "fio -filename=iotestfile -direct=1 -iodepth=1 -rw=randread -ioengine=psync -bs=16k -size=1G -numjobs=10 -runtime=5 -group_reporting -name=mytest --output-format=json"
    },
    {
        "name": "小文件随机写",
        "command": "fio -filename=iotestfile -direct=1 -iodepth=1 -rw=randwrite -ioengine=psync -bs=16k -size=1G -numjobs=10 -runtime=5 -group_reporting -name=mytest --output-format=json"
    },
    {
        "name": "大文件随机读",
        "command": "fio -filename=iotestfile -direct=1 -iodepth=1 -rw=randread -ioengine=psync -bs=10M -size=1G -numjobs=10 -runtime=5 -group_reporting -name=mytest --output-format=json"
    },
    {
        "name": "大文件随机写",
        "command": "fio -filename=iotestfile -direct=1 -iodepth=1 -rw=randwrite -ioengine=psync -bs=10M -size=1G -numjobs=10 -runtime=5 -group_reporting -name=mytest --output-format=json"
    },
    {
        "name": "异步测试最大读IOPS",
        "command": "fio -filename=iotestfile -direct=1 -iodepth=32 -rw=randread -ioengine=libaio -bs=4k -size=100M -numjobs=10 -runtime=5 -group_reporting -name=mytest --output-format=json"
    },
    {
        "name": "异步测试最大写IOPS",
        "command": "fio -filename=iotestfile -direct=1 -iodepth=32 -rw=randwrite -ioengine=libaio -bs=4k -size=100M -numjobs=10 -runtime=5 -group_reporting -name=mytest --output-format=json"
    },
]

results = []

def parse_fio_output(json_data, test_type):
    """解析 fio JSON 输出并提取性能指标"""
    job = json_data['jobs'][0]
    result = {
        'read_bw': job['read']['bw'] / 1024.0 if 'read' in job else 0,  # 转换为 MiB/s
        'read_iops': job['read']['iops'] if 'read' in job else 0,
        'write_bw': job['write']['bw'] / 1024.0 if 'write' in job else 0,  # 转换为 MiB/s
        'write_iops': job['write']['iops'] if 'write' in job else 0
    }
    return result

for test in tests:
    print(f"\n正在执行测试：{test['name']}")
    try:
        cmd_args = test['command'].split()
        # 使用 stdout=subprocess.PIPE 和 stderr=subprocess.PIPE 捕获输出
        # universal_newlines=True 确保输出为字符串
        result = subprocess.run(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, check=True)
        json_data = json.loads(result.stdout)
        test_result = parse_fio_output(json_data, test['name'])
        test_result['name'] = test['name']
        results.append(test_result)
    except subprocess.CalledProcessError as e:
        print(f"测试失败：{e.stderr}")
    except json.JSONDecodeError:
        print("JSON 解析失败")
    except KeyError:
        print("输出格式异常")

# 打印结果表格
print("\n{:=^60}".format(" 测试结果汇总 "))

# 定义表头和数据行
headers = ["测试类型", "读带宽(MiB/s)", "读IOPS", "写带宽(MiB/s)", "写IOPS"]
data_rows = [[res['name'], f"{res['read_bw']:.2f}", f"{res['read_iops']:.2f}", 
              f"{res['write_bw']:.2f}", f"{res['write_iops']:.2f}"] for res in results]
all_rows = [headers] + data_rows

# 计算每列的最大显示宽度
column_widths = [max(display_width(row[i]) for row in all_rows) for i in range(5)]

# 定义对齐方式
alignments = ['left', 'right', 'right', 'right', 'right']

# 定义格式化一行的函数
def format_row(row, column_widths, alignments):
    formatted_cells = []
    for i, cell in enumerate(row):
        w = display_width(cell)
        pad = column_widths[i] - w
        if alignments[i] == 'left':
            formatted_cells.append(cell + ' ' * pad)  # 左对齐，空格在后
        else:
            formatted_cells.append(' ' * pad + cell)  # 右对齐，空格在前
    return " | ".join(formatted_cells)

# 打印表头和分隔线
formatted_header = format_row(headers, column_widths, alignments)
print(formatted_header)
print("-" * len(formatted_header))

# 打印数据行
for row in data_rows:
    print(format_row(row, column_widths, alignments))

# 计算最大 IOPS
try:
    max_read_iops = max([res['read_iops'] for res in results if res['read_iops'] > 0])
    max_write_iops = max([res['write_iops'] for res in results if res['write_iops'] > 0])
except ValueError:
    max_read_iops = 0
    max_write_iops = 0

print("\n{:=^60}".format(" 峰值性能 "))
print(f"{'最大读IOPS:':<20} {max_read_iops:.2f}")
print(f"{'最大写IOPS:':<20} {max_write_iops:.2f}")
