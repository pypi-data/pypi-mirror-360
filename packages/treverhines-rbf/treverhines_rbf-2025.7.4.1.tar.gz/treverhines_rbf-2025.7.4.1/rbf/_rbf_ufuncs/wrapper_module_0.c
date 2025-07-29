#include "Python.h"
#include "math.h"
#include "numpy/ndarraytypes.h"
#include "numpy/ufuncobject.h"
#include "numpy/halffloat.h"
#include "wrapped_code_0.h"

static PyMethodDef wrapper_module_0Methods[] = {
        {NULL, NULL, 0, NULL}
};

#ifdef NPY_1_19_API_VERSION
static void wrapped_281415911921408_ufunc(char **args, const npy_intp *dimensions, const npy_intp* steps, void* data)
#else
static void wrapped_281415911921408_ufunc(char **args, npy_intp *dimensions, npy_intp* steps, void* data)
#endif
{
    npy_intp i;
    npy_intp n = dimensions[0];
    char *in0 = args[0];
    char *in1 = args[1];
    char *in2 = args[2];
    char *out0 = args[3];
    npy_intp in0_step = steps[0];
    npy_intp in1_step = steps[1];
    npy_intp in2_step = steps[2];
    npy_intp out0_step = steps[3];
    for (i = 0; i < n; i++) {
        *((double *)out0) = autofunc0(*(double *)in0, *(double *)in1, *(double *)in2);
        in0 += in0_step;
        in1 += in1_step;
        in2 += in2_step;
        out0 += out0_step;
    }
}
PyUFuncGenericFunction wrapped_281415911921408_funcs[1] = {&wrapped_281415911921408_ufunc};
static char wrapped_281415911921408_types[4] = {NPY_DOUBLE, NPY_DOUBLE, NPY_DOUBLE, NPY_DOUBLE};
static void *wrapped_281415911921408_data[1] = {NULL};

#if PY_VERSION_HEX >= 0x03000000
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "wrapper_module_0",
    NULL,
    -1,
    wrapper_module_0Methods,
    NULL,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit_wrapper_module_0(void)
{
    PyObject *m, *d;
    PyObject *ufunc0;
    m = PyModule_Create(&moduledef);
    if (!m) {
        return NULL;
    }
    import_array();
    import_umath();
    d = PyModule_GetDict(m);
    ufunc0 = PyUFunc_FromFuncAndData(wrapped_281415911921408_funcs, wrapped_281415911921408_data, wrapped_281415911921408_types, 1, 3, 1,
            PyUFunc_None, "wrapper_module_0", "Created in SymPy with Ufuncify", 0);
    PyDict_SetItemString(d, "wrapped_281415911921408", ufunc0);
    Py_DECREF(ufunc0);
    return m;
}
#else
PyMODINIT_FUNC initwrapper_module_0(void)
{
    PyObject *m, *d;
    PyObject *ufunc0;
    m = Py_InitModule("wrapper_module_0", wrapper_module_0Methods);
    if (m == NULL) {
        return;
    }
    import_array();
    import_umath();
    d = PyModule_GetDict(m);
    ufunc0 = PyUFunc_FromFuncAndData(wrapped_281415911921408_funcs, wrapped_281415911921408_data, wrapped_281415911921408_types, 1, 3, 1,
            PyUFunc_None, "wrapper_module_0", "Created in SymPy with Ufuncify", 0);
    PyDict_SetItemString(d, "wrapped_281415911921408", ufunc0);
    Py_DECREF(ufunc0);
}
#endif