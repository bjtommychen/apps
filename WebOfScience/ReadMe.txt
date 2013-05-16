这个没有成功. 因为第二天, 当suds都安装成功后, 发现wos.py访问的isiknowledge.com需要用户验证. 


Web of Science API access with ruby, python and php libs

https://gist.github.com/domoritz/2012629

http://stackoverflow.com/questions/15397225/accessing-isi-web-of-science-through-soap

https://fedorahosted.org/suds/wiki/Documentation



	1. install 'python2.7.4 for windows',  http://www.python.org/download/releases/2.7.4/
	2. install setuptools.  https://pypi.python.org/pypi/setuptools#files
	3. get python-suds-0.4.tar.gz,  https://fedorahosted.org/suds/
	4. unzip, and 'python setup.py install'
	5. 需要手动将suds解压包中的dist, suds,suds.egg-info三个文件夹复制到Python的安装路径\Lib\site-packages下
	6. >>> from suds.client import Client 

