#ifndef CASM_clexulator_ConfigDoFValues_json_io
#define CASM_clexulator_ConfigDoFValues_json_io

namespace CASM {

class jsonParser;
template <typename T>
T from_json(jsonParser const &);

namespace composition {
class CompositionConverter;
}

/// \brief Write composition::CompositionConverter to JSON
jsonParser &to_json(composition::CompositionConverter const &f,
                    jsonParser &json);

/// \brief Read composition::CompositionConverter from JSON
template <>
composition::CompositionConverter from_json<composition::CompositionConverter>(
    jsonParser const &json);

/// \brief Read composition::CompositionConverter from JSON
void from_json(composition::CompositionConverter &f, jsonParser const &json);

}  // namespace CASM

#endif
