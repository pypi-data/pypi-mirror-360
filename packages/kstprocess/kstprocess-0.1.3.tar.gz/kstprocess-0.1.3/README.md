
## 打包和上传pypi命令
```python
python3 setup.py sdist bdist_wheel
twine upload dist/*
```

## 第一步：处理原始数据

快商通-总后台-机器人-对话记录：导出的文件:2025年07月07日10时15分49秒-对话记录导出.xlsx。

```python


process_data(
    input_file_path='./接入数据-对话流.xlsx',
    output_file_path='./版本_主题_对话流.xlsx'
)
```

## 第二步：绘制对比图
```python

plot_comparison(
    file1_path='./版本_主题_候选话术库_kicp_gpt.xlsx',
    file2_path='./版本_主题_kicp-GPT.xlsx',
    prefix1='候选话术库_kicp_gpt',
    prefix2='kicp-GPT',
    save_path='./留联率对比.jpg',
    min_valid_conversations=5,
)
```