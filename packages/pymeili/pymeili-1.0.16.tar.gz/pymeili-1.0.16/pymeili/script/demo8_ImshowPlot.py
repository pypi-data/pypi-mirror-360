# Import the module / 引入套件
import beautifyplot as bp
import numpy as np

# Set image path / 設定圖片路徑
img_path = __file__[:-len(__file__.split('\\')[-1])]+ "\\img\\"

# Set data / 設定資料
X_data = np.arange(-500, 500, 10)
Y_data = np.arange(-500, 500, 10)
X_data, Y_data = np.meshgrid(X_data, Y_data)
Z_data = np.sin(np.radians(X_data)) + np.cos(np.radians(Y_data))

# Read image / 讀取圖片
demo_3 = bp.imread(filename = f'{img_path}demo3_ContourPlot.png')

# Add noise / 添加雜訊
R_noise = np.random.normal(0, 0.3, demo_3.shape)
G_noise = np.random.normal(0, 0.3, demo_3.shape)
B_noise = np.random.normal(0, 0.3, demo_3.shape)
demo_3[:,:,0] += R_noise[:,:,0]
demo_3[:,:,1] += G_noise[:,:,1]
demo_3[:,:,2] += B_noise[:,:,2]

# Set the gray colorbar / 設定灰階色階
gray_cmap = ['#EEEEEE','#222222', '#EEEEEE']

# Set the default mode / 設定預設模式
bp.default()

# Initialize the subplot1 / 初始化子圖一 : imshow 設定資料Z_data
bp.initplot(bp.subplot(221), figsize=(13, 10), theme='l')
bp.imshow(Z_data, cmap=gray_cmap, vmin=-2, vmax=2)
bp.colorbar(label='Z', ticks=[-2,-1,0,1,2])

# title / 標題
bp.lefttitle('DEMO 8-1')
bp.righttitle('imshow')

# Initialize the subplot2 / 初始化子圖二 : imshow 設定資料demo_3
bp.initplot(bp.subplot(222), figsize=(13, 10))
bp.imshow(demo_3)

# title / 標題
bp.lefttitle('DEMO 8-2')
bp.righttitle('imshow')

# Save the plot / 儲存圖表
bp.savefig(f'{img_path}demo8_ImshowPlot.png')

# Close the plot / 關閉圖表
bp.close()


