# Import the module / 引入套件
import beautifyplot as bp
import numpy as np

# Set image path / 設定圖片路徑
img_path = __file__[:-len(__file__.split('\\')[-1])]+ "\\img\\"

# Set data / 設定資料
X_data = np.arange(-180, 180, 1)
Y_data = np.arange(-90, 90, 1)
X_data, Y_data = np.meshgrid(X_data, Y_data)
Z_data = np.sin(np.radians(X_data)) + np.cos(np.radians(Y_data))


# Set the default mode / 設定預設模式
bp.default()

# Set the linewidth / 設定線寬
bp.Linewidth().change(2)

# Initialize the subplot1 / 初始化子圖一 : 地圖投影方式為「cyl」，解析度為「c」，中心經度為0
ax1 = bp.initplot(bp.subplot(221), figsize=(10, 5), theme='l')
map1= bp.basemap(ax=ax1, projection='cyl', resolution='c', lon_0=0)
map = bp.initplot(map1, figsize=(10, 5), theme='l')
X, Y = map(X_data, Y_data)
bp.drawcoastlines()
bp.drawcountries()
bp.drawmapboundary()
bp.contourf(x=X, y=Y, z=Z_data, levels=np.linspace(-2, 2, 19), cmap='49')
bp.colorbar(ax=ax1, label='Z', ticks=[-2,-1,0,1,2])

# title / 標題
bp.setax(ax1)
bp.lefttitle('DEMO 6-1')
bp.righttitle('cyl')

# Initialize the subplot2 / 初始化子圖二 : 地圖投影方式為「robin」，中心經度為0
ax2 = bp.initplot(bp.subplot(222), figsize=(10, 5), theme='l')
map2= bp.basemap(ax=ax2, projection='robin', lon_0 = 0)
map = bp.initplot(map2, figsize=(10, 5), theme='l')
X, Y = map(X_data, Y_data)
bp.drawcoastlines()
bp.drawcountries()
bp.drawmapboundary()
bp.contourf(x=X, y=Y, z=Z_data, levels=np.linspace(-2, 2, 19), cmap='49')
bp.colorbar(ax=ax2, label='Z', ticks=[-2,-1,0,1,2])

# title / 標題
bp.setax(ax2)
bp.lefttitle('DEMO 6-2')
bp.righttitle('robin')

# Initialize the subplot3 / 初始化子圖三 : 地圖投影方式為「aeqd」，中心經度為0, 中心緯度為90
ax3 = bp.initplot(bp.subplot(223), figsize=(10, 5), theme='l')
map3= bp.basemap(ax=ax3, projection='aeqd', lon_0 = 0, lat_0 = 90, width=20000000, height=10000000)
map = bp.initplot(map3, figsize=(10, 5), theme='l')
X, Y = map(X_data, Y_data)
bp.drawcoastlines()
bp.drawcountries()
bp.drawmapboundary()
bp.contourf(x=X, y=Y, z=Z_data, levels=np.linspace(-2, 2, 19), cmap='49', hatches=['-', '/', '\\', '//'])
bp.colorbar(ax=ax3, label='Z', ticks=[-2,-1,0,1,2])

# title / 標題
bp.setax(ax3)
bp.lefttitle('DEMO 6-3')
bp.righttitle('aeqd')

# Initialize the subplot4 / 初始化子圖四 : 地圖投影方式為「moll」，中心經度為0
ax4 = bp.initplot(bp.subplot(224), figsize=(10, 5), theme='l')
map4= bp.basemap(ax=ax4, projection='moll', lon_0 = 0)
map = bp.initplot(map4, figsize=(10, 5), theme='l')
X, Y = map(X_data, Y_data)
bp.drawcoastlines()
bp.drawcountries()
bp.drawmapboundary()
bp.contourf(x=X, y=Y, z=Z_data, levels=np.linspace(-2, 2, 19), cmap='49', hatches=['-', '/', '\\', '//'])
bp.colorbar(ax=ax4, label='Z', ticks=[-2,-1,0,1,2])


# title / 標題
bp.setax(ax4)
bp.lefttitle('DEMO 6-4')
bp.righttitle('moll')

# Save the plot / 儲存圖表
bp.savefig(f'{img_path}demo6_Basemap.png')

# Close the plot / 關閉圖表
bp.close()

