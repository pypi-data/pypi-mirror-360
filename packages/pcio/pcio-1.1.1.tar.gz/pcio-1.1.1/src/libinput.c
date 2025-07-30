#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <math.h>
#include <locale.h>
#include <wchar.h>
#include <Python.h>
#include "libpcio.h"

static PyObject *rec_arg=NULL;
static PyObject *rec_kw=NULL;
void pcio_init(void) {
  if(rec_kw==NULL)
    encoding(NULL,NULL);
}
PyObject * encoding(PyObject* self, PyObject* args) {
  if(rec_arg==NULL) {
    rec_arg=PyTuple_New(0);
    rec_kw=PyDict_New();
    PyDict_SetItemString(rec_kw, "errors", PyUnicode_FromString("replace"));
  }
  Py_ssize_t argc=0;
  if(args && PyTuple_Check(args))
    argc=PyTuple_GET_SIZE(args);
  if(argc==1) {
    PyDict_SetItemString(rec_kw, "encoding", PyTuple_GET_ITEM(args, 0));
  }
  PyObject* reconfigure=PyObject_GetAttrString(PySys_GetObject("stdin"), "reconfigure");
  PyObject* res=NULL;
  if(reconfigure) {
    res=PyObject_Call(reconfigure, rec_arg, rec_kw);
    Py_DECREF(reconfigure);
  }
  if(res==NULL) return NULL;
  Py_DECREF(res);
  reconfigure=PyObject_GetAttrString(PySys_GetObject("stdout"), "reconfigure");
  if(reconfigure) {
    res=PyObject_Call(reconfigure, rec_arg, rec_kw);
    Py_DECREF(reconfigure);
  }
  return res;
}
static wchar_t *in_buf=NULL;
static size_t in_len=0,in_maxlen=0,in_pos=0;
static int in_eof=0;
static inline int is_eof(void) {
  return in_eof && in_pos>=in_len;
}
static void getline(void) {
  if(in_buf==NULL) {
    pcio_init();
    in_buf=malloc(((in_maxlen=65536)+1)*sizeof(wchar_t));
    in_pos=in_len=0;
  }
  PyObject* readline=PyObject_GetAttrString(PySys_GetObject("stdin"), "readline");
  if(in_pos>=in_len) {
    in_pos=in_len=0;
  }
  PyObject* res=NULL;
  if(readline) {
    res=PyObject_CallNoArgs(readline);
    if(res && PyUnicode_Check(res)) {
      Py_ssize_t len=PyUnicode_GetLength(res);
      if(len==0) 
        in_eof=1;
      else {
        while(in_maxlen<in_len+len) 
          in_maxlen*=2;
        in_buf=realloc(in_buf,(in_maxlen+1)*sizeof(wchar_t));
        PyUnicode_AsWideChar(res,in_buf+in_len,len);
        in_len+=len;
        in_buf[in_len]=0;
      }
    }
    else
      in_eof=1;
    Py_DECREF(readline);
  }
}
static void skipws(void) {
  if(!in_buf) 
    getline();
  while(!is_eof()) {
    while(in_pos<in_len && in_buf[in_pos]<=' ')
      ++in_pos;
    if(in_pos<in_len) return;
    getline();
  }
}
PyObject* input_int(PyObject * self) {
  skipws();
  if(is_eof()) {
    PyErr_SetNone(PyExc_EOFError);
    return NULL;
  }
  int minus=0,k=0;

  size_t start=in_pos;
  if(in_buf[in_pos]=='-') {
    minus=1;
    ++in_pos;
  }
  long long x=0;
  wchar_t c;
  while((c=in_buf[in_pos])>='0' && c<='9') { 
    x=x*10+(c-'0');
    ++k;
    ++in_pos;
  }
  if(k==0) {
    if(minus) --in_pos;
    PyErr_SetString(PyExc_ValueError,"Not a integer number");
    return NULL;
  }
  else if(k<19)
    return PyLong_FromLongLong(minus?-x:x);
  else {
    char *buf=malloc(in_pos-start+1);
    char *end;
    for(size_t j=start;j<in_pos;++j)
      buf[j-start]=(char)in_buf[in_pos];
    buf[in_pos-start]='\0';
    PyObject* obj=PyLong_FromString(buf,&end,10);
    free(buf);
    return obj;
  }
}
PyObject* input_float(PyObject * self) {
  skipws();
  if(is_eof()) {
    PyErr_SetNone(PyExc_EOFError);
    return NULL;
  }
  wchar_t *end;
  double x=wcstod(in_buf+in_pos,&end);
  if(in_buf+in_pos==end) {
    PyErr_SetString(PyExc_ValueError,"Not a float number");
    return NULL;
  }
  else { 
    in_pos=end-in_buf;
    return PyFloat_FromDouble(x);
  }
}
static PyObject* input_0(int mode)
{
  if(mode=='w') skipws();
  else if(!in_buf || !in_eof && in_pos>=in_len) getline();
  if(is_eof()) {
    PyErr_SetNone(PyExc_EOFError);
    return NULL;
  }
  if(mode=='a') {
    while(!in_eof)
      getline();
  }
  size_t len=in_len-in_pos;
  if(mode=='a' || mode=='L')
    ;
  else if(mode=='l') {
    if(in_buf[in_pos+len-1]=='\n') {
      --in_len;
      --len;
    }
  }
  else if(mode=='c') {
    len=1;
  }
  else { // mode=='w'
    for(len=0;in_pos+len<in_len && in_buf[in_pos+len]<=' ';++len)
      ;
  }
  PyObject* ret = PyUnicode_FromWideChar(in_buf+in_pos,len);
  in_pos+=len;
  return ret;
}
PyObject* input_line(PyObject * self) {
  return input_0('l');
}
PyObject* input_word(PyObject * self) {
  return input_0('w');
}
PyObject* input_char(PyObject * self) {
  return input_0('c');
}

static PyObject* input_1(int mode) {
  if(mode=='f')
    return input_float(NULL);
  else if(mode=='i')
    return input_int(NULL);
  else
    return input_0(mode);
}
static PyObject* input_2(int fmt_kind, Py_ssize_t fmt_len, void *fmt, int fmt_c) {
   PyObject* ret;
   if(fmt_c>1) {
     ret=PyTuple_New(fmt_c);
   }
   else if(fmt_c==0) {
      Py_RETURN_NONE;
   }
   int k=0;
   for(Py_ssize_t j=0;j<fmt_len;++j) {
     unsigned char mode=PyUnicode_READ(fmt_kind,fmt,j);
     if(strchr("cifwlLa",mode)) {
       PyObject* obj=input_1(mode);
       if(fmt_c==1)
         return obj;
       PyTuple_SET_ITEM(ret, k++, obj);
     }
   }    
   return ret;
}

PyObject * input(PyObject *self, PyObject *args) {
    PyObject * ret;
    Py_ssize_t argc=0;
    if(PyTuple_Check(args))
       argc=PyTuple_GET_SIZE(args);
    long count_c=-1;
    int fmt_c=1;
    int fmt_kind=-1;
    int fmt_mode='l';
    Py_ssize_t fmt_len=0;
    void *fmt=NULL;
    if(argc>0) {
      int n=0;
      PyObject *obj = PyTuple_GET_ITEM(args, 0);
      if(PyLong_Check(obj)) {
        count_c=PyLong_AsLong(obj);
        if(count_c<0) count_c=0;
        n++;
      }
      if(n<argc) {
         obj = PyTuple_GET_ITEM(args, n);
         if(PyUnicode_Check(obj)) {
           fmt_kind=PyUnicode_KIND(obj);
           fmt=PyUnicode_DATA(obj);
           fmt_len=PyUnicode_GET_LENGTH(obj);
           fmt_c=0;
           for(Py_ssize_t j=0;j<fmt_len;++j) {
             unsigned char mode=PyUnicode_READ(fmt_kind,fmt,j);
             if(strchr("cifwlLa",mode))
             { fmt_mode=mode;
               fmt_c++;
             }
           }
	 }
      }
      else if(n>0) {
        fmt_mode='c';
        fmt_c=1;
      }
    }
    if(count_c>=0 && fmt_c==1 && fmt_mode=='c') {
       if(!in_buf || !in_eof && in_pos>=in_len) getline();
       if(is_eof()) {
         PyErr_SetNone(PyExc_EOFError);
         return NULL;
       }
       while(in_len-in_pos<count_c && !in_eof) {
         getline();
       }
       size_t len=count_c;
       if(len>in_len-in_pos) len=in_len-in_pos;
       PyObject *ret = PyUnicode_FromWideChar(in_buf+in_pos,len);
       in_pos+=len;
       return ret;
    }
    if(count_c>=0)
      ret=PyList_New(count_c);
    for(int i=0;i<count_c || count_c==-1;++i) {
      PyObject *obj;
      if(fmt_c==1)
        obj=input_1(fmt_mode);
      else
        obj=input_2(fmt_kind,fmt_len, fmt,fmt_c);
      if(count_c==-1)
         return obj;
      PyList_SET_ITEM(ret,i,obj);
    }
    return ret;
}
