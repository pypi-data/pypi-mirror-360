cd ../cpp
make
cd ../java
javac -h ./com/buildz/xf/cpp com/buildz/xf/LoaderJNI.java -encoding utf-8
javac com/buildz/xf/Loader.java -encoding utf-8
javac com/buildz/xf/Args.java -encoding utf-8

g++ -I"./com/buildz/xf/cpp" -I"$JAVA_HOME/include" -I"$JAVA_HOME/include/win32" -shared -o ./jxf.dll ./com/buildz/xf/cpp/jxf.cpp -I"../cpp" -L"../cpp" -lcxf -O3

g++ -I"./com/buildz/xf/cpp" -I"%JAVA_HOME%/include" -I"%JAVA_HOME%/include/win32" -shared -o ./jxf.dll ./com/buildz/xf/cpp/jxf.cpp -I"../cpp" -L"../cpp" -lcxf -O3

javac Test.java -encoding utf-8 && java -Djava.library.path=. Test

clean:
    rm ./com/buildz/xf/*.class
    rm *.class

win clean
    del .\com\buildz\xf\*.class
    del *.class