//////////////////////////////////////
// Warning Do not move this headers.
// Otherwise MSVC can not compile the stuff
/////////////////////////////////////////////////////////////////
#define WITH_THREAD
#include <Python.h>
#include <iostream>
#include <mutex>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <thread>
#include <variant>
#include <vector>
#include "wowool/analyzer/analyzer.hpp"
#include "wowool/analyzer/options.hpp"
#include "wowool/common/exception.hpp"
#include "wowool/common/logging.hpp"
#include "wowool/common/options.hpp"
#include "wowool/common/version.hpp"
#include "wowool/domain/domain.hpp"
#include "wowool/engine/engine.hpp"
#include "wowool/filter/filter.hpp"
#include "wowool/language_identifier/language_identifier.hpp"
#if !defined(WIN32)
	#include <signal.h>
#else
	#include <thread>
	#include <windows.h>
#endif
namespace py = pybind11;

//#define DEBUG_WOW_THREADS

#define TIR_WLOG_COMPILER 0x1000

std::mutex global_python_mutex;
#define PYTHON_LOCK std::lock_guard<std::mutex> guard(global_python_mutex);

bool get_environment_bool(std::string const &env_id, bool default_value)
{
	char const *value_ptr = std::getenv(env_id.c_str());
	if (value_ptr)
	{
		std::string value(value_ptr);
		return value == "true" or value == "True";
	}
	return default_value;
}

bool lock_gil = get_environment_bool("WOWOOL_LOCK_GIL", false);

namespace detail {
	struct DoNotExecFirstTime
	{
		mutable bool initial = true;

		template<typename Functor>
		void operator()(Functor functor) const
		{
			if (!initial)
			{
				functor();
			}
			else
				initial = false;
		}

		void reset() { initial = true; }
	};

} // namespace detail

std::ostream &print_string_map(std::ostream &out, wowool::common::Options const &options)
{
	for (auto const &option : options)
	{
		out << option.first << ":" << option.second << ",";
	}
	return out;
}

namespace tir {
namespace pywowool {

	class exception_t : public std::exception
	{
	private:
		std::string message;
		std::string extraData;

	public:
		exception_t(std::string message_, std::string extraData_)
			: message(message_), extraData(extraData_) {}
		// TODO: declare this nothrow
		~exception_t() throw() {}
		const char *what() const throw() { return message.c_str(); }
		std::string getMessage() { return message; }
		std::string getExtraData() { return extraData; }
	};

	class exception_json_t : public std::exception
	{
	private:
		std::string json_data;

	public:
		exception_json_t(std::string json_data_)
			: json_data(json_data_) {}
		// TODO: declare this nothrow
		~exception_json_t() throw() {}
		const char *what() const throw() { return json_data.c_str(); }
	};

	void translate(exception_json_t const &e)
	{
		PyErr_SetString(PyExc_RuntimeError, e.what());
	}
	void translate(exception_t const &e)
	{
		PyErr_SetString(PyExc_RuntimeError, e.what());
	}

	wowool::common::Options convert_py_2_api_options(py::dict const &kwargs)
	{
		wowool::common::Options options;
		for (auto const &item : kwargs)
		{
			options.emplace(py::str(item.first), py::str(item.second));
		}
		return options;
	}

	std::string convert_filterset(wowool::filter::Filter const &filterset)
	{
		return filterset.info();
	}

	py::dict convert_options_2_py(wowool::common::Options const &options)
	{
		py::dict kwargs;
		for (auto const &item : options)
		{
			kwargs[py::str(item.first)] = py::str(item.second);
		}
		return kwargs;
	}

	// self.options["pytryoshka"] = "true"

	static wowool::common::Options global_shared_engine_options = {
		{std::string("language"), std::string("auto")},
		// { std::string("verbose")  , std::string("trace") },
		{std::string("pytryoshka"), std::string("true")}};

	static std::shared_ptr<wowool::engine::Engine>
		global_shared_engine; //( global_shared_engine_options );

	wowool::engine::Engine &get_default_engine(wowool::common::Options &options)
	{
		PYTHON_LOCK

		if (!global_shared_engine)
		{
			wowool::engine::Engine *global_wowool_engine = new wowool::engine::Engine(options);
			// std::cout << " !!!!!!!!!!!!!! Creating Global Engine" << global_wowool_engine << std::endl;
			global_shared_engine.reset(global_wowool_engine);
		}
		return *global_shared_engine;
	}

	class engine_t : public wowool::engine::Engine
	{
	public:
		// typedef wowool::EngineInterface type;

		typedef wowool::engine::Engine type;

		// using wowool::engine::Engine::Engine;

		// engine_t(wowool::engine::Engine const &&base)
		// 	: wowool::engine::Engine(std::move(base))
		// {
		// 	std::cout << "PLUGIN wowool::engine::Engine(wowool::engine::Engine const &&base)" << this << std::endl;
		// }

		// engine_t(wowool::engine::Engine const &&base, py::dict const &kwarg)
		// 	: wowool::engine::Engine(tir::pywowool::convert_py_2_api_options(kwarg))
		// {
		// 	std::cout << "PLUGIN wowool::engine::Engine(wowool::engine::Engine const &&base, py::dict const &kwarg)" << this << std::endl;
		// }

		// we need this one to be able to create multi_process objects.
		engine_t(py::dict const &kwarg)
			: wowool::engine::Engine(tir::pywowool::convert_py_2_api_options(kwarg))
		{
		}
	};

	class lid_t : public wowool::language_identifier::LanguageIdentifier
	{
	public:
		typedef wowool::language_identifier::LanguageIdentifier type;

		using wowool::language_identifier::LanguageIdentifier::LanguageIdentifier;

		lid_t(wowool::language_identifier::LanguageIdentifier const &&base)
			: wowool::language_identifier::LanguageIdentifier(std::move(base)) {}

		lid_t(wowool::analyzer::Engine const &engine, py::dict const &kwarg)
			: wowool::language_identifier::LanguageIdentifier(engine, tir::pywowool::convert_py_2_api_options(kwarg)) {}

		lid_t(py::dict const &kwarg)
			: wowool::language_identifier::LanguageIdentifier(tir::pywowool::get_default_engine(global_shared_engine_options), tir::pywowool::convert_py_2_api_options(kwarg)) {}
	};

	class domain_t : public wowool::domain::Domain
	{
	public:
		typedef wowool::domain::Domain type;

		using wowool::domain::Domain::Domain;

		domain_t(wowool::domain::Domain const &&base)
			: wowool::domain::Domain(std::move(base)) {}

		domain_t(wowool::analyzer::Engine const &engine, std::string const domain_descriptor, py::dict const &kwarg)
			: wowool::domain::Domain(engine, domain_descriptor, tir::pywowool::convert_py_2_api_options(kwarg)) {}

		// we need this one to be able to create multi_process objects.
		domain_t(py::dict const &kwarg)
			: wowool::domain::Domain(
				tir::pywowool::get_default_engine(global_shared_engine_options),
				kwarg["name"].cast<std::string>(),
				tir::pywowool::convert_py_2_api_options(kwarg)) {}

		// wowool::analyzer::Results process(wowool::analyzer::Results const document)
		// {
		// 	char *p = 0;
		// 	*p = 0;
		// 	std::cout << "PLUGIN domain_t::process" << std::endl;
		// 	// py::gil_scoped_release release; // Release the GIL
		// 	return (*static_cast<wowool::domain::Domain const *>(this))(document);
		// };
	};

	wowool::filter::FilterCollection string2filterset(std::string const &filter_str)
	{
		auto filter_vector = wowool::common::split(filter_str, ',');
		return wowool::filter::FilterCollection(filter_vector.begin(), filter_vector.end());
	}

	class filter_t : public wowool::filter::Filter
	{
	public:
		typedef wowool::filter::Filter type;

		using wowool::filter::Filter::Filter;

		filter_t(wowool::filter::Filter const &&base)
			: wowool::filter::Filter(std::move(base)) {}

		filter_t(wowool::filter::FilterCollection const &filterset)
			: wowool::filter::Filter(filterset), _filterset(filterset) {}

		filter_t(std::string const filterset)
			: wowool::filter::Filter(filterset), _filterset(string2filterset(filterset)) {}

		wowool::filter::FilterCollection const _filterset;
	};

	class results_t : public wowool::analyzer::Results
	{
	public:
		typedef wowool::analyzer::Results type;

		using wowool::analyzer::Results::Results;

		results_t(wowool::analyzer::Results const &&base)
			: wowool::analyzer::Results(std::move(base)) {}
	};

	class analyzer_t : public wowool::analyzer::Analyzer
	{
	public:
		typedef wowool::analyzer::Analyzer type;
		py::dict _kwargs;

		using wowool::analyzer::Analyzer::Analyzer;
		using wowool::analyzer::Analyzer::operator();

		analyzer_t(wowool::analyzer::Analyzer const &&base)
			: wowool::analyzer::Analyzer(std::move(base)) {}

		analyzer_t(wowool::analyzer::Engine const &engine, py::dict const &kwarg)
			: wowool::analyzer::Analyzer(engine, tir::pywowool::convert_py_2_api_options(kwarg)), _kwargs(kwarg) {}

		std::string process_return_string(std::string const &document, wowool::common::Options const &json_options)
		{
			std::string ret_val;
			// std::cout << "options:" ; print_string_map(std::cout , json_options);
			// std::cout << std::endl;
			auto results = (*this)(document, json_options);
			return results.to_json();
		}
	};

	std::string pipeline_expand(std::string const &pipeline, std::string const &paths_str, bool file_access, bool allow_dev_versions, std::string const &pipeline_language)
	{
		try
		{
			std::vector<std::string> paths = wowool::common::split(paths_str, ',');
			return wowool::engine::expand_pipeline(pipeline, paths, file_access, allow_dev_versions, pipeline_language);
		} catch (wowool::common::JsonException const &ex)
		{
			throw exception_json_t(ex.what());
		}
	}

	bool is_valid_version_format(std::string const &version)
	{
		return wowool::common::is_valid_version_format(version);
	}

	std::string get_domain_info(std::string const domains_str)
	{
		std::vector<std::string> all_groups;
		std::vector<std::string> domains = wowool::common::split(domains_str, ',');
		std::stringstream json;
		try
		{
			for (auto const &domain_descriptor : domains)
			{
				std::vector<std::string> groups;
				std::string domain = domain_descriptor;
				wowool::domain::get_domain_concepts(domain, groups);
				std::copy(groups.begin(), groups.end(), std::back_inserter(all_groups));
			}
		} catch (std::exception const &ex)
		{
			throw exception_t(ex.what(), "");
		}

		if (!all_groups.empty())
		{
			json << "[";
			detail::DoNotExecFirstTime dneft;
			for (auto const &concept : all_groups)
			{
				if (concept.empty())
					continue;

				dneft([&json]() { json << ","; });
				json << "\"" << concept << "\"";
			}
			json << "]";
			return json.str();
		}
		else
		{
			json << "[]";
		}
		return json.str();
	}

	void print_log_message(unsigned short id, char const *msg)
	{
		std::cout << msg << std::endl;
	}

	std::string compile_domain(std::string const domain_descriptor, py::dict const &kwargs)
	{
		try
		{
			auto options = convert_py_2_api_options(kwargs);
			return wowool::domain::compile_domain(options);
		} catch (wowool::common::Exception &ex)
		{
			throw exception_t(ex.what(), "");
		} catch (std::exception const &e)
		{
			throw exception_t(e.what(), "");
		}
	}

	struct options_t
	{
		static const std::string language;
	};

	const std::string options_t::language = wowool::analyzer::option::language;

	auto __exit__callback = []() {
		PYTHON_LOCK
		global_shared_engine.reset();
	};

	struct PyLog
	{
		std::function<void(unsigned short, const char *)> logit;

		PyLog(std::function<void(unsigned short, const char *)> logit_)
			: logit(logit_) {}
	};

	std::function<void(int, std::string)> pylogit;

	void global_logger_fn(unsigned short id, const char *msg)
	{
		if (pylogit)
		{
			pylogit(id, std::string(msg));
		}
	}

	void add_logger(unsigned short id, std::string level, const std::function<void(int, std::string)> logit)
	{
		pylogit = logit;
		wowool::logging::add_logger(id, level, global_logger_fn);
	}

	void unset_logger() { pylogit = nullptr; }

}
} // namespace tir::pywowool

// clang-format off

std::variant<py::none, py::object> make_py_range(plugin_Annotation * concept_internal_ptr)
{
	if (concept_internal_ptr == 0)
	{
		return py::none();
	}
	py::module plugin = py::module::import("wowool.package.lib.wowool_plugin");
	auto annotation_range =  plugin.attr("annotation_range");
	return annotation_range(concept_internal_ptr);
}

PYBIND11_MODULE(_wowool_sdk, m)
{

    m.add_object("_cleanup", py::capsule(tir::pywowool::__exit__callback));
    m.def("get_domain_info", tir::pywowool::get_domain_info);
    m.def("pipeline_expand", tir::pywowool::pipeline_expand);
    m.def("is_valid_version_format", tir::pywowool::is_valid_version_format);
    m.def("compile_domain", tir::pywowool::compile_domain);
    m.def("add_logger", tir::pywowool::add_logger);
    m.def("unset_logger", tir::pywowool::unset_logger);

    py::register_exception<tir::pywowool::exception_t>(m, "TirException");
    py::register_exception<tir::pywowool::exception_json_t>(m, "TirJsonException");

    //------------------------------------------------------------------------------------------
    // Engine Object
    //------------------------------------------------------------------------------------------
    py::class_<wowool::engine::Engine, tir::pywowool::engine_t>(m, "engine")
        .def(py::init([](py::dict const& kwargs) {
			wowool::engine::Engine * engine = new wowool::engine::Engine(tir::pywowool::convert_py_2_api_options(kwargs));
			return engine;
        }))
        .def("property", [](wowool::engine::Engine const& self, std::string const& prop) {
            return wowool::engine::get_engine_property(&self, prop.c_str());
        })
        .def("purge", [](wowool::engine::Engine& self, std::string const& purge_descriptor) {
            return self.purge(purge_descriptor);
        })
        .def("info", [](wowool::engine::Engine& self) {
            return self.info();
        })
        .def("languages", [](wowool::engine::Engine& self) {
            return self.languages();
        })
        .def("release_domain", [](wowool::engine::Engine& self, std::string const& domain_descriptor) {
            return self.release_domain(domain_descriptor);
        })
        .def("__getstate__", [](wowool::engine::Engine const& self) {
            py::dict kwargs = tir::pywowool::convert_options_2_py(self.options);
            return kwargs;
        })
        .def("__setstate__", [](py::object self, py::dict kwargs) {
			// std::cout << "PLUGIN __setstate__ wowool::engine::Engine(py::dict const& kwargs)" << std::endl;
            auto& p = self.cast<tir::pywowool::engine_t&>();
            new (&p) tir::pywowool::engine_t(kwargs);
        })
    ;

    //------------------------------------------------------------------------------------------
    // Language Identification
    //------------------------------------------------------------------------------------------
    py::class_<wowool::language_identifier::LanguageIdentifier, tir::pywowool::lid_t>(m, "lid")
        .def(py::init([](tir::pywowool::engine_t const& eng, py::dict const& kwargs) {
            return new wowool::language_identifier::LanguageIdentifier(eng, tir::pywowool::convert_py_2_api_options(kwargs));
        }))
        .def("language_identification_section", [](wowool::language_identifier::LanguageIdentifier const& self, std::string const& doc) {
            return self.language_identification_section(doc);
        })
        .def("language_identification", [](wowool::language_identifier::LanguageIdentifier const& self, std::string const& doc) {
            return self.language_identification(doc);
        })
		.def("__getstate__", [](wowool::language_identifier::LanguageIdentifier const& self) {
            py::dict kwargs = tir::pywowool::convert_options_2_py(self.options);
            return kwargs;
        })
        .def("__setstate__", [](py::object self, py::dict kwargs) {
            auto& p = self.cast<tir::pywowool::lid_t&>();
            new (&p) tir::pywowool::lid_t(kwargs);
        })
    ;

    //------------------------------------------------------------------------------------------
    // Results object
    //------------------------------------------------------------------------------------------
    py::class_<wowool::analyzer::Results, tir::pywowool::results_t>(m, "results")
        .def("to_json", [](wowool::analyzer::Results const& self) {
            return self.to_json();
        })
        .def("metadata", [](wowool::analyzer::Results const& self) {
            return self.metadata();
        })
        .def("internal_annotations", [](wowool::analyzer::Results const& self) {
            return self.internal_annotations();
        })
        .def("language", [](wowool::analyzer::Results const& self) {
            return self.language();
        })
        .def("id", [](wowool::analyzer::Results const& self) {
            return self.id();
        })
		.def("get_concept" , [&](wowool::analyzer::Results const& self, unsigned int begin_offset, unsigned int end_offset, std::string const & uri , bool unicode_offsets ) 
			-> std::variant<py::none, py::object>
		{
			plugin_Annotation * concept_internal_ptr = const_cast<wowool::analyzer::Results &>(self).get_concept(begin_offset,end_offset,uri,unicode_offsets);
			return make_py_range(concept_internal_ptr);
		})
		.def("add_concept" , [&](wowool::analyzer::Results const& self, unsigned int begin_offset, unsigned int end_offset, std::string const & uri , bool unicode_offsets )
			-> std::variant<py::none, py::object>
		{
    		plugin_Annotation * concept_internal_ptr = const_cast<wowool::analyzer::Results &>(self).add_concept(begin_offset,end_offset,uri,unicode_offsets);
			return make_py_range(concept_internal_ptr);
		})
		.def("remove_pos" , [&](wowool::analyzer::Results const& self, unsigned int begin_offset, unsigned int end_offset, std::string const & pos , bool unicode_offsets )
		{
    		const_cast<wowool::analyzer::Results &>(self).remove_pos(begin_offset,end_offset,pos,unicode_offsets);
		})
		.def("get_byte_offset" , [&](wowool::analyzer::Results const& self, unsigned int begin_offset)
		{
    		return  const_cast<wowool::analyzer::Results &>(self).get_byte_offset(begin_offset);
		})

    ;

    using namespace pybind11::literals;

    //------------------------------------------------------------------------------------------
    // Domain Object
    //------------------------------------------------------------------------------------------
    py::class_<wowool::domain::Domain, tir::pywowool::domain_t>(m, "domain")

        .def(py::init([](tir::pywowool::engine_t const& eng, std::string const filename, py::dict const& kwargs) {
			return new wowool::domain::Domain(eng, filename, tir::pywowool::convert_py_2_api_options(kwargs));
        }))
        .def("info", [](wowool::domain::Domain const& self) {
            return self.info();
        })
        .def("filename", [](wowool::domain::Domain const& self) {
            return self.filename();
        })
        .def("process", [](wowool::domain::Domain const& self, wowool::analyzer::Results const& document) {
			if (lock_gil)
			{
				return self(document);
			}
			py::gil_scoped_release release; // Release the GIL
			return self(document);
        })
		.def("__getstate__", [](wowool::domain::Domain const& self) {
            py::dict kwargs = tir::pywowool::convert_options_2_py(self.options);
            return kwargs;
        })
        .def("__setstate__", [](py::object self, py::dict kwargs) {
            assert(kwargs.find("name") != kwargs.end());
            auto& p = self.cast<tir::pywowool::domain_t&>();
            new (&p) tir::pywowool::domain_t(kwargs);
        })
    ;

    //------------------------------------------------------------------------------------------
    // Analyzer
    //------------------------------------------------------------------------------------------
    py::class_<wowool::analyzer::Analyzer, tir::pywowool::analyzer_t>(m, "analyzer")
        .def(py::init([](tir::pywowool::engine_t const& eng, py::dict const& kwargs) {
            return new wowool::analyzer::Analyzer(eng, tir::pywowool::convert_py_2_api_options(kwargs));
        }))
        .def("process", [](wowool::analyzer::Analyzer const& self, std::string const& doc, py::dict const& kwargs) {
			auto options = tir::pywowool::convert_py_2_api_options(kwargs);
			if (lock_gil)
			{
				return self.process(doc, options).to_json();
			}
			return self.process(doc, options).to_json();
        },
            "Process a given input and return a JSON string."
            "\n\nEXAMPLE"
            "\n\twith wowool() as mc:"
            "\n\t\toptions['language']='english'"
            "\n\t\tresult_data = mc.process( input_text , options )",
            "doc"_a, "options"_a)
        .def("process_results", [](wowool::analyzer::Analyzer const& self, std::string const& text, py::dict const& kwargs) {
			auto options = tir::pywowool::convert_py_2_api_options(kwargs);
			if (lock_gil)
			{
				return new wowool::analyzer::Results(self.process(text, options));
			}
			py::gil_scoped_release release; // Release the GIL
			return new wowool::analyzer::Results(self.process(text, options));
        },
            "Process a given input and return a JSON string."
            "\n\nEXAMPLE"
            "\n\twith wowool() as mc:"
            "\n\t\toptions['language']='english'"
            "\n\t\tresult_data = mc.process_results( input_text , options )",
            "doc"_a, "options"_a)        
        .def("process_document", [](wowool::analyzer::Analyzer const& self, wowool::analyzer::Results const text, py::dict const& kwargs) {
			if (lock_gil)
			{
            	return new wowool::analyzer::Results(self.process_results(text));
			}
			// py::gil_scoped_release release; // Release the GIL
			return new wowool::analyzer::Results(self.process_results(text));
        })
        .def("filename", [](wowool::analyzer::Analyzer const& self) {
            return self.filename();
        })
        .def("__getstate__", [](wowool::analyzer::Analyzer const& self) {
            py::dict kwargs = tir::pywowool::convert_options_2_py(self.options);
            return kwargs;
        })
        .def("__setstate__", [](py::object self, py::dict kwargs) {
            auto& p = self.cast<tir::pywowool::analyzer_t&>();

            new (&p) tir::pywowool::analyzer_t(tir::pywowool::get_default_engine(tir::pywowool::global_shared_engine_options) , kwargs);
        })
    ;

    //------------------------------------------------------------------------------------------
    // Filter object
    //------------------------------------------------------------------------------------------
    py::class_<wowool::filter::Filter, tir::pywowool::filter_t>(m, "filter")
        .def(py::init([](wowool::filter::FilterCollection const& filter_set) {
            return new wowool::filter::Filter(filter_set);
        }))
        .def(py::init([](py::str filter_set) {
            return new wowool::filter::Filter(filter_set);
        }))
        .def("process", [](wowool::filter::Filter const& self, wowool::analyzer::Results const& document) {
			return self(document);
        })
        .def("info", [](wowool::filter::Filter const& self) {
            return self.info();
        })
        .def("__getstate__", [](wowool::filter::Filter const& self) {
            py::str filter_set = tir::pywowool::convert_filterset(self);
            return filter_set;
        })
        .def("__setstate__", [](py::object self, py::str filter_set) {
            auto& p = self.cast<tir::pywowool::filter_t&>();
            new (&p) tir::pywowool::filter_t( filter_set );
        })
        ;
}
