# Import the module / 引入套件
import beautifyplot as bp
from matplotlib import pyplot as plt
import numpy as np
import cartopy.crs as ccrs

# Set image path / 設定圖片路徑
img_path = __file__[:-len(__file__.split('\\')[-1])]+ "\\img\\"

# Set the default mode / 設定預設模式
bp.default()

# Define sample data / 定義資料
def sample_data(shape=(37, 73)):
    """Return ``lons``, ``lats`` and ``data`` of some fake data."""
    import numpy as np

    nlats, nlons = shape
    lats = np.linspace(-np.pi / 2, np.pi / 2, nlats)
    lons = np.linspace(-np.pi, np.pi, nlons)
    lons, lats = np.meshgrid(lons, lats)
    wave = 0.75 * (np.sin(2 * lats) ** 8) * np.cos(4 * lons)
    mean = 0.5 * np.cos(2 * lats) * ((np.sin(2 * lats)) ** 2 + 2)

    lats = np.rad2deg(lats)
    lons = np.rad2deg(lons)
    data = wave + mean

    return lons, lats, data

# Set the data / 設定資料
lons, lats, data = sample_data()

# Set the extent / 設定範圍
xmin, xmax, ymin, ymax = 30, 150, 0, 60

# Initialize the subplot1 / 初始化子圖一 : Basemap(投影方式為「cyl」，解析度為「c」，中心經度為0)；縮放範圍
ax1 = bp.initplot(bp.subplot(221), figsize=(16, 8), theme='l')
map1= bp.basemap(ax=ax1, projection='cyl', resolution='c', lon_0=0, llcrnrlon=xmin, llcrnrlat=ymin, urcrnrlon=xmax, urcrnrlat=ymax)
map = bp.initplot(map1, figsize=(16, 8), theme='l')
bp.drawcoastlines(zorder=12)
bp.drawcountries(zorder=12)
bp.drawmeridians(np.arange(-180, 181, 60), labelsize=10)
bp.drawparallels(np.arange(-90, 91, 30), labelsize=10)
bp.drawmapboundary(linewidth=3)

# Plot / 繪圖
X, Y = map(lons, lats)
bp.contourf(x=X, y=Y, z=data, cmap='49', levels=np.linspace(-1.1, 1.1, 26))
bp.colorbar(ax=ax1, label='', ticks=[-1,-0.5,0,0.5,1])
bp.scatter(x=X[np.abs(data)>0.9], y=Y[np.abs(data)>0.9], color='fg', s=0.1, zorder=12, alpha=0.6)

# title / 標題
bp.lefttitle('DEMO 7-1', ax=ax1)
bp.righttitle('Basemap(cyl)', ax=ax1)

# Initialize the subplot2 / 初始化子圖二 : Cartopy(投影方式為「PlateCarree」)
ax2 = bp.initplot(bp.subplot(222, projection=ccrs.PlateCarree()), figsize=(16, 8), theme='l')
bp.coastlines(zorder=12)
bp.countries(zorder=12)
bp.gridlines(labelsize=10, zorder=12)

# Plot / 繪圖
X, Y = np.meshgrid(np.linspace(-180, 180, 73), np.linspace(-90, 90, 37))
bp.contourf(x=lons, y=lats, z=data, cmap='49', transform=ccrs.PlateCarree(), levels=np.linspace(-1.1, 1.1, 26),zorder=10)
bp.colorbar(label='', ticks=[-1,-0.5,0,0.5,1])
bp.scatter(x=X[np.abs(data)>0.9], y=Y[np.abs(data)>0.9], transform=ccrs.PlateCarree(), color='fg', s=0.1, zorder=12, alpha=0.6)
bp.set_extent([xmin, xmax, ymin, ymax], crs=ccrs.PlateCarree())
bp.add_mapboundary(linewidth=3, zorder=12)

# Zoom in / 縮放範圍
bp.set_extent([xmin, xmax, ymin, ymax], crs=ccrs.PlateCarree())
bp.add_mapboundary(linewidth=3, zorder=12)

# title / 標題
bp.lefttitle('DEMO 7-2')
bp.righttitle('Cartopy(PlateCarree)')

# Initialize the subplot3 / 初始化子圖三 : Basemap(投影方式為「robin」，中心經度為0)
ax3 = bp.initplot(bp.subplot(223), figsize=(16, 8), theme='l')
map3= bp.basemap(ax=ax3, projection='robin', lon_0 = 0)
map = bp.initplot(map3, figsize=(16, 8), theme='l')
bp.drawcoastlines()
bp.drawcountries()
bp.drawmeridians(np.arange( 0,360, 60), labelsize=10)
bp.drawparallels(np.arange(-90,120, 30), labelsize=10)
bp.drawmapboundary(linewidth=3)

# Plot / 繪圖
X, Y = map(lons, lats)
bp.contourf(x=X, y=Y, z=data, cmap='49', levels=np.linspace(-1.1, 1.1, 26))
bp.colorbar(ax=ax3, label='', ticks=[-1,-0.5,0,0.5,1])
bp.scatter(x=X[np.abs(data)>0.9], y=Y[np.abs(data)>0.9], color='fg', s=0.1, zorder=12, alpha=0.6)

# title / 標題
bp.lefttitle('DEMO 7-3', ax=ax3)
bp.righttitle('Basemap(robin)', ax=ax3)

# Initialize the subplot4 / 初始化子圖四 : Cartopy(投影方式為「Robinson」)
ax4 = bp.initplot(bp.subplot(224, projection=ccrs.Robinson()), figsize=(16, 8), theme='l')
ax4 = bp.initplot(bp.subplot(224, projection=ccrs.Robinson()), figsize=(16, 8), theme='l')
bp.coastlines(zorder=12)
bp.countries(zorder=12)
bp.gridlines(labelsize=10, zorder=12)

# Plot / 繪圖
X, Y = np.meshgrid(np.linspace(-180, 180, 73), np.linspace(-90, 90, 37))
bp.contourf(x=lons, y=lats, z=data, cmap='49', transform=ccrs.PlateCarree(), levels=np.linspace(-1.1, 1.1, 26),zorder=10)
bp.colorbar(label='', ticks=[-1,-0.5,0,0.5,1])
bp.scatter(x=X[np.abs(data)>0.9], y=Y[np.abs(data)>0.9], transform=ccrs.PlateCarree(), color='fg', s=0.1, zorder=12, alpha=0.6, label='data>0.9 or data<-0.9')
bp.legend(zorder=13, fontsize=15)

# title / 標題
bp.lefttitle('DEMO 7-4')
bp.righttitle('Cartopy(Robinson)')

# suptitle / 主標題
bp.title('Basemap vs. Cartopy in pymeili')

# Save the figure / 儲存圖片
bp.tight_layout(pad=2)
bp.savefig(img_path + 'demo7_BasemapVSCartopy.png')

# Close the plot / 關閉圖表
bp.close()

# Show the record Table / 顯示圖表輸出列表
bp.record()