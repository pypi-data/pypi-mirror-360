# Import the module / 引入套件
import beautifyplot as bp

# Set image path / 設定圖片路徑
img_path = __file__[:-len(__file__.split('\\')[-1])]+ "\\img\\"

# Set the default mode / 設定預設模式
bp.default()

# Initialize the plot / 初始化圖表
bp.initplot()

# Plot / 繪圖
bp.plot([1, 2, 3, 4], [1, 2, 2.5, 3], label='bp.plot')

# Scatter / 散佈圖
bp.scatter([1, 2, 3, 4], [1, 1.5, 2, 2.5], label='bp.scatter')

# Set the title / 設定標題
bp.title('DEMO 1: Basic Plot')

# Set labels / 設定標籤
bp.xlabel('X LABEL')
bp.ylabel('Y LABEL')

# Set ticks / 設定刻度
bp.xticks([1, 2, 3, 4])
bp.yticks([1, 2, 3])

# Set spines / 設定脊梁
bp.spines()

# Set grid / 設定格線
bp.grid()

# Add legend / 加上圖例
bp.legend()

# Save the plot / 儲存圖表
bp.savefig(f'{img_path}demo1_BasicPloy.png')

# Close the plot / 關閉圖表
bp.close()