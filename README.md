# iotest
Disk performance testing  
## 使用方法
注：需要安装好fio和libaio，并且安装了python3，python3的版本要在3.6.0及以上  
参考[这篇文章](https://starstao.com/2025/03/linux-vps-use-fio-to-comprehensively-test-disk-performance)安装fio和libaio
### 下载iotest.py
curl -O https://raw.githubusercontent.com/starstao/iotest/refs/heads/main/iotest.py
### 执行iotest.py
python3 iotest.py
### 测试结果
```
python3 iotest.py 

正在执行测试：小文件随机读

正在执行测试：小文件随机写

正在执行测试：大文件随机读

正在执行测试：大文件随机写

正在执行测试：异步测试最大读IOPS

正在执行测试：异步测试最大写IOPS

========================== 测试结果汇总 ==========================
测试类型           | 读带宽(MiB/s) |   读IOPS | 写带宽(MiB/s) |  写IOPS
-----------------------------------------------------------
小文件随机读       |        140.77 |  9009.60 |          0.00 |    0.00
小文件随机写       |          0.00 |     0.00 |         86.46 | 5533.47
大文件随机读       |       2261.64 |   226.16 |          0.00 |    0.00
大文件随机写       |          0.00 |     0.00 |        718.59 |   71.86
异步测试最大读IOPS |         98.98 | 25337.84 |          0.00 |    0.00
异步测试最大写IOPS |          0.00 |     0.00 |         37.23 | 9529.94

=========================== 峰值性能 ===========================
最大读IOPS:             25337.84
最大写IOPS:             9529.94
```
