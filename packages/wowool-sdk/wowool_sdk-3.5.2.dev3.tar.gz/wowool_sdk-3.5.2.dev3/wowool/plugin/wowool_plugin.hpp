#pragma once
// ----------------------------------------------------------------------------------
// Copyright (c) 2020 Wowool, All Rights Reserved.
// NOTICE:  All information contained herein is, and remains the property of Wowool.
// ----------------------------------------------------------------------------------
#include <functional>
#include <pybind11/pybind11.h>
#include <string>
#include "plugins/api.hpp"
#include "wowool/analyzer/tir.hpp"
#include "wowool/common/c/plugin.h"
#include "wowool/common/exception.hpp"
#include "wowool/common/options.hpp"

namespace py = pybind11;
using namespace wowool;

namespace wow {
namespace python {

	typedef std::function<bool(plugin_Annotation const *)>
		filter_annotation_filter_type;

	struct AttributesPair
	{
		AttributesPair();

		AttributesPair(void const *n, void *v);

		std::string name() const { return name_; }
		std::string value() const { return value_; }

		std::string to_string() const;

		std::string name_;
		std::string value_;
	};

	struct python_object_attributes
		: public std::vector<AttributesPair>
	{
	public:
		// typedef std::vector<AttributesPair> container_type;
		using std::vector<AttributesPair>::begin;
		using std::vector<AttributesPair>::end;
		using std::vector<AttributesPair>::size;

		python_object_attributes();
		python_object_attributes(plugin_Annotation const *cncpt_);

		bool has(std::string const &key) const;
		bool pybool() const;

		std::string to_string() const;
		plugin_Annotation const *cncpt;
	};

	// object that represent a annotation range in python.
	struct python_object_range
	{
		python_object_range();
		python_object_range(plugin_Annotation const *cncpt);
		python_object_range(plugin_Annotation const *begin_, plugin_Annotation const *end_);

		~python_object_range();

		void remove_concept();

		int get_begin_offset() const;

		int get_end_offset() const;

		std::string get_uri() const;

		std::vector<python_object_range> find_with_filter(filter_annotation_filter_type const &filter);

		python_object_attributes attributes();

		bool has(std::string const &key) const;

		std::string get_attribute(std::string const &key) const;

		bool add_attribute(std::string const &key, std::string const &value);

		// filter a range of annotations.

		std::vector<python_object_range> regex(std::string const &uri);

		python_object_range add_concept(std::string const &uri);

		// implements the python calls capture["person" ]
		// argument is a string
		std::vector<python_object_range> get_item(std::string const &uri);

		py::object find_one(std::string const &uri);
		// implements the python calls capture.person
		// argument is a string
		py::object get_attr(std::string const &uri);
		// implements the python calls capture["person","boss", .... ]
		// argument is a tuple (a,b,c,...)
		std::vector<python_object_range> get_item(py::tuple const &elements);
		std::vector<python_object_range> find(std::string const &uri);

		std::vector<int> find_int(std::string const &uri);

		std::string repr() const;

		py::list tokens();

		std::string str();

		std::string literal(std::string const delemiter = " ");
		std::string canonical(std::string const delemiter = " ");
		std::string stem(std::string const delemiter = " ");
		std::string lemma(std::string const delemiter = " ");

		void set_uri(std::string const &uri);

		bool pybool() const;

		mutable plugin_Annotation const *begin = nullptr;
		mutable plugin_Annotation const *end = nullptr;
	};

	/////////////////////////////////////////////////////////////////////////////////////////////

	struct python_token
	{
		python_token();
		python_token(plugin_Annotation const *token_);
		bool has_property(std::string const &prop) const;
		std::string head() const;
		std::string pos(int idx = 0) const;
		std::string stem(int idx = 0) const;
		std::string lemma(int idx = 0) const;
		std::string str() const;
		plugin_Annotation const *token;
	};

	// the match context api.
	struct python_object_match_context
	{
		python_object_match_context();
		python_object_range capture();
		python_object_range rule();
		python_object_range sentence();
		python_object_range make_range(python_object_range begin_, python_object_range end_);
		const std::string property(std::string const &key);
		std::string to_string();
		std::string msg;
		c_context context;
	};

}
} // namespace wow::python
