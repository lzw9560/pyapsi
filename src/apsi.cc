#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/chrono.h>
#include "sender/apsi/sender_db.h"
#include "receiver/apsi/receiver.h"

namespace py = pybind11;

using namespace std;
using namespace apsi;
using namespace apsi::sender;

// APSI
#include "apsi/psi_params.h"
#include "apsi/psi_params_generated.h"
#include "apsi/version.h"
#include "apsi/util/utils.h"

// SEAL
#include "seal/context.h"
#include "seal/modulus.h"
#include "seal/util/common.h"
#include "seal/util/defines.h"

// JSON
#include "json/json.h"

#include <sstream>
#include <fstream>

vector<Item> CreateItems(){
    vector<Item> sender_items;
    for (size_t i = 0; i < 100; i++) {
        sender_items.push_back({ i + 1, i + 1 });
    }

    return sender_items;
}

void TestSend(const PSIParams &params, size_t sender_size){
    vector<Item> sender_items;
    for (size_t i = 0; i < sender_size; i++) {
        sender_items.push_back({ i + 1, i + 1 });
    }

    auto sender_db = make_shared<SenderDB>(params, 0);
    auto oprf_key = sender_db->get_oprf_key();

    sender_db->set_data(sender_items);

    auto seal_context = sender_db->get_seal_context();
}

//std::string save_to_string(const SenderDB &db) {
//    stringstream ss;
//    std::string out;
//    auto save_size = db.save(ss);
//    std::cout << save_size << "\n";
//    out = ss.str();
//    return out;
//}

std::size_t save_to_file(const SenderDB &db, const string &file_name) {
    ofstream fs;
    fs.open(file_name);
    auto save_size = db.save(fs);
    return save_size;
}

PYBIND11_MAKE_OPAQUE(std::vector<Item>);

PYBIND11_MODULE(pyapsi, m) {
    m.doc() = "pybind11 pyapsi plugin";  // Optional module docstring

    py::bind_vector<std::vector<Item>>(m, "VectorItem");

    py::class_<Item>(m, "Item")
//        .def("hash_to_value", &Item::hash_to_value)
        .def("to_bitstring", &Item::to_bitstring);

    py::class_<PSIParams>(m, "PSIParams")
        .def("save", &PSIParams::save, "Writes the PSIParams to a stream.")
        .def("Load", py::overload_cast<std::istream &>(&PSIParams::Load), "Reads the PSIParams from a stream.")
        .def("Load", py::overload_cast<const std::string &>(&PSIParams::Load), "Reads the PSIParams from a JSON string.");

    py::class_<SenderDB>(m, "SenderDB")
        .def(py::init<PSIParams, std::size_t, std::size_t, bool>(), py::arg("params"), py::arg("label_byte_count") = 0, py::arg("nonce_byte_count") = 16, py::arg("compressed") = true, "Creates a new SenderDB.")
        .def(py::init<PSIParams, oprf::OPRFKey, std::size_t, std::size_t, bool>(), py::arg("params"), py::arg("oprf_key"), py::arg("label_byte_count") = 0, py::arg("nonce_byte_count") = 16, py::arg("compressed") = true, "Creates a new SenderDB.")
//   TODO     .def(py::init<SenderDB &&>(), "Creates a new SenderDB by moving from an existing one.")
//       .def(py::init<SenderDB >(), py::arg("source"), "Creates a new SenderDB by moving from an existing one.")
//   TODO     .def(py::init<SenderDB &&>(), "Moves an existing SenderDB to the current one.")

        .def("clear", &SenderDB::clear, "Clears the database. Every item and label will be removed. The OPRF key is unchanged.")
        .def("is_labeled", &SenderDB::is_labeled, "Returns whether this is a labeled SenderDB.")
        .def("get_label_byte_count", &SenderDB::get_label_byte_count, "Returns the label byte count. A zero value indicates an unlabeled SenderDB.")
        .def("get_nonce_byte_count", &SenderDB::get_nonce_byte_count, "Returns the nonce byte count used for encrypting labels.")
        .def("is_compressed", &SenderDB::is_compressed, "Indicates whether SEAL plaintexts are compressed in memory.")
        .def("is_stripped", &SenderDB::is_stripped, "Indicates whether the SenderDB has been stripped of all information not needed for serving a query.")
//        .def("insert_or_assign", static_cast<void (Sender_db::*)(const std::vector<std::pair<Item, Label>> &)> (&Sender_db::insert_or_assign), "Inserts the given data into the database. This function can be used only on a labeled SenderDB instance. If an item already exists in the database, its label is overwritten with the new label.")
//        .def("insert_or_assign", static_cast<void (Sender_db::*)(const std::pair<Item, Label> &)> (&Sender_db::insert_or_assign), "Inserts the given (hashed) item-label pair into the database. This function can be used only on a labeled SenderDB instance. If the item already exists in the database, its label is overwritten with the new label.")
//        .def("insert_or_assign", static_cast<void (Sender_db::*)(const std::vector<Item> &)> (&Sender_db::insert_or_assign), "Inserts the given data into the database. This function can be used only on an unlabeled SenderDB instance.")
//        .def("insert_or_assign", static_cast<void (Sender_db::*)(const Item &)> (&Sender_db::insert_or_assign), "Inserts the given (hashed) item into the database. This function can be used only on an unlabeled SenderDB instance.")
        .def("set_data", static_cast<void (SenderDB::*)(const std::vector<std::pair<Item, Label>> &)> (&SenderDB::set_data), "Clears the database and inserts the given data. This function can be used only on a labeled SenderDB instance.")
        .def("set_data", static_cast<void (SenderDB::*)(const std::vector<Item> &)> (&SenderDB::set_data), "Clears the database and inserts the given data. This function can be used only on an unlabeled SenderDB instance.")
        .def("has_item", &SenderDB::has_item, "")
        .def("get_label", &SenderDB::get_label, "")
        .def("get_params", &SenderDB::get_params, "")
        .def("get_crypto_context", &SenderDB::get_crypto_context, "")
        .def("get_seal_context", &SenderDB::get_seal_context, "")
        .def("get_hashed_items", &SenderDB::get_hashed_items, "")
        .def("get_item_count", &SenderDB::get_item_count, "")
        .def("get_packing_rate", &SenderDB::get_packing_rate, "")
        .def("save", &SenderDB::save, "")
        .def("Load", &SenderDB::Load, "")
        ;

    m.def("CreateItems", &CreateItems);
    m.def("TestSend", &TestSend);
//    m.def("save_to_string", &save_to_string);
//    m.def("save_to_file", &save_to_file, py::arg("file_name"));
    m.def("save_to_file", &save_to_file);
}