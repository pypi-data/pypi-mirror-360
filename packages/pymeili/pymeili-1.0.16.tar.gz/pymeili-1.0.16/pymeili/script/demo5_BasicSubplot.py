# Import the module / 引入套件
import beautifyplot as bp
import numpy as np

# Set image path / 設定圖片路徑
img_path = __file__[:-len(__file__.split('\\')[-1])]+ "\\img\\"

# Set the default mode / 設定預設模式
bp.default()

# Initialize the subplot1 / 初始化子圖一
bp.initplot(bp.subplot(1, 3, 1), figsize=(15, 5), theme='l')

# Plot / 繪圖
x1 = np.linspace(0, 6*np.pi, 100)
y1 = np.sin(x1)
bp.plot(x1, y1)

# Set the title / 設定標題
bp.lefttitle('DEMO 5-1')
bp.righttitle('sin(x)')

# Set ticks / 設定刻度
bp.xticks([0, np.pi, 2*np.pi, 3*np.pi, 4*np.pi, 5*np.pi, 6*np.pi], ['0', 'π', '2π', '3π', '4π', '5π', '6π'])
bp.yticks([-2, -1, 0, 1, 2])

# Set spines / 設定脊梁
bp.spines()

# Set grid / 設定格線
bp.grid()

# Initialize the subplot2 / 初始化子圖二
bp.initplot(bp.subplot(1, 3, 2), theme='l')

# Plot / 繪圖
x2 = np.linspace(0, 6*np.pi, 100)
y2 = np.cos(x2)
bp.plot(x2, y2)

# Set the title / 設定標題
bp.lefttitle('DEMO 5-2')
bp.righttitle('cos(x)')

# Set ticks / 設定刻度
bp.xticks([0, np.pi, 2*np.pi, 3*np.pi, 4*np.pi, 5*np.pi, 6*np.pi], ['0', 'π', '2π', '3π', '4π', '5π', '6π'])
bp.yticks([-2, -1, 0, 1, 2])

# Set spines / 設定脊梁
bp.spines()

# Set grid / 設定格線
bp.grid()

# Initialize the subplot3 / 初始化子圖三
bp.initplot(bp.subplot(1, 3, 3), theme='l')

# Plot / 繪圖
x3 = np.linspace(0, 6*np.pi, 100)
y3 = np.tan(x3)
bp.plot(x3, y3)

# Set the title / 設定標題
bp.lefttitle('DEMO 5-3')
bp.righttitle('tan(x)')

# Set ticks / 設定刻度
bp.xticks([0, np.pi, 2*np.pi, 3*np.pi, 4*np.pi, 5*np.pi, 6*np.pi], ['0', 'π', '2π', '3π', '4π', '5π', '6π'])
bp.yticks([-2, -1, 0, 1, 2])

# Set spines / 設定脊梁
bp.spines()

# Set grid / 設定格線
bp.grid()

# Set ylimit / 設定 y 軸範圍
bp.ylim(-2, 2)

# Save the plot / 儲存圖表
bp.savefig(f'{img_path}demo5_BasicSubplot.png')

# Close the plot / 關閉圖表
bp.close()