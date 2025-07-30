#ifndef CASM_clexulator_SparseCoefficients
#define CASM_clexulator_SparseCoefficients

#include <vector>

#include "casm/global/eigen.hh"

namespace CASM {
namespace clexulator {

/// \brief Container for non-zero expansion coefficients
struct SparseCoefficients {
  /// \brief Indices of basis functions with non-zero coefficients to evaluate
  std::vector<unsigned int> index;

  /// \brief Expansion coefficients, for the basis functions specified by
  /// `index`
  std::vector<double> value;
};

/// \brief Evaluate cluster expansion value given coefficients and correlations
double operator*(SparseCoefficients const &coeff,
                 Eigen::VectorXd const &correlations);

/// \brief Evaluate cluster expansion value given coefficients and correlations
double operator*(SparseCoefficients const &coeff,
                 double const *correlations_begin);

// -- Inline definitions --

/// \brief Evaluate cluster expansion value given coefficients and correlations
inline double operator*(SparseCoefficients const &coeff,
                        Eigen::VectorXd const &correlations) {
  return coeff * correlations.data();
}

/// \brief Evaluate cluster expansion value given coefficients and correlations
inline double operator*(SparseCoefficients const &coeff,
                        double const *correlations_begin) {
  double result(0);
  auto index_it = coeff.index.data();
  auto index_end = index_it + coeff.index.size();
  auto value_it = coeff.value.data();
  while (index_it != index_end) {
    result += (*value_it) * (*(correlations_begin + *index_it));
    ++index_it;
    ++value_it;
  }
  return result;
}

}  // namespace clexulator
}  // namespace CASM

#endif
