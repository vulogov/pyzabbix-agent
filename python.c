/*
** Zabbix
** Copyright (C) 2001-2014 Zabbix SIA
**
** This program is free software; you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation; either version 2 of the License, or
** (at your option) any later version.
**
** This program is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
** GNU General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with this program; if not, write to the Free Software
** Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
**/


/*
 ** Vladimir Ulogov (c) 2014.
 ** Use it at your own risk
*/


#include "sysinc.h"
#include "module.h"
#include <Python.h>


extern char *CONFIG_LOAD_MODULE_PATH;
char        *modpath;
/* the variable keeps timeout setting for item processing */
static int	item_timeout = 0;

char *zbx_python_call_module(char* modname, AGENT_REQUEST *request, AGENT_RESULT *result);
int	zbx_module_python_ping(AGENT_REQUEST *request, AGENT_RESULT *result);
int	zbx_module_python_version(AGENT_REQUEST *request, AGENT_RESULT *result);
int	zbx_module_python_call(AGENT_REQUEST *request, AGENT_RESULT *result);

static ZBX_METRIC keys[] =
/*      KEY                     FLAG		FUNCTION        	TEST PARAMETERS */
{
	{"python.ping",		0,		zbx_module_python_ping,	NULL},
	{"python.version",	0,		zbx_module_python_version,	NULL},
	{"python",		CF_HAVEPARAMS,	zbx_module_python_call, ""},
	{NULL}
};



/******************************************************************************
 *                                                                            *
 * Function: zbx_python_call_module                                           *
 *                                                                            *
 * Purpose: importing module and calling it's "main()" function               *
 *                                                                            *
 * Return value: Return value from "main()" as a string                       *
 *                                                                            *
 ******************************************************************************/

char *zbx_python_call_module(char* modname, AGENT_REQUEST *request, AGENT_RESULT *result)  {
   int i;
   char *cstrret;
   PyObject* mod, *param, *fun, *ret;

   mod = PyImport_ImportModule(modname);
   param = PyTuple_New(request->nparam-1);
   for (i=1;i<request->nparam;i++) {
      PyTuple_SET_ITEM(param,i-1,PyString_FromString(get_rparam(request, i)));
   }
   fun = PyObject_GetAttrString(mod, "main");
   ret = PyEval_CallObject(fun, param);
   PyArg_Parse(ret, "s", &cstrret);
   printf("%s\n", cstrret);
   SET_STR_RESULT(result, strdup(cstrret));
   return cstrret;
}


/******************************************************************************
 *                                                                            *
 * Function: zbx_module_api_version                                           *
 *                                                                            *
 * Purpose: returns version number of the module interface                    *
 *                                                                            *
 * Return value: ZBX_MODULE_API_VERSION_ONE - the only version supported by   *
 *               Zabbix currently                                             *
 *                                                                            *
 ******************************************************************************/
int	zbx_module_api_version()
{
	return ZBX_MODULE_API_VERSION_ONE;
}

/******************************************************************************
 *                                                                            *
 * Function: zbx_module_item_timeout                                          *
 *                                                                            *
 * Purpose: set timeout value for processing of items                         *
 *                                                                            *
 * Parameters: timeout - timeout in seconds, 0 - no timeout set               *
 *                                                                            *
 ******************************************************************************/
void	zbx_module_item_timeout(int timeout)
{
	item_timeout = timeout;
}

/******************************************************************************
 *                                                                            *
 * Function: zbx_module_item_list                                             *
 *                                                                            *
 * Purpose: returns list of item keys supported by the module                 *
 *                                                                            *
 * Return value: list of item keys                                            *
 *                                                                            *
 ******************************************************************************/
ZBX_METRIC	*zbx_module_item_list()
{
   return keys;
}

int	zbx_module_python_ping(AGENT_REQUEST *request, AGENT_RESULT *result)
{
   SET_UI64_RESULT(result, 1);
   
   return SYSINFO_RET_OK;
}

int	zbx_module_python_version(AGENT_REQUEST *request, AGENT_RESULT *result)
{
   
   PyGILState_STATE gstate;
   gstate = PyGILState_Ensure();
   SET_STR_RESULT(result, strdup(Py_GetVersion()));
   PyGILState_Release(gstate);
   return SYSINFO_RET_OK;
}

int	zbx_module_python_call(AGENT_REQUEST *request, AGENT_RESULT *result)
{
   
   PyGILState_STATE gstate;
   gstate = PyGILState_Ensure();
   if (request->nparam < 1) {
      SET_MSG_RESULT(result, strdup("Invalid number of parameters."));
      return SYSINFO_RET_FAIL;
   }
   zbx_python_call_module(get_rparam(request, 0), request, result);
   PyGILState_Release(gstate);
   return SYSINFO_RET_OK;
}


/******************************************************************************
 *                                                                            *
 * Function: zbx_module_init                                                  *
 *                                                                            *
 * Purpose: the function is called on agent startup                           *
 *          It should be used to call any initialization routines             *
 *                                                                            *
 * Return value: ZBX_MODULE_OK - success                                      *
 *               ZBX_MODULE_FAIL - module initialization failed               *
 *                                                                            *
 * Comment: the module won't be loaded in case of ZBX_MODULE_FAIL             *
 *                                                                            *
 ******************************************************************************/
int	zbx_module_init()
{
   PyObject *mod, *param, *fun;
   modpath=malloc(strlen(CONFIG_LOAD_MODULE_PATH)+36);
   sprintf(modpath, "%s/pymodules", CONFIG_LOAD_MODULE_PATH);
   Py_SetProgramName("zabbix_agentd");
   Py_Initialize();
   PySys_SetPath(modpath);
   if ((mod = PyImport_ImportModule("ZBX_startup"))!=NULL) {
      fun = PyObject_GetAttrString(mod, "main");
      PyEval_CallObject(fun, Py_BuildValue("(s)", CONFIG_LOAD_MODULE_PATH));
   }
   return ZBX_MODULE_OK;
}

/******************************************************************************
 *                                                                            *
 * Function: zbx_module_uninit                                                *
 *                                                                            *
 * Purpose: the function is called on agent shutdown                          *
 *          It should be used to cleanup used resources if there are any      *
 *                                                                            *
 * Return value: ZBX_MODULE_OK - success                                      *
 *               ZBX_MODULE_FAIL - function failed                            *
 *                                                                            *
 ******************************************************************************/
int	zbx_module_uninit()
{
   PyObject *mod, *param, *fun;
   if ((mod = PyImport_ImportModule("ZBX_finish"))!=NULL) {
      fun = PyObject_GetAttrString(mod, "main");
      PyEval_CallObject(fun, Py_BuildValue("(s)", CONFIG_LOAD_MODULE_PATH));
   }
   Py_Finalize();
   free(modpath);
   return ZBX_MODULE_OK;
}
