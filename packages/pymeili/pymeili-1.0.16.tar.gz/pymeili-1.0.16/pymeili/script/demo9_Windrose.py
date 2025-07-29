# WINDROSE
from windrose import WindroseAxes
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import numpy as np
import beautifyplot as bp

# Set image path / 設定圖片路徑
img_path = __file__[:-len(__file__.split('\\')[-1])]+ "\\img\\"

# Create wind speed and direction variables / 創建風速和風向變數
ws = np.random.random(500) * 6 # 0-6 m/s
wd = np.random.random(500) * 360 # 0-360°

# Initialize the subplot / 初始化子圖
bp.initplot(WindroseAxes.from_ax(), theme='d')

# plot windrose / 繪製風玫瑰圖
bp.rbox(wd, ws, normed=True, edgecolor='fg', linewidth=2)

# set xticklabels (rticklabels) / 設定x軸標籤
bp.rticklabels(['N', 'NW',  'W', 'SW', 'S', 'SE','E', 'NE'], color='fg')
bp.set_theta_zero_location('N')

# set yticks and yticklabels / 設定y軸標籤
bp.yticks([2, 4, 6, 8, 10, 12, 14], labels=['2', '4', '6', '8', '10', '12', '14'], color='fg')
bp.ylim(0, 12)

# adjust rlables / 調整r標籤
bp.set_rlabel_position(-135)

# set grid / 設定網格
bp.rgrids()

# set spines / 設定脊梁
bp.rspines()

# set title / 設定標題
bp.legend(fontsize=12)

# set xlabel / 設定x軸標籤
bp.xlabel('Wind Direction', color='fg')

# set title / 設定標題
bp.lefttitle('DEMO 9')
bp.righttitle('WINDROSE')

# Save the plot / 儲存圖表
bp.savefig(f'{img_path}demo9_Windrose.png')

# Close the plot / 關閉圖表
bp.close()
