# Import the module / 引入套件
import beautifyplot as bp
import numpy as np

# Set image path / 設定圖片路徑
img_path = __file__[:-len(__file__.split('\\')[-1])]+ "\\img\\"

# Create data / 建立資料
x, y = np.meshgrid(np.linspace(-2, 2, 100), np.linspace(-2, 2, 100))
z = np.sin(x**2+y**2) + np.random.normal(0, 0.1, (100, 100))

# Set the default mode / 設定預設模式
bp.default()

# Initialize the plot / 初始化圖表
bp.initplot()

# Contourf / 等高線填滿圖
bp.contourf(x=x, y=y, z=z, levels=np.linspace(-1, 1, 20), cmap='149', extend='both')

# Colorbar / 色條
bp.colorbar(label='COLORBAR OF Z', ticks=[-1, -0.5, 0, 0.5, 1], extendrect=False, extendfrac='auto')

# Contour / 等高線圖
bp.contour(x=x, y=y, z=z, levels=0, colors='fg')

# Textbox / 文字框
bp.textbox(-1.1, 0, 'z = sin(x^2+y^2)', fontsize=20, color='fg')

# Set the title / 設定標題
bp.lefttitle('DEMO 3')
bp.righttitle('Contour Plot')

# Set labels / 設定標籤
bp.xlabel('X LABEL')
bp.ylabel('Y LABEL')

# Set ticks / 設定刻度
bp.xticks([-2, -1, 0, 1, 2])
bp.yticks([-2, -1, 0, 1, 2])

# Set spines / 設定脊梁
bp.spines()

# Set grid / 設定格線
bp.grid()

# Save the plot / 儲存圖表
bp.savefig(f'{img_path}demo3_ContourPlot.png')

# Close the plot / 關閉圖表
bp.close()
