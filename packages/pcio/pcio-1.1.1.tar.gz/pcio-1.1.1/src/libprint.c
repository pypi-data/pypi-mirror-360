#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <Python.h>
#include <wchar.h>
#include "libpcio.h"

static char fmtc=0;
static char fmta=0;
static wchar_t fmtf=L' ';
static char fmts=0;
static int fmtp=0;
static int fmtw=0;
static char float_spec[]="EeGgfF";

static wchar_t *out_buf=NULL;
static size_t out_len=0, out_maxlen=0;
static void outw(wchar_t c)
{ if(out_buf==NULL) {
    pcio_init();
    out_buf=malloc((out_maxlen=65536)*sizeof(wchar_t));
  }
  if(out_len==out_maxlen) {
    out_buf=realloc(out_buf,(out_maxlen*=2)*sizeof(wchar_t));
  }
  out_buf[out_len++]=c;
}

static void print_w(wchar_t *s, size_t len, int isnum) {
  int a=fmta;
  if(a==0) {
    if(isnum) a='>';
    else a='<';
  }
  wchar_t sgn=0;
  int xlen=(int)len;
  if(isnum && fmts=='+' && s[0]!='-') {
    sgn='+';
    ++xlen;
  }
  int la=0,ra=0;
  if(xlen<fmtw) { 
    if(a=='<')
      ra=fmtw-xlen;
    else if(a=='>')
      la=fmtw-xlen;
    else {
      la=(fmtw-xlen+1)/2;
      ra=fmtw-xlen-la;
    }
  }
  while(la-- > 0)
    outw(isnum?fmtf:L' ');
  if(sgn)
    outw(sgn);
  for(size_t j=0;j<len;++j) {
    if(isnum && s[j]==',')
      outw(L'.');
    else
      outw(s[j]);
  }
  while(ra-- > 0)
    outw(L' ');
}
static void print_str(PyObject *o, int isnum) {
   Py_ssize_t str_len=PyUnicode_GET_LENGTH(o);
   if(fmtp>0 && (fmtc=='s' || fmtc==0) && !isnum)
     str_len=fmtp;
   wchar_t *s=calloc(str_len+1,sizeof(wchar_t));
   PyUnicode_AsWideChar(o,s,str_len);
   print_w(s,str_len,isnum);
   free(s);
}
static wchar_t buf[1025];
static void print_0(PyObject *o) {
  int len;
  if(fmtc=='r') {
    PyObject* obj=PyObject_Repr(o);
    if(obj) {
      print_str(obj, 0);
      Py_DECREF(obj);
    }
    return;
  }
  if(PyUnicode_Check(o)) {
    print_str(o, 0);
    return;
  }
  else if(PyLong_Check(o)) {
    if(fmtc && strchr("idoxX",fmtc)) {
      int over;
      long long x=PyLong_AsLongLongAndOverflow(o,&over);
      if(!over) {
        wchar_t fmtstr[]=L"%lli";
        fmtstr[3]=fmtc;
        len=swprintf(buf,1024,fmtstr,x);
        if(len>0)
          print_w(buf,len,1);
      }
      else {
        PyObject* obj=PyObject_Str(o);
        if(obj) {
          print_str(obj,1);
          Py_DECREF(obj);
        }
      }
    }
    else if(fmtp>0 && (fmtc=='f' || fmtc=='F') || fmtc && strchr("EeGg",fmtc) ) {
      double x=PyLong_AsDouble(o);
      if(fmtp>=0) {
        wchar_t fmtstr[]=L"%.*lf";
        fmtstr[4]=fmtc;
        len=swprintf(buf,1024,fmtstr,fmtp,x);
      }
      else {
        wchar_t fmtstr[]=L"%lg";
        fmtstr[2]=fmtc;
        len=swprintf(buf,1024,fmtstr,x);
      }
      if(len>0)
        print_w(buf,len,1);
    }
    else {
      PyObject* obj=PyObject_Str(o);
      if(obj) {
        print_str(obj,1);
        Py_DECREF(obj);
      }
    }
    return;
  }
  else if(PyFloat_Check(o)) {
    double x=PyFloat_AS_DOUBLE(o);
    if(fmtc && strchr(float_spec,fmtc)) {
      if(fmtp>=0) {
        wchar_t fmtstr[]=L"%.*lf";
        fmtstr[4]=fmtc;
        len=swprintf(buf,1024,fmtstr,fmtp,x);
      }
      else if(strchr("EeGg",fmtc)) {
        wchar_t fmtstr[]=L"%lg";
        fmtstr[2]=fmtc;
        len=swprintf(buf,1024,fmtstr,x);
      }
      else {
        wchar_t fmtstr[]=L"%lf";
        fmtstr[2]=fmtc;
        len=swprintf(buf,1024,fmtstr,x);
        while(len>0 && buf[len-1]=='0') --len;
      }
      if(len>0)
        print_w(buf,len,1);
    }
    else if(fmtc && strchr("id",fmtc)) {
      wchar_t fmtstr[]=L"%.0lf";
      len=swprintf(buf,1024,fmtstr,x);
      if(len>0)
        print_w(buf,len,1);
    }
    else {
      PyObject* obj=PyObject_Str(o);
      if(obj) {
        print_str(obj,1);
        Py_DECREF(obj);
      }
    }
    return;
  }
  PyObject *iter = PyObject_GetIter(o);
  if (iter == NULL) {
    PyErr_Clear();
    PyObject* obj=PyObject_Str(o);
    if(obj) {
      print_str(obj,0);
      Py_DECREF(obj);
    }
    return;
  }
  PyObject *item;
  int n=0;
  while((item = PyIter_Next(iter))) {
    if(n++ >0)
      outw(L' ');
    print_0(item);
    Py_DECREF(item);
  }
  Py_DECREF(iter);
}
#define nextc()  ++j;c=(j<fmt_len)?PyUnicode_READ(fmt_kind,fmt,j):0
static int pcio_ln=0;
PyObject* print(PyObject *self, PyObject *args) {
    Py_ssize_t argc=0;
    if(PyTuple_Check(args))
       argc=PyTuple_GET_SIZE(args);
    if(argc==0) Py_RETURN_NONE;
    Py_ssize_t n=1;
    PyObject *obj = PyTuple_GET_ITEM(args, 0);
    if(PyUnicode_Check(obj)) { 
      Py_ssize_t fmt_len=PyUnicode_GET_LENGTH(obj);
      int fmt_kind=PyUnicode_KIND(obj);
      void *fmt=PyUnicode_DATA(obj);
      if(argc==1) {
        for(Py_ssize_t j=0;j<fmt_len;++j) {
          outw(PyUnicode_READ(fmt_kind,fmt,j));
        }
      }
      else {
         for(int j=0;j<fmt_len;++j) {
           Py_UCS4 c=PyUnicode_READ(fmt_kind,fmt,j);
           if(c=='{') {
             nextc();
             if(c=='{')
               outw('{');
             else {
               Py_ssize_t id;
               if(c>='0' && c<='9') {
                 id=0;
                 while(c>='0' && c<='9') {
                   id=id*10+(c-'0');
                   nextc();
                 }
                 id+=1;
               }
               else
                id=n++;
               fmtc=0;
               fmtw=0;
               fmtp=-1;
               fmta=0;
               fmtf=L' ';
               fmts=0;
               if(c==':') { 
                 nextc();
                 int minus=0;
                 if(c && strchr("<>=^",c)) {
                   fmta=c;
                   nextc();
                 }
                 if(c && strchr("+-",c)) {
                   fmts=c;
                   nextc();
                 }
                 if(c=='0') fmtf=L'0';
                 while(c>='0' && c<='9') {
                   fmtw=fmtw*10+(c-'0');
                   nextc();
                 }
                 if(fmtw>10000 || fmtw<0) fmtw=0;
                 if(c=='.') {
                   fmtp=0;
                   nextc();
                   while(c>='0' && c<='9') {
                     fmtp=fmtp*10+(c-'0');
                     nextc();
                   }
                   if(fmtp<0) fmtp=6;
                   if(fmtp>1000) fmtp=1000;
                 }
                 if(c=='}') ;
                 else if(c && strchr("sidoxXeEgGfF",c)) {
                   fmtc=c;
                   nextc();
                 }
                 else {
                   PyErr_SetString(PyExc_ValueError,"Wrong format specifier");
                   return NULL;
                 }
               }
               else if(c=='!') {
                 nextc();
                 if(c && !strchr("asr",c)) {
                   PyErr_SetString(PyExc_ValueError,"Wrong format specifier");
                   return NULL;
                 }
                 fmtc='r';
                 nextc();
               }
               if(c!='}') {
                 PyErr_SetString(PyExc_ValueError,"Wrong format specifier");
                 return NULL;
               }
               if(id<argc) {
                 print_0(PyTuple_GET_ITEM(args, id));
               }
               else {
                 PyErr_SetString(PyExc_ValueError,"Argument not exists");
                 return NULL;
               }
             }
           }
           else if(c=='}') {
             nextc();
             if(c=='}')
               outw(L'}');
           }
           else 
             outw(c);
         }
       }
       if(pcio_ln)
         outw(L'\n');
    }
    else {
      fmtc=0;
      fmtw=0;
      fmtp=-1;
      fmta=0;
      fmtf=0;
      fmts=0;
      for(n=0;n<argc;++n) {
        if(n>0) outw(L' ');
        print_0(PyTuple_GET_ITEM(args, n));
      }
      if(pcio_ln)
        outw(L'\n');
    }
    PyObject *str=PyUnicode_FromWideChar(out_buf, out_len);
    out_len=0;
    PyObject *write = PyObject_GetAttrString(PySys_GetObject("stdout"), "write");
    PyObject *res=NULL;
    if(write) {
       res=PyObject_CallOneArg(write, str);
       Py_DECREF(write);
    } 
    Py_DECREF(str);
    return res;
}
PyObject* println(PyObject *self, PyObject *args) {
  pcio_ln=1;
  PyObject *res=print(self,args);
  pcio_ln=0;
  return res;
}
