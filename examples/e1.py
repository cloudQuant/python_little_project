import pandas as pd

# 示例数据
data = {
    'Gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
    'Purchase Intention': ['Yes', 'No', 'Yes', 'Yes', 'No', 'No', 'Yes', 'Yes', 'No', 'No']
}

df = pd.DataFrame(data)

# 创建交叉表
cross_tab = pd.crosstab(df['Gender'], df['Purchase Intention'])

print(cross_tab)