import sys
import os
import platform

module_path = r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\ﾏｽﾀ\sql_python_module'
if platform.system() == 'Linux':
    module_path = r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'

sys.path.append(os.path.abspath(module_path))

from control import Control

def main():
    control = Control()
    control.start()
    
    

if __name__ == '__main__':
    main()
