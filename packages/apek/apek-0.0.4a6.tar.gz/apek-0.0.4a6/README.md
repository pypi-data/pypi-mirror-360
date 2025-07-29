# Introduction
`apek` is a Python package for handling large numbers. It represents large numbers using scientific notation `XeY` and provides rich functionalities to support operations and formatted display of large numbers.

# Features
- **Large Number Representation**: Represents large numbers using scientific notation through the `LargeNumber` class.
- **Precision Control**: Supports setting display precision and actual calculation precision.
- **Customizable Unit Tables**: Allows customization of English and Chinese unit tables for formatted display of large numbers.
- **Language Support**: Provides language setting functionality for help information, supporting English and Chinese.
- **Version Log**: Offers the ability to view version update logs.

# Installation
Install via pip: `pip install apek==0.0.4a6`

# Usage

## LargeNumber Class

```python
from apek.largeNumber import LargeNumber

# Create a LargeNumber instance
num = LargeNumber(1.2345, 6)  # Represents 1.2345e6

# Set precision and unit table
num = LargeNumber(1.2345, 6, dispPrec=2, reprUnits_en="KMBT")
print(num.parseString())  # Output the formatted string

# Operations
num1 = LargeNumber(1.2, 3)
num2 = LargeNumber(2.3, 4)
result = num1 + num2
print(result)  # Output the result of the operation
```

## Help Function

```python
from apek import helps

# Set language
helps.language("en")  # Set to English
helps.language("zh")  # Set to Chinese

# View version update log
helps.upgradeLog(ver="0.0.1")  # View the log for a specific version
```

## Example

```python
# Create a large number and perform operations
num1 = LargeNumber(1.2345, 10)
num2 = LargeNumber(6.789, 5)
result = num1 * num2
print(result.parseString(expReprMode="byUnit_en"))  # Output using unit table formatting
```

# Upgraded Contents
- New or changed:
  - Modified and optimized the code content.
- Fixes:
  - None

(Translated by Kimi)


***


# apek 包

# 简介
`apek`是一个用于处理大数字的Python包。它通过科学记数法"XeY"来表示大数字，并提供了一些功能来支持大数字的运算和格式化显示。

# 功能
- **大数字表示**：通过`LargeNumber`类，使用科学记数法表示大数字。
- **精度控制**：支持设置显示精度和实际计算精度。
- **单位表自定义**：可以自定义英文单位表和中文单位表，用于大数字的格式化显示。
- **语言支持**：提供帮助信息的语言设置功能，支持英文和中文。
- **版本日志**：提供版本更新日志的查看功能。

# 安装
通过pip安装：`pip install apek==0.0.4a6`

# 使用方法

## LargeNumber 类

```python
from apek import LargeNumber

# 创建LargeNumber实例
num = LargeNumber(1.2345, 6)  # 表示1.2345e6

# 设置精度和单位表
num = LargeNumber(1.2345, 6, dispPrec=2, reprUnits_en="KMBT")
print(num.parseString())  # 输出格式化后的字符串

# 运算
num1 = LargeNumber(1.2, 3)
num2 = LargeNumber(2.3, 4)
result = num1 + num2
print(result)  # 输出运算结果
```

## 帮助功能

```python
from apek import helps

# 设置语言
helps.language("en")  # 设置为英文
helps.language("zh")  # 设置为中文

# 查看版本更新日志
helps.upgradeLog(ver="0.0.1")  # 查看指定版本的日志
```

## 示例

```python
# 创建一个大数字并进行运算
num1 = LargeNumber(1.2345, 10)
num2 = LargeNumber(6.789, 5)
result = num1 * num2
print(result.parseString(expReprMode="byUnit_en"))  # 使用单位表格式化输出
```

# 更新内容
- 新增或更改：
  - 修改与优化了代码内容。
- 修复：
  - 无

(Write by Kimi)
