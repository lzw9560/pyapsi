
// STD
#include <csignal>
#include <fstream>
#include <iostream>
#include <memory>
#include <numeric>
#include <random>
#include <sstream>

// pybind11
#include <pybind11/chrono.h>
#include <pybind11/complex.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include "receiver/apsi/receiver.h"
#include "sender/apsi/sender_db.h"

namespace py = pybind11;

using namespace std;
using namespace apsi;
using namespace apsi::sender;
using namespace apsi::receiver;

// APSI
#include <apsi/item.h>
#include <apsi/log.h>
#include <apsi/network/stream_channel.h>
#include <apsi/psi_params.h>
#include <apsi/receiver.h>
#include <apsi/sender.h>
#include <apsi/sender_db.h>
#include <apsi/thread_pool_mgr.h>

// SEAL
#include "seal/context.h"
#include "seal/modulus.h"
#include "seal/util/common.h"
#include "seal/util/defines.h"

// JSON
#include "json/json.h"

#include <typeinfo>

#define PYBIND11_DETAILED_ERROR_MESSAGES

// PYBIND11_MAKE_OPAQUE(std::vector<Item>);
// PYBIND11_MAKE_OPAQUE(std::vector<std::pair<Item, Label>>);
// PYBIND11_MAKE_OPAQUE(std::vector<std::pair<std::string, std::string>>);
// PYBIND11_MAKE_OPAQUE(std::vector<std::pair<std::uint64_t, std::uint64_t>>);

// using PairList = std::vector<std::pair<Item, Label>>;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

void sigint_handler(int param [[maybe_unused]]) {
    exit(0);
}

void set_log_level(const string& level) {
    Log::Level ll;

    if (level == "all" || level == "ALL") {
        ll = Log::Level::all;
    } else if (level == "debug" || level == "DEBUG") {
        ll = Log::Level::debug;
    } else if (level == "info" || level == "INFO") {
        ll = Log::Level::info;
    } else if (level == "warning" || level == "WARNING") {
        ll = Log::Level::warning;
    } else if (level == "error" || level == "ERROR") {
        ll = Log::Level::error;
    } else if (level == "off" || level == "OFF") {
        ll = Log::Level::off;
    } else {
        throw invalid_argument("unknown log level");
    }

    Log::SetLogLevel(ll);
}

/*
Custom StreamChannel class that uses separate stringstream objects as the
backing streams input and output and allows the buffers to be easily set (for
input) and extracted (for output).
*/
class StringStreamChannel : public network::StreamChannel {
   public:
    StringStreamChannel() : network::StreamChannel(_in_stream, _out_stream) {}

    // Sets the input buffer to hold a given string. The read/get-position is
    // set to beginning.
    void set_in_buffer(const string& str) {
        _in_stream.str(str);
        _in_stream.seekg(0);
    }

    // Returns the value in the output buffer as a string. The
    // write/put-position is set to beginning.
    string extract_out_buffer() {
        string str(_out_stream.str());
        _out_stream.seekp(0);
        return str;
    }

   private:
    stringstream _in_stream;
    stringstream _out_stream;
};

class APSIClient {
   public:
    APSIClient(string& params_json) : _receiver(PSIParams::Load(params_json)) {}

    // TODO: use std::vector<str> in conjunction with "#include
    // <pybind11/stl.h>" for auto conversion
    py::bytes oprf_request(const py::list& input_items) {
        vector<Item> receiver_items;
        for (py::handle item : input_items) {
            receiver_items.push_back(item.cast<std::string>());
        }

        _oprf_receiver = Receiver::CreateOPRFReceiver(receiver_items);
        Request request = Receiver::CreateOPRFRequest(_oprf_receiver);

        _channel.send(move(request));
        return py::bytes(_channel.extract_out_buffer());
    }

    py::bytes build_query(const string& oprf_response_string) {
        _channel.set_in_buffer(oprf_response_string);
        OPRFResponse oprf_response =
            to_oprf_response(_channel.receive_response());
        tie(_hashed_recv_items, _label_keys) =
            Receiver::ExtractHashes(oprf_response, _oprf_receiver);

        // Create query and send
        pair<Request, IndexTranslationTable> recv_query =
            _receiver.create_query(_hashed_recv_items);
        _itt = make_shared<IndexTranslationTable>(move(recv_query.second));

        _channel.send(move(recv_query.first));
        return py::bytes(_channel.extract_out_buffer());
    }

    py::list extract_unlabeled_result_from_query_response(
        const string& query_response_string) {
        signal(SIGINT, sigint_handler);

        _channel.set_in_buffer(query_response_string);
        QueryResponse query_response =
            to_query_response(_channel.receive_response());
        uint32_t package_count = query_response->package_count;

        vector<ResultPart> rps;
        while (package_count--) {
            rps.push_back(
                _channel.receive_result(_receiver.get_seal_context()));
        }

        vector<MatchRecord> query_result =
            _receiver.process_result(_label_keys, *_itt, rps);

        py::list matches;
        for (auto const& qr : query_result)
            matches.append(qr.found);
        return matches;
    }

    py::list extract_labeled_result_from_query_response(
        const string& query_response_string) {
        signal(SIGINT, sigint_handler);

        _channel.set_in_buffer(query_response_string);
        QueryResponse query_response =
            to_query_response(_channel.receive_response());
        uint32_t package_count = query_response->package_count;

        vector<ResultPart> rps;
        while (package_count--) {
            rps.push_back(
                _channel.receive_result(_receiver.get_seal_context()));
        }

        vector<MatchRecord> query_result =
            _receiver.process_result(_label_keys, *_itt, rps);

        py::list labels;
        for (auto const& qr : query_result)
            labels.append(qr.label.to_string());
        return labels;
    }

   private:
    shared_ptr<IndexTranslationTable> _itt;
    Receiver _receiver;
    oprf::OPRFReceiver _oprf_receiver = oprf::OPRFReceiver(vector<Item>());
    vector<HashedItem> _hashed_recv_items;
    vector<LabelKey> _label_keys;
    StringStreamChannel _channel;
};

class APSIServer {
   public:
    APSIServer() {}

    void init_db(string& params_json,
                 size_t label_byte_count,
                 size_t nonce_byte_count,
                 bool compressed) {
        db_label_byte_count = label_byte_count;
        auto params = PSIParams::Load(params_json);
        _db = make_shared<SenderDB>(params, label_byte_count, nonce_byte_count,
                                    compressed);
    }

    void save_db(const string& db_file_path) {
        try {
            ofstream ofs;
            ofs.open(db_file_path, ios::binary);
            _db->save(ofs);
            ofs.close();
        } catch (const exception& e) {
            throw runtime_error("Failed saving database");
        }
    }

    void load_db(const string& db_file_path) {
        try {
            ifstream ifs;
            ifs.open(db_file_path, ios::binary);
            auto [data, size] = SenderDB::Load(ifs);
            _db = make_shared<SenderDB>(move(data));
            ifs.close();
        } catch (const exception& e) {
            throw runtime_error("Failed loading database");
        }
    }

    void add_item(const string& input_item, const string& input_label) {
        Item item(input_item);

        if (input_label.length() > 0) {
            vector<unsigned char> label(input_label.begin(), input_label.end());
            _db->insert_or_assign(make_pair(item, label));
        } else {
            _db->insert_or_assign(item);
        }
    }

    void add_items(const py::list& items_with_label) {
        vector<pair<Item, Label>> items;
        for (py::handle item_label : items_with_label) {
            cout << item_label << "\n";
            pair<string, string> item_pair;
            item_pair = item_label.cast<std::pair<string, string>>();
            cout << "pair: " << item_pair.first << " : " << item_pair.second
                 << "\n";
            // item
            string input_item = item_pair.first;
            cout << "imput itam: " << input_item << "\n";
            Item item(input_item);

            // label
            std::vector<unsigned char> label(64);
            std::copy(item_pair.second.begin(), item_pair.second.end(),
                      label.data());
            cout << "label data: " << label.data() << "\n";
            // push back
            items.push_back({item, label});
        }
        _db->insert_or_assign(items);
    }

    void add_unlabeled_items(const py::list& input_items) {
        vector<Item> items;
        for (py::handle item : input_items) {
            items.push_back(item.cast<std::string>());
        }
        _db->insert_or_assign(items);
    }

    py::bytes handle_oprf_request(const string& oprf_request_string) {
        _channel.set_in_buffer(oprf_request_string);

        OPRFRequest oprf_request2 = to_oprf_request(_channel.receive_operation(
            nullptr, network::SenderOperationType::sop_oprf));
        Sender::RunOPRF(oprf_request2, _db->get_oprf_key(), _channel);
        return py::bytes(_channel.extract_out_buffer());
    }

    py::bytes handle_query(const string& query_string) {
        _channel.set_in_buffer(query_string);

        QueryRequest sender_query = to_query_request(_channel.receive_operation(
            _db->get_seal_context(), network::SenderOperationType::sop_query));
        Query query(move(sender_query), _db);

        Sender::RunQuery(query, _channel);
        return py::bytes(_channel.extract_out_buffer());
    }

   public:
    size_t db_label_byte_count;

   private:
    shared_ptr<SenderDB> _db;
    StringStreamChannel _channel;
};

std::size_t save_to_file(const SenderDB& db, const string& file_name) {
    ofstream fs;
    fs.open(file_name);
    auto save_size = db.save(fs);
    return save_size;
}

// PYBIND11_MAKE_OPAQUE(std::vector<std::pair<Item, Label>>);
PYBIND11_MAKE_OPAQUE(std::vector<std::string, std::allocator<std::string>>);

using StringList = std::vector<std::string, std::allocator<std::string>>;
PYBIND11_MODULE(pyapsi, m) {
    m.doc() = "pybind11 pyapsi plugin";  // Optional module docstring

    // py::bind_vector<std::vector<Item>>(m, "VectorItem");
    // py::bind_vector<std::vector<std::pair<std::string, std::string>>>(
    //     m, "VectorPairString");
    // py::bind_vector<std::vector<std::pair<std::uint64_t, std::uint64_t>>>(
    //     m, "VectorPairUint64T");

    py::class_<Item>(m, "Item")
        //        .def("hash_to_value", &Item::hash_to_value)
        .def("to_bitstring", &Item::to_bitstring);

    py::class_<PSIParams>(m, "PSIParams")
        .def("save", &PSIParams::save, "Writes the PSIParams to a stream.")
        .def("Load", py::overload_cast<std::istream&>(&PSIParams::Load),
             "Reads the PSIParams from a stream.")
        .def("Load", py::overload_cast<const std::string&>(&PSIParams::Load),
             "Reads the PSIParams from a JSON string.");

    py::class_<SenderDB>(m, "SenderDB")
        .def(py::init<PSIParams, std::size_t, std::size_t, bool>(),
             py::arg("params"), py::arg("label_byte_count") = 0,
             py::arg("nonce_byte_count") = 16, py::arg("compressed") = true,
             "Creates a new SenderDB.")
        .def(py::init<PSIParams, oprf::OPRFKey, std::size_t, std::size_t,
                      bool>(),
             py::arg("params"), py::arg("oprf_key"),
             py::arg("label_byte_count") = 0, py::arg("nonce_byte_count") = 16,
             py::arg("compressed") = true, "Creates a new SenderDB.")
        //   TODO     .def(py::init<SenderDB &&>(), "Creates a new SenderDB
        //   by moving from an existing one.")
        //       .def(py::init<SenderDB >(), py::arg("source"), "Creates a
        //       new SenderDB by moving from an existing one.")
        //   TODO     .def(py::init<SenderDB &&>(), "Moves an existing
        //   SenderDB to the current one.")

        .def("clear", &SenderDB::clear,
             "Clears the database. Every item and label will be removed. "
             "The "
             "OPRF key is unchanged.")
        .def("is_labeled", &SenderDB::is_labeled,
             "Returns whether this is a labeled SenderDB.")
        .def("get_label_byte_count", &SenderDB::get_label_byte_count,
             "Returns the label byte count. A zero value indicates an "
             "unlabeled SenderDB.")
        .def("get_nonce_byte_count", &SenderDB::get_nonce_byte_count,
             "Returns the nonce byte count used for encrypting labels.")
        .def("is_compressed", &SenderDB::is_compressed,
             "Indicates whether SEAL plaintexts are compressed in memory.")
        .def("is_stripped", &SenderDB::is_stripped,
             "Indicates whether the SenderDB has been stripped of all "
             "information not needed for serving a query.")
        //        .def("insert_or_assign", static_cast<void
        //        (Sender_db::*)(const std::vector<std::pair<Item, Label>>
        //        &)>
        //        (&Sender_db::insert_or_assign), "Inserts the given data
        //        into the database. This function can be used only on a
        //        labeled SenderDB instance. If an item already exists in
        //        the database, its label is overwritten with the new
        //        label.") .def("insert_or_assign", static_cast<void
        //        (Sender_db::*)(const std::pair<Item, Label> &)>
        //        (&Sender_db::insert_or_assign), "Inserts the given
        //        (hashed) item-label pair into the database. This function
        //        can be used only on a labeled SenderDB instance. If the
        //        item already exists in the database, its label is
        //        overwritten with the new label.") .def("insert_or_assign",
        //        static_cast<void (Sender_db::*)(const std::vector<Item>
        //        &)>
        //        (&Sender_db::insert_or_assign), "Inserts the given data
        //        into the database. This function can be used only on an
        //        unlabeled SenderDB instance.") .def("insert_or_assign",
        //        static_cast<void (Sender_db::*)(const Item &)>
        //        (&Sender_db::insert_or_assign), "Inserts the given
        //        (hashed) item into the database. This function can be used
        //        only on an unlabeled SenderDB instance.")
        .def("set_data",
             static_cast<void (SenderDB::*)(
                 const std::vector<std::pair<Item, Label>>&)>(
                 &SenderDB::set_data),
             "Clears the database and inserts the given data. This function "
             "can be used only on a labeled SenderDB instance.")
        .def("set_data",
             static_cast<void (SenderDB::*)(const std::vector<Item>&)>(
                 &SenderDB::set_data),
             "Clears the database and inserts the given data. This function "
             "can be used only on an unlabeled SenderDB instance.")
        .def("has_item", &SenderDB::has_item, "")
        .def("get_label", &SenderDB::get_label, "")
        .def("get_params", &SenderDB::get_params, "")
        .def("get_crypto_context", &SenderDB::get_crypto_context, "")
        .def("get_seal_context", &SenderDB::get_seal_context, "")
        .def("get_hashed_items", &SenderDB::get_hashed_items, "")
        .def("get_item_count", &SenderDB::get_item_count, "")
        .def("get_packing_rate", &SenderDB::get_packing_rate, "")
        .def("save", &SenderDB::save, "")
        .def("Load", &SenderDB::Load, "");

    m.def("save_to_file", &save_to_file);

    py::module utils = m.def_submodule("utils", "APSI related utilities.");
    utils.def("_set_log_level", &set_log_level, "Set APSI log level.");
    utils.def("_set_console_log_disabled", &Log::SetConsoleDisabled,
              "Enable or disable standard out console logging.");
    utils.def("_set_log_file", &Log::SetLogFile,
              "Set file for APSI log output.");
    utils.def("_set_thread_count", &ThreadPoolMgr::SetThreadCount,
              "Set thread count for parallelization.");
    utils.def("_get_thread_count", &ThreadPoolMgr::GetThreadCount,
              "Get thread count for parallelization.");

    py::class_<APSIServer>(m, "APSIServer")
        .def(py::init())
        .def("_init_db", &APSIServer::init_db)
        .def("_save_db", &APSIServer::save_db)
        .def("_load_db", &APSIServer::load_db)
        .def("_add_item", &APSIServer::add_item)
        .def("_add_items", &APSIServer::add_items)
        .def("_add_unlabeled_items", &APSIServer::add_unlabeled_items)
        .def("_handle_oprf_request", &APSIServer::handle_oprf_request)
        .def("_handle_query", &APSIServer::handle_query)
        // TODO: use def_property_readonly instead
        .def_readwrite("_db_label_byte_count",
                       &APSIServer::db_label_byte_count);
    py::class_<APSIClient>(m, "APSIClient")
        .def(py::init<string&>())
        .def("_oprf_request", &APSIClient::oprf_request)
        .def("_build_query", &APSIClient::build_query)
        .def("_extract_labeled_result_from_query_response",
             &APSIClient::extract_labeled_result_from_query_response)
        .def("_extract_unlabeled_result_from_query_response",
             &APSIClient::extract_unlabeled_result_from_query_response);

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
