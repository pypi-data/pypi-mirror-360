#ifndef RANDOM_H
#define RANDOM_H

#include <cmath>
#include <cstdint>
#include <limits>
#include <memory>
#include <random>

namespace lotto {

/**
 * Random number generator
 *
 * Allows sampling of random integers and reals.
 *
 * To use the Mersenne Twister 19937 generator (64-bit),
 * seeded by std::random_device.  (default):
 * \code
 * lotto::RandomGenerator random_generator;
 * \endcode
 *
 * To use another engine, seeded by std::random_device:
 * \code
 * lotto::RandomGeneratorT<EngineType> random_generator();
 * \endcode
 *
 * To use another engine, seeded any method:
 * \code
 * auto engine = std::make_shared<EngineType>();
 * engine->seed(...);
 * lotto::RandomGeneratorT<EngineType> random_generator(engine);
 * \endcode
 */
template <typename EngineType = std::mt19937_64>
class RandomGeneratorT {
 public:
  typedef typename EngineType::result_type UIntType;
  typedef double RealType;

  /// Constructor, automatically construct and seed from random device if
  /// engine is empty
  RandomGeneratorT(
      std::shared_ptr<EngineType> engine = std::shared_ptr<EngineType>())
      : engine(engine),
        // std::uniform_real_distribution provides the interval [a, b)
        // so to obtain (a, b] we must shift the endpoints to the next
        // representable values
        unit_interval_distribution(
            std::nextafter(0.0, std::numeric_limits<RealType>::max()),
            std::nextafter(1.0, std::numeric_limits<RealType>::max())) {
    if (this->engine == nullptr) {
      this->engine = std::make_shared<EngineType>();
      std::random_device device;
      reseed_generator(device());
    }
  }

  /// Returns a random integer from the closed interval [0, maximum_value]
  UIntType sample_integer_range(UIntType maximum_value) {
    return std::uniform_int_distribution<UIntType>(0, maximum_value)(*engine);
  }

  /// Returns a random real from the half-open unit interval (0, 1]
  RealType sample_unit_interval() {
    return unit_interval_distribution(*engine);
  }

  /// Returns the value used to seed the generator
  UIntType get_seed() const { return seed; }

  /// Reseeds the generator
  void reseed_generator(UIntType new_seed) {
    seed = new_seed;
    engine->seed(seed);
  }

  /// Get the random number generator engine
  std::shared_ptr<EngineType> get_engine() const { return engine; }

 private:
  /// Random number generator engine
  std::shared_ptr<EngineType> engine;

  /// Seed used for generator engine
  UIntType seed;

  /// Half-open unit interval distribution (0, 1]
  std::uniform_real_distribution<RealType> unit_interval_distribution;
};

typedef RandomGeneratorT<> RandomGenerator;

}  // namespace lotto

#endif
