# /bin/zsh

rm -rf x_obfuscate
cp -r someip_py x_obfuscate
pip install python-minifier
for i in `find x_obfuscate -name "*.py"`;do if [ ! `echo $i|grep "service_interface"` ];then pyminify $i >> $i.old;rm -rf $i;mv $i.old $i;fi;done
