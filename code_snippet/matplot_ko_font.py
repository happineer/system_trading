import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import font_manager as fm
from matplotlib import rc

print('버전: ', mpl.__version__)
print('설치위치: ', mpl.__file__)
print('설정위치: ', mpl.get_configdir())
print('캐시위치: ', mpl.get_cachedir())
print('설정파일위치: ', mpl.matplotlib_fname())

print("#설정되어 있는 폰트사이즈")
print(plt.rcParams["font.size"])

print("#설정되어 있는 폰트글꼴")
print(plt.rcParams["font.family"])
font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')

path = 'c:/Windows/Fonts/D2Coding-Ver1.3-20171129.ttc'
# path = 'c:/Windows/Fonts/NanumGothic.ttf'
font_name = fm.FontProperties(fname=path, size=20).get_name()
print(font_name)
plt.rc('font', family=font_name)

# 그래프에서 마이너스 폰트 깨지는 문제에 대한 대처
mpl.rcParams['axes.unicode_minus'] = False

path = 'c:/Windows/Fonts/D2Coding-Ver1.3-20171129.ttc'
font_name = fm.FontProperties(fname=path).get_name()
plt.rcParams["font.family"] = font_name
plt.rcParams["font.size"] = 10
plt.rcParams["figure.figsize"] = (20, 15)