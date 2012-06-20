
#ifndef __ARM_EABI__
#define ARCH_ARM 1
#define ARCH_X86 0
#else
#define ARCH_ARM 0
#define ARCH_X86 1
#endif


#if ARCH_X86
#include<iostream>
#include<fstream>
using namespace std;
#endif


#if ARCH_ARM
#include <iostream>
using namespace std;
#include <jni.h>
#include <string.h>

#define LOG_TAG "CPP_TEST"
#define DEBUG 0
#include <android/log.h>
#if DEBUG
#  define  D(x...)  __android_log_print(ANDROID_LOG_DEBUG,LOG_TAG,x)
#else
#  define  D(...)  do {} while (0)
#endif

#if 1
#  define  I(x...)  __android_log_print(ANDROID_LOG_INFO,LOG_TAG,x)
#else
#  define  I(...)  do {} while (0)
#endif
#endif

int main( int argc, char *argv[ ] )
{
    cout<<"argc is "<<argc<<endl;

    ifstream fin;        //
    ofstream fout;
    fin.open("hello.cpp", ios::binary);
    fout.open("hello_out.cpp", ios::out | ios::binary); ////iso:app

    if (!fin.is_open() || !fout.is_open())
    {
        cout<<"open file failed."<<endl;
        return 1;
    }
    cout<<"file opened."<<endl;
    cout<<"last para is "<<argv[argc-1]<<endl;

#if 1
    long begin, end;
    begin = fin.tellg();
    fin.seekg (0, ios::end);
    end = fin.tellg();
    fin.seekg (0, ios::beg);
    cout << "fin size is: 0x" << hex << (end-begin) << " bytes.\n";
    cout << "fin size is: " << dec <<(end-begin) << " bytes.\n";
#endif

#if 0
    char c;
    int r;
    while(fin.get(c))         //
    {
        cout<<"get"<<r<<endl;
        //fin.get(c);
        fout<<c;
    }
#endif

#if 0
    //Tommy: this way, all 'tab' will be removed.
    string out_text;

    while (fin.good())
    {
        fin >> out_text; //将读取的内容存储到变量out_text中
        fout <<  out_text <<  endl;
    }
#endif

#if 1
    int r;
	#define READLEN 	100
    //Tommy: this way, all 'tab' will be removed.
    //char array[10];
    char *array;

	array = new char[100];
    while (fin.good())
    {
        fin.read(array, 100);//sizeof(array));
		r = fin.gcount();
        cout<<"read "<<r<<endl;
        fout.write(array, r);
    }
	delete []array;

#endif

    cout<<"copy done."<<endl;
    fin.close();//
    fout.close();

    return 0;
}

