#include "libpcio.h"

char input_docs[] = "Formatted input function. As the input argument, you can specify a number (the number of input characters) or a format (a non-empty sequence of characters: 'l' - input of a line without a newline character, 'L' - input of a line including a newline character, 'i' - input an integer number, 'f' - input a float number, 'w' - input a word up to whitespace characters, 'c' - input a symbol, 'a' - input all text up to the end of the file). To input an array, the first argument must be the number of array elements, and the second argument must be the format. When called without arguments, an argument 'l' is used.";
char inputint_docs[] = "Input an integer number.";
char inputfloat_docs[] = "Input a float number.";
char inputline_docs[] = "Input a line as string.";
char inputword_docs[] = "Input a word.";
char inputchar_docs[] = "Input a symbol.";
char encoding_docs[] = "Default encoding: 'utf-8' or 'cp1251'.";
char print_docs[] = "Print arguments by format.";
char println_docs[] = "Print arguments by format and new line.";


PyMethodDef pcio_funcs[] = {
	{"input_int",(PyCFunction)input_int,METH_NOARGS,inputint_docs},
	{"input_float",	(PyCFunction)input_float,METH_NOARGS,inputfloat_docs},
	{"input_line",	(PyCFunction)input_line,METH_NOARGS,inputline_docs},
	{"input_word",	(PyCFunction)input_word,METH_NOARGS,inputword_docs},
	{"input_char",	(PyCFunction)input_char,METH_NOARGS,inputchar_docs},
	{"input",input,	METH_VARARGS,	input_docs},
	{"print",print,	METH_VARARGS,	print_docs},
	{"println",println,METH_VARARGS,println_docs},
	{"encoding",encoding,	METH_VARARGS,encoding_docs},
	{NULL}
};

char pciomod_docs[] = "Programming contest input/output module.";

PyModuleDef pcio_mod = {
	PyModuleDef_HEAD_INIT,
	"pcio",
	pciomod_docs,
	-1,
	pcio_funcs,
	NULL,
	NULL,
	NULL,
	NULL
};

PyMODINIT_FUNC PyInit_pcio(void) {
	return PyModule_Create(&pcio_mod);
}
