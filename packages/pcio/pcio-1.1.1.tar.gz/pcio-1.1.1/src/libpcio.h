#ifndef __LIBMYPY_H__
#define __LIBMYPY_H__

#include <Python.h>

PyObject * input_int(PyObject *);
PyObject * input_float(PyObject *);
PyObject * input_line(PyObject *);
PyObject * input_word(PyObject *);
PyObject * input_char(PyObject *);
PyObject * input(PyObject *, PyObject *);
PyObject * encoding(PyObject *, PyObject *);
PyObject * print(PyObject *, PyObject *);
PyObject * println(PyObject *, PyObject *);

void pcio_init(void);
#endif
