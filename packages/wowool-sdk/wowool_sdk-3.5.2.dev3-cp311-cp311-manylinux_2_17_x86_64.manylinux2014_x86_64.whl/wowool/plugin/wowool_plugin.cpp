// ----------------------------------------------------------------------------------
// Copyright (c) 2024 Wowool, All Rights Reserved.
// NOTICE:  All information contained herein is, and remains the property of Wowool.
// ----------------------------------------------------------------------------------
#define WITH_THREAD

#include "wowool_plugin.hpp"
// #include <codecvt>
#include <functional>
#include <iostream>
#include <mutex>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
// #include <pybind11/stl_bind.h>
#include <regex>
#include <string>
#include <vector>
#include "nlohmann/json.hpp"
#include "plugins/api.hpp"
#include "wowool/common/c/plugin.h"
#include "wowool/common/exception.hpp"
#include "wowool/common/options.hpp"

// Undefine Logging
#define LOG_PLUGIN "[plugin]"
#define LOG_PYTHON "[py]"
#define TRACE 0
#define ERROR 0
#define DEBUG 0
#define WARNING 0
#define INFO 0
//#define WLOG(x, m) std::cout << m << std::endl;
#define WLOG(x, m)
// #define DEBUG_PYTHON_PLUGIN_MSG(x) std::cerr << "Thread ID: " << std::this_thread::get_id() << x << std::endl;
#define DEBUG_PYTHON_PLUGIN_MSG(x)

#ifdef __cplusplus
extern "C" {
#endif

struct _object;
typedef _object PyObject;

#ifdef __cplusplus
}
#endif

namespace py = pybind11;
using namespace wowool;

bool called_from_python_host_system = false;
///////////////////////////////////////////////////////////////////////////////////////
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
// forward declaration of global variable because the python people did not do a
// good job in creating a decent c/c++ api. we need to have this variable when
// we do the pytroushka :-) operation. which is from a python script :
//    --> which call the wowool python api
//    ----> which calls the c++ api
//    ------> which triggers call in python
//    ----------> which call back c++ functions
//    -------------> which could eventually call python functions.
// in short when we call Py_IsInitialized from within a native python script
// we cannot call Py_IsInitialized  otherwise the python people will make sure
// we crash. ( even if they say we need to ALWAYS call Py_IsInitialized ). but
// they forgot about the pytroushkas
// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

py::object python_object_range_obj;

namespace wow {
namespace python {

	// Convert a vector to a python list.
	template<class T>
	py::list to_list(std::vector<T> const &v)
	{
		typename std::vector<T>::const_iterator iter;
		py::list list;
		for (iter = v.begin(); iter != v.end(); ++iter)
		{
			list.append(*iter);
		}
		return list;
	}

	// wrapper class to make sure we close properly the python instance
	class python_instance
	{
	public:
		bool initialized_has_been_called = false;
		python_instance(bool embbeded_in_python = false)
		{
			if (called_from_python_host_system)
				return;

			if (embbeded_in_python)
				return;

			{
				DEBUG_PYTHON_PLUGIN_MSG("!!!!!!!!! Initialize Py_Initialize")
				Py_Initialize();
				DEBUG_PYTHON_PLUGIN_MSG("!!!!!!!!! Initialize PyEval_SaveThread")
				PyEval_SaveThread();
				initialized_has_been_called = true;
			}
		}

		~python_instance()
		{
			DEBUG_PYTHON_PLUGIN_MSG("!!!!!!!!! ~python_instance()")
			if (called_from_python_host_system)
				return;
			if (initialized_has_been_called)
			{
				DEBUG_PYTHON_PLUGIN_MSG("!!!!!!!!! PyGILState_Ensure")
				PyGILState_Ensure();
				DEBUG_PYTHON_PLUGIN_MSG("!!!!!!!!! Py_Finalize")
				Py_Finalize();
			}
		}
	};

	typedef std::function<bool(plugin_Annotation const *)>
		filter_annotation_filter_type;

	///////////////////////////////////////////////////////////////////////////////
	// AttributesPair
	/////////////////////////////////////////////////////////////////////////////////////////////
	AttributesPair::AttributesPair()
		: name_(nullptr)
		, value_(nullptr)
	{
	}

	AttributesPair::AttributesPair(void const *n, void *v)
		: name_(std::string(wowool_plugin_string_to_string(n)))
		, value_(std::string(wowool_plugin_any_to_string(v)))
	{
	}

	std::string AttributesPair::to_string() const
	{
		std::string retval = name_;
		retval += ":";
		retval += value_;
		return retval;
	}

	///////////////////////////////////////////////////////////////////////////////
	// python_object_attributes
	/////////////////////////////////////////////////////////////////////////////////////////////
	python_object_attributes::python_object_attributes()
		: cncpt()
	{
	}

	python_object_attributes::python_object_attributes(plugin_Annotation const *cncpt_)
		: cncpt(cncpt_)
	{
		int idx = 0;
		void *key = wowool_plugin_concept_attribute_key(cncpt, idx);
		while (key)
		{
			void *value = wowool_plugin_concept_attribute_value(cncpt, idx);
			this->emplace_back(key, value);
			key = wowool_plugin_concept_attribute_key(cncpt, ++idx);
		}
	}

	bool python_object_attributes::has(std::string const &key) const
	{
		if (!this->empty())
		{
			return wowool_plugin_concept_has_attribute(cncpt, key.c_str());
		}
		return false;
	}

	bool python_object_attributes::pybool() const
	{
		return cncpt == nullptr;
	}

	std::string python_object_attributes::to_string() const
	{
		std::stringstream strm;
		strm << '[';
		std::copy(begin(), end(), std::ostream_iterator<AttributesPair>(strm, ", "));
		strm << ']';
		return strm.str();
	}

	std::once_flag once;
	thread_local c_context thrd_context;

	// #define PYTHON_LOCK python::python_lock pylock;
	std::mutex global_python_mutex;
	// #define PYTHON_LOCK std::lock_guard<std::mutex> guard(global_python_mutex);
	// #define PYTHON_LOCK
	std::string get_python_error_message();

	class python_instance;

	// return the current error message in the python module.
	std::string get_python_error_message()
	{
		PyObject *type = nullptr, *value = nullptr, *traceback = nullptr,
				 *pyString = nullptr;
		PyErr_Fetch(&type, &value, &traceback);
		PyErr_Clear();
		std::string message = "Python error: ";
		if (type != nullptr && (pyString = PyObject_Str(type)) != nullptr && (PyUnicode_Check(pyString)))
		{
			PyObject *pyStr = PyUnicode_AsEncodedString(pyString, "utf-8", "Error ~");
			const char *strExcType = PyBytes_AS_STRING(pyStr);
			message += strExcType;
			Py_XDECREF(strExcType);
			Py_XDECREF(pyStr);
		}
		else
		{
			message += "<unknown exception type> ";
		}
		Py_XDECREF(pyString);
		if (value != nullptr && (pyString = PyObject_Str(value)) != nullptr && (PyUnicode_Check(pyString)))
		{
			message += ": ";
			PyObject *pyStr = PyUnicode_AsEncodedString(pyString, "utf-8", "Error ~");
			const char *strExcType = PyBytes_AS_STRING(pyStr);
			message += strExcType;
			Py_XDECREF(strExcType);
			Py_XDECREF(pyStr);
		}
		else
		{
			message += "<unknown exception date> ";
		}
		Py_XDECREF(pyString);

		char const *verbose = std::getenv("WOWOOL_LOG_LEVEL");
		if (verbose && strcmp(verbose, "DEBUG") == 0)
		{
			// Get the trace
			PyObject *tracebackModule = PyImport_ImportModule("traceback");
			if (tracebackModule != nullptr)
			{
				PyObject *tbList = nullptr;
				PyObject *emptyString = nullptr;
				PyObject *strRetval = nullptr;

				tbList = PyObject_CallMethod(tracebackModule, "format_exception", "OOO", type, value == nullptr ? Py_None : value, traceback == nullptr ? Py_None : traceback);

				if (tbList)
				{
					emptyString = PyUnicode_FromString("");

					strRetval = PyObject_CallMethod(emptyString, "join", "O", tbList);
					if (strRetval)
					{
						PyObject *pyStr = PyUnicode_AsEncodedString(strRetval, "utf-8", "Error ~");
						const char *strExcType = PyBytes_AS_STRING(pyStr);
						message += "\n";
						message += strExcType;
						Py_XDECREF(strExcType);
						Py_XDECREF(pyStr);
					}

					Py_DECREF(tbList);
					if (emptyString)
						Py_DECREF(emptyString);
				}
				if (strRetval)
					Py_DECREF(strRetval);
				Py_DECREF(tracebackModule);
			}
			else
			{
				// chrRetval = strdup("Unable to import traceback module.");
				message += "Unable to import traceback module.";
			}
		}
		Py_XDECREF(type);
		Py_XDECREF(value);
		Py_XDECREF(traceback);

		return message;
		// FIXME: Now we have an error message .. log it or something.
	}

	char *alloc_string(std::string const &str)
	{
		if (str.length() != 0)
		{
			char *data = (char *)malloc(str.size() + 1);
			memcpy(data, str.c_str(), str.size());
			data[str.size()] = 0;
			return data;
		}
		else
		{
			return nullptr;
		}
	}

	//----------------------------------------------------------------
	// class to collect the python modules
	//----------------------------------------------------------------
	class Facade
	{
	public:
		Facade(std::string const &module);
		char *call(char const *module_name, char const *function_name, wowool::plugins::Arguments const &arguments, tir_exception *ex);
		~Facade();

		std::string name;
		py::object module;
	};

	typedef std::shared_ptr<Facade> Facade_ptr;
	typedef std::map<std::string, Facade_ptr> FacadeCollection;

	Facade::Facade(std::string const &module_name)
		: name(module_name)
		, module(py::module::import(name.c_str()))
	{
	}

	Facade::~Facade()
	{
	}

	char *Facade::call(char const *module_name, char const *function_name, wowool::plugins::Arguments const &arguments, tir_exception *ex)
	{
		assert(module);
		WLOG(TRACE, LOG_PLUGIN << LOG_PYTHON << "call(" << function_name << ")");
		PyObject *pFunc = nullptr;
		pFunc = PyObject_GetAttrString(module.ptr(), function_name);
		if (pFunc && PyCallable_Check(pFunc))
		{
			PyObject *pArgs, *pValue;
			pArgs = PyTuple_New(arguments.size());
			for (size_t i = 0; i < arguments.size(); ++i)
			{
				if (arguments[i].type == wowool::plugins::do_char_ptr)
				{
					pValue = PyUnicode_FromString((char *)arguments[i].data);
					if (!pValue)
					{
						Py_DECREF(pArgs);
						Py_XDECREF(pFunc);
						WLOG(ERROR, "Cannot convert argument");
						return nullptr;
					}
					/* pValue reference stolen here: */
					PyTuple_SetItem(pArgs, i, pValue);
				}
				else if (arguments[i].type == wowool::plugins::do_pydict)
				{
					py::dict &data = *((py::dict *)(arguments[i].data));
					data.inc_ref();
					PyTuple_SetItem(pArgs, i, data.ptr());
				}
				else if (arguments[i].type == wowool::plugins::do_annotation)
				{
					try
					{
						// get the object constructor.
						// create a python object.
						py::object pyobj = python_object_range_obj((plugin_Annotation *)arguments[i].data);
						pyobj.inc_ref();
						PyTuple_SetItem(pArgs, i, pyobj.ptr());
					} catch (std::exception &ex)
					{
						std::cerr << "error adding annotation attribute. " << ex.what() << std::endl;
					}
				}
			}

			pValue = PyObject_CallObject(pFunc, pArgs);
			if (pValue != nullptr)
			{
				std::string retval;
				if (PyBool_Check(pValue))
				{
					if (PyObject_IsTrue(pValue))
					{
						retval = "true";
					}
					else
					{
						retval = "false";
					}
				}
				else if (PyUnicode_Check(pValue))
				{
					retval = py::str(pValue);
				}
				Py_DECREF(pValue);
				Py_DECREF(pArgs);
				Py_XDECREF(pFunc);
				WLOG(TRACE, LOG_PLUGIN << LOG_PYTHON << "RETURN (" << retval << ")");
				return alloc_string(retval);
			}
			else
			{
				std::string errstr = get_python_error_message();
				WLOG(ERROR, "Could not execute python function:" << function_name << " in module " << module_name << ":" << errstr.c_str());
				wowool::common::throw_c_exception(ex, errstr.c_str());
				return nullptr;
			}

			Py_DECREF(pArgs);
			Py_XDECREF(pFunc);
		}
		else
		{
			WLOG(ERROR, "Could not find python function:" << function_name << " in module " << module_name);
		}

		/* Release the thread. No Python API allowed beyond this point. */
		// PyGILState_Release(gstate);

		WLOG(ERROR, "Could not find python function:" << function_name << " in module " << module_name);
		return nullptr;
	}

	struct IsURI
	{
		IsURI(std::string const &uri_)
			: uri(uri_.c_str())
		{
		}

		const char *uri;

		bool operator()(plugin_Annotation const *a) const
		{
			return ((wowool_plugin_get_type(a) == AnnotationType_Concept) && (strcmp(wowool_plugin_concept_uri(a), uri) == 0));
		}
	};

	std::ostream &operator<<(std::ostream &out, AttributesPair const &data)
	{
		out << '(' << data.name() << '=' << data.value() << ')';
		return out;
	}

	typedef std::pair<std::string, std::string> AttributePair;
	typedef std::map<std::string, std::string> AttributeCollection;

	AttributeCollection convert_py_options(py::dict const &kwargs)
	{
		AttributeCollection options;
		for (auto const item : kwargs)
		{
			options.emplace(py::str(item.first), py::str(item.second));
		}
		return options;
	}

	c_context const &get_current_context() { return thrd_context; }

	static std::shared_ptr<python::python_instance> python_instance_singleton;

	void create_python_instance()
	{
		python_instance_singleton.reset(new python::python_instance());
	}

	void init_python_instance() { std::call_once(once, &create_python_instance); }

	struct PyLock
	{
		PyLock()
		{
			DEBUG_PYTHON_PLUGIN_MSG(" >> PyGILState_Ensure");
			gstate = PyGILState_Ensure();
			DEBUG_PYTHON_PLUGIN_MSG(" << PyGILState_Ensure");
		}

		~PyLock()
		{
			DEBUG_PYTHON_PLUGIN_MSG(" >> PyGILState_Release");
			PyGILState_Release(gstate);
			DEBUG_PYTHON_PLUGIN_MSG(" << PyGILState_Release");
		}

		// PyThreadState *python_interprter;
		PyGILState_STATE gstate;
	};

	struct python_user_data_object
	{
		python_user_data_object()
			: pydict(nullptr)
		{
			pydict = new py::dict();
		}

		~python_user_data_object()
		{
			DEBUG_PYTHON_PLUGIN_MSG(">> ~python_user_data_object");
			if (pydict)
			{
				PyLock pylock;
				DEBUG_PYTHON_PLUGIN_MSG(">> delete python_user_data_object");
				delete pydict;
				DEBUG_PYTHON_PLUGIN_MSG("<< delete python_user_data_object");
			}
		}

		// PyThreadState *python_interprter;
		py::dict *pydict;
		// std::shared_ptr<python::python_instance> py_instance;
	};

	typedef std::shared_ptr<python_user_data_object> python_user_data;
	thread_local python_user_data thread_python_user_data;

	// create the python dictionary as user document data.
	python_user_data &create_userdata()
	{
		PyLock pylock;
		DEBUG_PYTHON_PLUGIN_MSG("PYDEBUG: create_userdata");

		thread_python_user_data.reset(new python_user_data_object);
		// py::gil_scoped_acquire acquire;
		thread_python_user_data->pydict = new py::dict();

		return thread_python_user_data;
	}

	python_user_data &get_current_userdata() { return thread_python_user_data; }

	// release the user data when we are done with the document.
	void release_userdata()
	{
		DEBUG_PYTHON_PLUGIN_MSG("PYDEBUG: release_userdata");
		if (thread_python_user_data.get())
		{
			DEBUG_PYTHON_PLUGIN_MSG("PYDEBUG: release_userdata.reset()");
			PyLock pylock;
			thread_python_user_data.reset();
		}
	}

	///////////////////////////////////////////////////////////////////////////////
	// python_token
	// object that represents a token object in python.
	/////////////////////////////////////////////////////////////////////////////////////////////
	python_token::python_token()
		: token(nullptr)
	{
	}

	python_token::python_token(plugin_Annotation const *token_)
		: token(token_)
	{
	}

	bool python_token::has_property(std::string const &prop) const
	{
		return wowool_plugin_token_has_attribute(token, prop.c_str());
	}

	std::string python_token::head() const
	{
		return wowool_plugin_token_head(token);
	}

	std::string python_token::pos(int idx) const
	{
		return wowool_plugin_token_pos(token, idx);
	}

	std::string python_token::stem(int idx) const
	{
		return wowool_plugin_token_stem(token, idx);
	}

	std::string python_token::lemma(int idx) const
	{
		return wowool_plugin_token_stem(token, idx);
	}

	std::string python_token::str() const
	{
		return std::string(wowool_plugin_token_literal(token));
	}

	///////////////////////////////////////////////////////////////////////////////
	// python_object_range
	// object that represent a annotation range in python.
	/////////////////////////////////////////////////////////////////////////////////////////////
	python_object_range::python_object_range() {}

	python_object_range::python_object_range(plugin_Annotation const *cncpt)
	{
		begin = cncpt;
		if (begin)
		{
			end = wowool_plugin_concept_get_end(cncpt);
		}
	}

	python_object_range::~python_object_range() {}

	python_object_range::python_object_range(plugin_Annotation const *begin_, plugin_Annotation const *end_)
	{
		begin = begin_;
		end = end_;
	}

	void python_object_range::remove_concept()
	{
		wowool_plugin_concept_remove(const_cast<plugin_Annotation *>(begin));
	}

	int python_object_range::get_begin_offset() const
	{
		if (begin)
			return wowool_plugin_get_begin_offset(begin);
		return -1;
	}

	int python_object_range::get_end_offset() const
	{
		plugin_Annotation const *it = end;
		while (it != nullptr)
		{
			if (wowool_plugin_get_type(it) == AnnotationType_Token)
			{
				return wowool_plugin_get_end_offset(it);
			}
			it = wowool_plugin_get_prev(it);
		}
		return get_begin_offset();
	}

	std::string python_object_range::get_uri() const
	{
		if (begin && wowool_plugin_get_type(begin) == AnnotationType_Concept)
			return std::string(wowool_plugin_concept_uri(begin));
		return "";
	}

	std::vector<python_object_range> python_object_range::find_with_filter(
		filter_annotation_filter_type const &filter)
	{
		std::vector<python_object_range> retval;
		// tir::wowool::is_concept filter;

		// algin to the begin end offset of the given annotation.
		auto it = wowool_plugin_align_begin(begin, end);

		while (it != end)
		{
			if (filter(it))
			{
				if (!wowool_plugin_concept_is_deleted(it))
				{
					retval.emplace_back(python_object_range(it));
				}
			}
			it = wowool_plugin_get_next(it);
		}
		return retval;
	}

	python_object_attributes python_object_range::attributes()
	{
		return python_object_attributes(begin);
	}

	bool python_object_range::has(std::string const &key) const
	{
		return wowool_plugin_concept_has_attribute(begin, key.c_str());
	}

	std::string python_object_range::get_attribute(std::string const &key) const
	{
		return std::string(wowool_plugin_concept_get_attribute(begin, key.c_str()));
	}

	bool python_object_range::add_attribute(std::string const &key, std::string const &value)
	{
		return wowool_plugin_concept_add_attribute(
			const_cast<plugin_Annotation *>(begin), key.c_str(), value.c_str());
	}

	// filter a range of annotations.
	std::vector<python_object_range>
	python_object_range::regex(std::string const &uri)
	{
		std::regex re(uri);
		std::smatch what;
		// Note: uri is a char pointer !
		return find_with_filter([&](plugin_Annotation const *a) -> bool {
			if (wowool_plugin_get_type(a) == AnnotationType_Concept)
			{
				std::string uri = wowool_plugin_concept_uri(a);
				return std::regex_match(uri, what, re);
			}
			return false;
		});
	}

	python_object_range python_object_range::add_concept(std::string const &uri)
	{
		auto const context = python::get_current_context();
		plugin_Annotation *annotation = wowool_plugin_update_concept_in_collection(&context, begin, end, uri.c_str());
		if (annotation)
		{
			return python_object_range(annotation);
		}
		else
		{
			return python_object_range();
		}
	}

	// implements the python calls capture["person" ]
	// argument is a string
	std::vector<python_object_range>
	python_object_range::get_item(std::string const &uri)
	{
		return find(uri);
	}

	// implements the python calls capture["person","boss", .... ]
	// argument is a tuple (a,b,c,...)
	std::vector<python_object_range>
	python_object_range::get_item(py::tuple const &elements)
	{
		std::vector<python_object_range> results;
		for (auto const item : elements)
		{
			std::string key = py::str(item);
			std::vector<python_object_range> tmp = find(key);
			std::copy(tmp.begin(), tmp.end(), std::back_inserter(results));
		}
		return results;
	}

	// implements the python calls capture.person
	// argument is a string
	py::object python_object_range::get_attr(std::string const &uri)
	{
		return find_one(uri);
	}

	py::object python_object_range::find_one(std::string const &uri)
	{
		assert(begin);
		// Note do note align for the attribute.
		if (wowool_plugin_get_type(begin) == AnnotationType_Concept)
		{
			if (wowool_plugin_concept_has_attribute(begin, uri.c_str()))
			{
				return py::str(
					std::string(wowool_plugin_concept_get_attribute(begin, uri.c_str())));
			}
		}

		std::vector<python_object_range> results;
		if (uri.size() >= 2 && uri[0] == '/' && uri[uri.size() - 1] == '/')
		{
			results = regex(uri.substr(1, uri.size() - 2));
		}
		else
		{
			IsURI filter(uri);
			results = find_with_filter(filter);
		}
		if (results.size())
			return py::cast(results[0]);
		return py::none();
	}

	std::vector<python_object_range>
	python_object_range::find(std::string const &uri)
	{
		if (uri.size() > 2 && uri[0] == '/' && uri[uri.size() - 1] == '/')
			return regex(uri.substr(1, uri.size() - 2));
		IsURI filter(uri);
		return find_with_filter(filter);
	}

	std::vector<int> python_object_range::find_int(std::string const &uri)
	{
		return std::vector<int>();
	}

	py::list python_object_range::tokens()
	{
		if (begin == nullptr)
		{
			std::vector<python_token> v;
			return python::to_list(v);
		}
		std::vector<python_token> retval;
		std::stringstream strm;
		auto it = begin;
		while (it != end)
		{
			if (wowool_plugin_get_type(it) == AnnotationType_Token)
			{
				retval.emplace_back(it);
			}
			it = wowool_plugin_get_next(it);
		}
		return python::to_list(retval);
	}

	std::string python_object_range::str() { return literal(); }

	std::string python_object_range::repr() const
	{
		std::stringstream out;
		auto it = begin;
		while (it != end)
		{
			if (wowool_plugin_get_type(it) == AnnotationType_Token)
			{
				out << "T:" << wowool_plugin_token_literal(it) << std::endl;
			}
			else if (wowool_plugin_get_type(it) == AnnotationType_Concept)
			{
				out << "C:" << wowool_plugin_concept_uri(it) << std::endl;
			}
			it = wowool_plugin_get_next(it);
		}
		return out.str();
	}

	std::string python_object_range::literal(std::string const delimiter)
	{
		if (begin == nullptr)
			return "";
		return std::string(
			wowool_plugin_range_literal(begin, end, delimiter.c_str()));
	}

	std::string python_object_range::canonical(std::string const delimiter)
	{
		if (begin == nullptr)
			return "";

		if (wowool_plugin_get_type(begin) == AnnotationType_Concept)
		{
			if (wowool_plugin_concept_has_attribute(begin, "canonical"))
			{
				return py::str(
					std::string(wowool_plugin_concept_get_attribute(begin, "canonical")));
			}
			else
			{
				return literal(delimiter);
			}
		}

		return std::string(
			wowool_plugin_range_literal(begin, end, delimiter.c_str()));
	}

	std::string python_object_range::stem(std::string const delimiter)
	{
		if (begin == nullptr)
			return "";
		return std::string(wowool_plugin_range_stem(begin, end, delimiter.c_str()));
	}

	std::string python_object_range::lemma(std::string const delimiter)
	{
		if (begin == nullptr)
			return "";
		return std::string(wowool_plugin_range_stem(begin, end, delimiter.c_str()));
	}

	bool python_object_range::pybool() const
	{
		return begin != nullptr;
	}

	bool operator==(python_object_range const &lhs, python_object_range const &rhs)
	{
		return ((lhs.begin == rhs.begin) && (lhs.end == rhs.end));
	}

	// the match context api.
	python_object_match_context::python_object_match_context() { context = python::get_current_context(); }

	python_object_range python_object_match_context::capture()
	{
		return python_object_range(python::get_current_context().capture);
	}

	python_object_range python_object_match_context::rule()
	{
		if (context.rule == nullptr)
			return python_object_range(python::get_current_context().capture);
		return python_object_range(python::get_current_context().rule);
	}

	python_object_range python_object_match_context::sentence()
	{
		if (context.sent)
		{
			return python_object_range(wowool_plugin_sentence_begin(context.sent), wowool_plugin_sentence_end(context.sent));
		}
		return python_object_range();
	}

	python_object_range python_object_match_context::make_range(python_object_range begin_, python_object_range end_)
	{
		return python_object_range(begin_.begin, end_.end);
	}

	std::string python_object_match_context::to_string() { return wowool_plugin_concept_uri(context.capture); }

	const std::string python_object_match_context::property(std::string const &key) { return wowool_plugin_property(&context, key.c_str()); }

}
} // namespace wow::python
// ----------------------------------------------------------------------------
// Plugin code to be loaded in the cpp module
// ----------------------------------------------------------------------------
namespace wow {
namespace python {

	using wowool::plugins::Arguments;

	// convert UTF-8 string to wstring
	std::string wstring_to_utf8(const std::wstring &wstr)
	{
		std::string utf8;
		for (wchar_t wc : wstr)
		{
			if (wc <= 0x7F)
			{
				utf8.push_back(static_cast<char>(wc)); // ASCII range (1 byte)
			}
			else if (wc <= 0x7FF)
			{
				utf8.push_back(static_cast<char>(0xC0 | ((wc >> 6) & 0x1F))); // 2 bytes
				utf8.push_back(static_cast<char>(0x80 | (wc & 0x3F)));
			}
			else if (wc <= 0xFFFF)
			{
				utf8.push_back(static_cast<char>(0xE0 | ((wc >> 12) & 0x0F))); // 3 bytes
				utf8.push_back(static_cast<char>(0x80 | ((wc >> 6) & 0x3F)));
				utf8.push_back(static_cast<char>(0x80 | (wc & 0x3F)));
			}
			else
			{
				utf8.push_back(static_cast<char>(0xF0 | ((wc >> 18) & 0x07))); // 4 bytes
				utf8.push_back(static_cast<char>(0x80 | ((wc >> 12) & 0x3F)));
				utf8.push_back(static_cast<char>(0x80 | ((wc >> 6) & 0x3F)));
				utf8.push_back(static_cast<char>(0x80 | (wc & 0x3F)));
			}
		}
		return utf8;
	}

	std::wstring utf8_to_wstring(const std::string &str)
	{
		std::wstring wstr;
		size_t i = 0;
		while (i < str.size())
		{
			unsigned char ch = str[i];
			wchar_t wc = 0;
			int extra_bytes = 0;

			if ((ch & 0x80) == 0)
			{ // 1-byte character (ASCII)
				wc = ch;
			}
			else if ((ch & 0xE0) == 0xC0)
			{ // 2-byte character
				wc = ch & 0x1F;
				extra_bytes = 1;
			}
			else if ((ch & 0xF0) == 0xE0)
			{ // 3-byte character
				wc = ch & 0x0F;
				extra_bytes = 2;
			}
			else if ((ch & 0xF8) == 0xF0)
			{ // 4-byte character
				wc = ch & 0x07;
				extra_bytes = 3;
			}

			for (int j = 0; j < extra_bytes; ++j)
			{
				if (++i >= str.size()) return {}; // Invalid UTF-8
				wc = (wc << 6) | (str[i] & 0x3F);
			}
			wstr.push_back(wc);
			++i;
		}
		return wstr;
	}

	class Plugin : public wowool::plugins::API
	{
	public:
		Plugin();
		virtual ~Plugin();

		virtual bool load_modules(char const *json_options, tir_exception *) noexcept;
		bool _nolock_load_modules(char const *json_options, tir_exception *) noexcept;

		virtual char *call(char const *module_name, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept;

		char *_nolock_call(char const *module_name, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept;

		// virtual char *init(char const *module_name, char const *name, wowool::plugins::Arguments
		// const &arguments, tir_exception *ex) noexcept;
		virtual char *open_document(char const *module_name, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept;
		virtual char *close_document(char const *module_name, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept;
		virtual char *trigger(char const *module_name, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept;
		virtual void release_document(tir_exception *) noexcept;
		virtual void set_document_property(char const *key, char const *value, tir_exception *) noexcept;

		virtual void release(void *ptr) noexcept;

		virtual void delete_this(tir_exception *) noexcept { py_modules.clear(); }

		virtual void set_context(c_context *ctxt) noexcept
		{
			thrd_context.blackbrd = ctxt->blackbrd;
			thrd_context.sent = ctxt->sent;
			thrd_context.rule = ctxt->rule;
			thrd_context.capture = ctxt->capture;
		}

	private:
		FacadeCollection py_modules;
	};

	Plugin::Plugin()
		: wowool::plugins::API()
	{
	}

	Plugin::~Plugin() {}

	void Plugin::release_document(tir_exception *ex) noexcept
	{
		release_userdata();
	}

	void Plugin::set_document_property(char const *key, char const *value, tir_exception *) noexcept
	{
		python_user_data &ud = get_current_userdata();
		if (ud.get() == nullptr)
		{
			ud = create_userdata();
		}
		PyLock py_lock;
		if (ud.get() != nullptr && ud->pydict != nullptr)
		{
			(*ud->pydict)[key] = value;
		}
	}

#define LOG_TRACE LOG(TRACE)
#define TIR_LOG_DEBUG LOG(DEBUG)
	static std::string empty;

	std::string const get(nlohmann::json const &options, std::string const key)
	{
		if (options.find(key) != options.end())
		{
			return options[key].get<std::string>();
		}
		return empty;
	}

	bool has(nlohmann::json const &options, std::string const key)
	{
		return (options.find(key) != options.end());
	}

	// Load the given modules.
	bool Plugin::load_modules(char const *json_options, tir_exception *ex) noexcept
	{
		bool retval = false;
		retval = _nolock_load_modules(json_options, ex);
		return retval;
	}

	char *Plugin::call(char const *module_name, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept
	{
		try
		{
			char *retval = nullptr;
			// python_object_range_obj = py::module::import("wowool_plugin").attr("annotation_range");

			python_user_data &ud = get_current_userdata();
			if (ud.get() == nullptr)
			{
				ud = create_userdata();
			}

			PyLock pylock;
			retval = _nolock_call(module_name, name, arguments, ex);
			return retval;
		} catch (pybind11::error_already_set const &ex)
		{
			std::cerr << "Error: already set" << ex.what() << std::endl;
			return nullptr;
		} catch (std::exception const &ex)
		{
			std::cerr << "Error: " << ex.what() << std::endl;
			return nullptr;
		}
	}

	// Load the given modules.
	bool Plugin::_nolock_load_modules(char const *json_options, tir_exception *ex) noexcept
	{
		// std::ofstream fo("dump.txt");
		WLOG(TRACE, LOG_PLUGIN << LOG_PYTHON << "load_modules(" << json_options << ")\n");
		nlohmann::json options = nlohmann::json::parse(json_options);

		//#ifdef WIN32
		// set_python_home(options);
		//#endif

		bool embbeded_in_python = true;
		{
			if (!has(options, "pytryoshka"))
			{
				embbeded_in_python = false;
			}
		}

		if (!embbeded_in_python)
		{
			WLOG(TRACE, LOG_PLUGIN << LOG_PYTHON << "init_python_instance");
			wow::python::init_python_instance(); // Py_Initialize();
		}

		return true;
	}

	using wowool::plugins::Arguments;
	namespace lbp = wowool::plugins;

	char *Plugin::_nolock_call(char const *module_name, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept
	{
		if (auto it = py_modules.find(module_name); it != py_modules.end())
		{
			auto const &module = it->second;
			if (module.get())
			{
				char *retval = module->call(module_name, name, arguments, ex);
				return retval;
			}
			return nullptr;
		}
		else
		{
			WLOG(INFO, LOG_PLUGIN << LOG_PYTHON << "Loading python module: " << module_name);
			try
			{
				Facade_ptr ptr(new Facade(module_name));
				WLOG(DEBUG, LOG_PLUGIN << LOG_PYTHON << "OK Module:" << module_name);
				py_modules.emplace(module_name, ptr);
				auto const &module = py_modules.at(module_name);
				char *retval = module->call(module_name, name, arguments, ex);
				return retval;
			} catch (pybind11::error_already_set const &ex_import)
			{
				std::cerr << "Error:[wowool_plugin] Could not import " << module_name << " module"
						  << "\n"
						  << ex_import.what() << ")" << std::endl;
				py_modules.emplace(module_name, Facade_ptr());
			}
		}

		return nullptr;
	}

	char *Plugin::open_document(char const *module, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept
	{
		create_userdata();
		return trigger(module, name, arguments, ex);
	}

	char *Plugin::close_document(char const *module, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept
	{
		char *result = trigger(module, name, arguments, ex);
		release_userdata();
		return result;
	}

	char *Plugin::trigger(char const *module, char const *name, wowool::plugins::Arguments const &arguments, tir_exception *ex) noexcept
	{
		python_user_data &ud = get_current_userdata();
		if (ud.get() == nullptr)
		{
			create_userdata();
		}

		Arguments decorated_arguments = arguments;
		if (ud.get() != nullptr)
		{
			decorated_arguments.emplace(decorated_arguments.begin(), wowool::plugins::do_pydict, ud->pydict);
		}
		char *retval = call(module, name, decorated_arguments, ex);
		return retval;
	}

	// release a pointer which got return by this api, We need to have this as the
	// malloc and the free has to happen in the same module.
	// example alloc_string( ... )
	void Plugin::release(void *ptr) noexcept
	{
		DEBUG_PYTHON_PLUGIN_MSG("Plugin::release");
		if (ptr != nullptr)
		{
			free(ptr);
		}
	}
}
} // namespace wow::python

//
// Dynamic shared object (DSO) and dynamic-link library (DLL) support
//
#if defined(_WIN32) || defined(__WIN32__) || defined(WIN32) || defined(__CYGWIN__)
  //#define WOW_BOOST_SYMBOL_EXPORT __attribute__((__dllexport__))
	#define WOW_BOOST_SYMBOL_EXPORT __declspec(dllexport)

#else
	#define WOW_BOOST_SYMBOL_EXPORT __attribute__((__visibility__("default")))
#endif

extern "C" WOW_BOOST_SYMBOL_EXPORT wow::python::Plugin plugin;

wow::python::Plugin plugin;

// ----------------------------------------------------------------------------------
// Copyright (c) 2024 Wowool, All Rights Reserved.
// NOTICE:  All information contained herein is, and remains the property of Wowool.
// !!! Note merging the code with the python plugin module.
// ----------------------------------------------------------------------------------
typedef std::vector<wow::python::AttributesPair> python_object_attributes_type;
typedef wow::python::python_object_range python_object_range;
using wow::python::AttributesPair;
using wow::python::python_object_attributes;
using wow::python::python_object_match_context;
using wow::python::python_token;

PYBIND11_MAKE_OPAQUE(python_object_attributes_type);

// ----------------------------------------------------------------------------
// Python Bindings for the wowool_plugin.
// ----------------------------------------------------------------------------
PYBIND11_MODULE(_wowool_plugin, m)
{
	using namespace pybind11::literals;

	py::class_<python_token>(m, "python_token")
		.def("has_property", &python_token::has_property)
		.def("head", &python_token::head)
		.def("pos", &python_token::pos, py::arg("idx") = 0)
		.def("stem", &python_token::stem, py::arg("idx") = 0)
		.def("lemma", &python_token::lemma, py::arg("idx") = 0)
		.def("__repr__", &python_token::str, "Returns literal")
		.def("__str__", &python_token::str, "Returns literal");

	py::class_<python_object_range>(m, "annotation_range", "\nA annotation range marks the begin and "
														   "end of a annotation collection.")
		.def(py::init([](plugin_Annotation *cnpt) {
			return new python_object_range(cnpt);
		})) // C++ constructor, shadowed by raw ctor
		.def_property_readonly("tokens", &python_object_range::tokens, "Returns a list with the tokens of this range.")
		.def("literal", &python_object_range::literal, "\n:param separator: separator between the tokens, default space."
													   "\n:type separator: str"
													   ":returns: a literal string of this range, you can specify the "
													   "literal delimiter ",
			 py::arg("separator") = " ")
		.def("canonical", &python_object_range::canonical, "\n:param separator: separator between the tokens, default space."
														   "\n:type separator: str"
														   ":returns: a canonical string of this range, you can specify the "
														   "canonical delimiter ",
			 py::arg("separator") = " ")
		.def("__repr__", &python_object_range::repr, ":returns: the literal string of this range, you can specify the "
													 "stem delimiter.")
		.def("__str__", &python_object_range::str, ":returns: the literal string of this range, you can specify the "
												   "stem delimiter.")
		.def("stem", &python_object_range::stem, "\n:param separator: separator between the tokens, default space."
												 "\n:type separator: str"
												 ":returns: a string with the stems of this range, you can specify "
												 "the literal delimiter ",
			 py::arg("separator") = " ")
		.def("lemma", &python_object_range::lemma, "\n:param separator: separator between the tokens, default space."
												   "\n:type separator: str"
												   ":returns: a string with the stems of this range, you can specify "
												   "the literal delimiter ",
			 py::arg("separator") = " ")
		.def("find", &python_object_range::find, "\n:param uri: uri of a concept to find."
												 "\n:type uri: str"
												 "\n:returns: a list of annotation_range object"
												 "\n:type: list(annotation_range)",
			 py::arg("uri"))
		.def("find_one", &python_object_range::find_one, "\n:param uri: uri of a concept to find."
														 "\n:type uri: str"
														 "\n:returns: a annotation_range object"
														 "\n:type: annotation_range",
			 py::arg("uri"))
		// when accessing the scope using a . then the return will be one range.
		// example capture.person will return the first person.
		// .def("__getattr__", &python_object_range::get_attr )
		.def(
			"__getattr__",
			static_cast<py::object (python_object_range::*)(std::string const &)>(
				&python_object_range::get_attr))
		// when accessing the scope using a ['person'] then the return will be  a
		// vector of ranges example capture['person'] will return the all the
		// persons in the scope.
		.def("__getitem__", static_cast<std::vector<python_object_range> (python_object_range::*)(std::string const &)>(&python_object_range::get_item))
		.def("__getitem__", static_cast<std::vector<python_object_range> (python_object_range::*)(py::tuple const &)>(&python_object_range::get_item))
		.def("attributes", &python_object_range::attributes, "Returns the Attribute Object of this range.")
		.def("has", &python_object_range::has, "\n:param name: name of the attribute."
											   "\n:type name: str"
											   "\n:returns: true if this range has the given attribute."
											   "\n:type: bool",
			 py::arg("name"))
		.def("attribute", &python_object_range::get_attribute, "\n:param name: name of the attribute."
															   "\n:type name: str"
															   "\n:returns: the value of the given attribute."
															   "\n:type: str",
			 py::arg("name"))
		.def("add_attribute", &python_object_range::add_attribute, "Add a attribute to this range", py::arg("key"), py::arg("value"))
		.def("add_concept", &python_object_range::add_concept, "Add a concept ( semantic annotation ) over this range."
															   "\n"
															   "\n    ::"
															   "\n"
															   "\n      capture = match.capture()"
															   "\n      capture.add_concept('other_uri')"
															   "\n",
			 py::arg("uri"))
		.def("uri", &python_object_range::get_uri, "\n:returns: the uri of this annotation"
												   "\n:type: str")
		.def("begin_offset", &python_object_range::get_begin_offset, "\n:returns: a int with the begin offset of this range."
																	 "\n:type begin_offset: int")
		.def("end_offset", &python_object_range::get_end_offset, "\n:returns: a int with the end offset of this range."
																 "\n:type end_offset: int")
		.def("remove", &python_object_range::remove_concept, "remove the annotation over this range.")
		.def("__bool__", &python_object_range::pybool);

	py::class_<python_object_match_context>(
		m, "match_info", "\nIs all the data related to the match of the triggered function."
						 "\nThis object contains the capture, rule and the sentence where the "
						 "match was located."
						 "\n\nEXAMPLE"
						 "\n match = wowool_plugin.match_info()"
						 "\n capture_group = match.capture()")
		.def(py::init([]() { return new python_object_match_context(); }))
		.def("uri", &python_object_match_context::to_string, ":returns: the uro of the rule")
		.def("sentence", &python_object_match_context::sentence, "The sentence object (range) where the match has occurred.")
		.def("rule", &python_object_match_context::rule, ":returns: the annotation range that the rule has matched. "
														 "\n"
														 "\n    ::"
														 "\n"
														 "\n      ex rule: { <'Mr'> { <'Fawlty'> }= "
														 "::python::module_name::silly_person }= rule_context;"
														 "\n"
														 "\nHere the range is 'Mr Fawlty'= rule_context."
														 "\n:type: annotation_range")
		.def("capture", &python_object_match_context::capture, ":returns: the annotation range that we have captured. "
															   "\n"
															   "\n    ::"
															   "\n"
															   "\n        ex rule: { <'Mr'> { <'Fawlty'> }= "
															   "::python::module_name::silly_person }= rule_context;"
															   "\n"
															   "\nHere the range is 'Fawlty'= silly_person."
															   "\n:type: annotation_range")
		.def("property", &python_object_match_context::property, ":returns: a property of the range (ex: language)", py::arg("key"))
		.def("range", &python_object_match_context::make_range, "\n:param begin_range: begin position of the range."
																"\n:type begin_range: annotation_range"
																"\n:param end_range: end position of the range."
																"\n:type end_range: annotation_range"
																"\n:returns: a annotation range for the given begin and end "
																"annotation."
																"\n:type: annotation_range",
			 py::arg("begin_range"),
			 py::arg("end_range"));

	// py::bind_vector<python_object_attributes>(m, "python_object_attributes");

	py::class_<python_object_attributes>(m, "Attributes")
		.def("has", &python_object_attributes::has)
		.def("__len__", &python_object_attributes::size)
		.def(
			"__iter__",
			[](python_object_attributes &v) {
				return py::make_iterator(v.begin(), v.end());
			},
			py::keep_alive<0, 1>()) /*Keep vector alive while iterator is used*/
		.def("__bool__", &python_object_attributes::pybool)
		.def("__repr__", &python_object_attributes::to_string)
		.def("__str__", &python_object_attributes::to_string);

	py::class_<AttributesPair>(m, "attributes_vp")
		.def("name", &AttributesPair::name)
		.def("value", &AttributesPair::value)
		.def("__repr__", &AttributesPair::to_string)
		.def("__str__", &AttributesPair::to_string);
}
