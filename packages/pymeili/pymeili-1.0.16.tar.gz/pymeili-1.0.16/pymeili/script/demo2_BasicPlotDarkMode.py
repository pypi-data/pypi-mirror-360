# Import the module / 引入套件
import beautifyplot as bp
import numpy as np

# Set image path / 設定圖片路徑
img_path = __file__[:-len(__file__.split('\\')[-1])]+ "\\img\\"

# Set the default mode / 設定預設模式
bp.default()

# Initialize the plot with specific figsize and theme / 初始化圖表，並設定特定的 figsize 和 theme
bp.initplot(figsize=(10, 5), theme='d')

# Bar plot / 長條圖
bp.bar(np.array([1.5, 2.5, 3.5])-0.1, [3, 2, 1], width=0.2, label='bp.bar1')
bp.bar(np.array([1.5, 2.5, 3.5])+0.1, [1, 2, 3], width=0.2, label='bp.bar2', color='fg5')

# Add text / 加上文字
bp.text(2.8, 1.5, 'TEXTTEXTTEXT')

# Set the title / 設定標題
bp.lefttitle('DEMO 2')
bp.righttitle('Basic Plot (Dark)')

# Set labels / 設定標籤
bp.xlabel('X LABEL')
bp.ylabel('Y LABEL')

# Set ticks / 設定刻度
bp.xticks([1, 2, 3, 4])
bp.yticks([0, 1, 2, 3])

# Set spines / 設定脊梁
bp.spines()

# Set grid only for y-axis / 只設定 y 軸的格線
bp.grid(axis='y')

# Add legend / 加上圖例
bp.legend()

# Save the plot / 儲存圖表
bp.savefig(f'{img_path}demo2_BasicPloyDarkMode.png')

# Close the plot / 關閉圖表
bp.close()