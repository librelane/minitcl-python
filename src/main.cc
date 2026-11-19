// Copyright (C) 2026 Mohamed Gaber
// SPDX-License-Identifier: MIT
#pragma GCC visibility push(default)
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <tcl.h>

#include <string>
#include <optional>

namespace py = pybind11;

namespace minitcl {
    struct Interpreter {
        Tcl_Interp *_internal;
        Interpreter() { _internal = Tcl_CreateInterp();}
        ~Interpreter() { Tcl_DeleteInterp(_internal); _internal = nullptr; }
        
        void eval(const std::string &script) {
            int status = Tcl_EvalEx(_internal, script.c_str(), -1, TCL_EVAL_GLOBAL);
            if (status == TCL_OK) {
                return;
            }
            std::string error {Tcl_GetStringResult(_internal)};
            Tcl_ResetResult(_internal);
            throw std::runtime_error(error);
        }
        
        void eval_file(const std::string &path) {
            int status = Tcl_EvalFile(_internal, path.c_str());
            if (status == TCL_OK) {
                return;
            }
            std::string error {Tcl_GetStringResult(_internal)};
            Tcl_ResetResult(_internal);
            throw std::runtime_error(error);
        }

        std::string get_var(const std::string &name, const std::optional<std::string> &assoc_array_key) {
            auto var = Tcl_GetVar2(_internal, name.c_str(), assoc_array_key.has_value() ? assoc_array_key.value().c_str() : nullptr, TCL_LEAVE_ERR_MSG);
            if (var == NULL) {
                std::string error {Tcl_GetStringResult(_internal)};
                Tcl_ResetResult(_internal);
                throw std::runtime_error(error);
            }
            std::string result {var};
                Tcl_ResetResult(_internal);
            return result;
        }

        void set_var(const std::string &name, const std::optional<std::string> &assoc_array_key, const std::string &value) {
            auto var = Tcl_SetVar2(_internal, name.c_str(), assoc_array_key.has_value() ? assoc_array_key.value().c_str() : nullptr, value.c_str(), TCL_LEAVE_ERR_MSG);
            if (var == NULL) {
                std::string error {Tcl_GetStringResult(_internal)};
                Tcl_ResetResult(_internal);
                throw std::runtime_error(error);
            }
        }
        
        py::list parse_list(const std::string &list) {
            py::list result;

            Tcl_Size argc;
            const char **argv;
            int status = Tcl_SplitList(_internal, list.c_str(), &argc, &argv);
            if (status != TCL_OK) {
                std::string error {Tcl_GetStringResult(_internal)};
                Tcl_ResetResult(_internal);
                throw std::runtime_error(error);
            }
            for (const char **seeker = argv; *seeker != nullptr; seeker++) {
                result.append(py::str(*seeker));
            }
            Tcl_Free(argv);
            return result;
        }

        py::dict parse_dict(const std::string &list) {
            return dict_from_iterable(parse_list(list));
        }
        
        py::dict dict_from_iterable(const py::iterable iterable) {
            auto len = py::len(iterable);
            if (len % 2 != 0) {
                throw py::value_error("cannot be parsed as dict: odd number of elements");
            }
            py::dict result;
            auto iter = py::iter(iterable);
            py::handle key = py::none();
            while (iter != py::iterator::sentinel()) {
                if (key.is(py::none())) {
                    key = *iter++;
                } else {
                    result[key] = *iter++;
                    key = py::none();
                }
            }
            return result;
        }
    };
};

PYBIND11_MODULE(_minitcl, m, py::mod_gil_not_used()) {
    using namespace minitcl;

    py::class_<Interpreter, py::smart_holder>(m, "Interpreter")
        .def(py::init<>())
        .def("eval", &Interpreter::eval, py::arg("script"))
        .def("eval_file", &Interpreter::eval_file, py::arg("path"))
        .def("get_var", &Interpreter::get_var, py::arg("variable"), py::arg("assoc_array_key") = std::nullopt)
        .def("set_var", [](Interpreter &i, const std::string &variable, const std::string &value) {
            i.set_var(variable, std::nullopt, value);
        }, py::arg("variable"), py::arg("value"))
        .def("set_var", &Interpreter::set_var, py::arg("variable"), py::arg("assoc_array_key"), py::arg("value"))
        .def("parse_list", &Interpreter::parse_list, py::arg("tcl_list_value"))
        .def("parse_dict", &Interpreter::parse_dict, py::arg("tcl_dict_value"))
        .def("dict_from_iterable", &Interpreter::dict_from_iterable, py::arg("iterable"));
}
