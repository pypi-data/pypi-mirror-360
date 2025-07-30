#ifndef REJECTION_FREE_H
#define REJECTION_FREE_H

#include <cassert>
#include <map>
#include <memory>
#include <stdexcept>
#include <vector>

#include "event_rate_tree.hpp"
#include "event_rate_tree_impl.hpp"
#include "event_selector.hpp"

class RejectionFreeEventSelectorTest;

namespace lotto {

template <typename EventIDType>
struct GetImpactFromTable {
  GetImpactFromTable(
      std::map<EventIDType, std::vector<EventIDType>> const &_impact_table)
      : impact_table(_impact_table) {}

  std::vector<EventIDType> const &operator()(
      const EventIDType &event_id) const {
    return impact_table.at(event_id);
  }

  std::map<EventIDType, std::vector<EventIDType>> const &impact_table;
};

template <typename EventIDType>
const std::vector<EventIDType> &_validate_event_id_list(
    const std::vector<EventIDType> &event_id_list) {
  if (event_id_list.empty()) {
    std::cerr << "Warning: Event list is empty." << std::endl;
  }
  return event_id_list;
}

/*
 * Event selector implemented using rejection-free KMC algorithm
 * - For any EventIDType that can be used as a std::map key
 * - Uses a binary sum tree (log complexity) constructed using std::map and
 *   linked lists
 */
template <typename EventIDType, typename RateCalculatorType,
          typename EngineType = std::mt19937_64,
          typename GetImpactType = GetImpactFromTable<EventIDType>>
class RejectionFreeEventSelector
    : public EventSelectorBase<EventIDType, RateCalculatorType, EngineType> {
 public:
  // Construct given a rate calculator, event ID list, impact table, and random
  // number generator
  RejectionFreeEventSelector(
      const std::shared_ptr<RateCalculatorType> &rate_calculator_ptr,
      const std::vector<EventIDType> &event_id_list,
      const std::map<EventIDType, std::vector<EventIDType>> &_impact_table,
      std::shared_ptr<RandomGeneratorT<EngineType>> random_generator =
          std::shared_ptr<RandomGeneratorT<EngineType>>())
      : EventSelectorBase<EventIDType, RateCalculatorType, EngineType>(
            rate_calculator_ptr, random_generator),
        event_rate_tree(_validate_event_id_list(event_id_list),
                        this->calculate_rates(event_id_list)),
        impact_table(fill_impact_table(_impact_table, event_id_list)),
        impacted_events_ptr(nullptr),
        get_impact(impact_table) {
    if (event_rate_tree.total_rate() == 0.0) {
      std::cerr << "Warning: Total rate is zero." << std::endl;
    }
  }

  // Construct given a rate calculator, event ID list, get impact function, and
  // random number generator
  RejectionFreeEventSelector(
      const std::shared_ptr<RateCalculatorType> &rate_calculator_ptr,
      const std::vector<EventIDType> &event_id_list, GetImpactType get_impact_f,
      std::shared_ptr<RandomGeneratorT<EngineType>> random_generator =
          std::shared_ptr<RandomGeneratorT<EngineType>>())
      : EventSelectorBase<EventIDType, RateCalculatorType, EngineType>(
            rate_calculator_ptr, random_generator),
        event_rate_tree(_validate_event_id_list(event_id_list),
                        this->calculate_rates(event_id_list)),
        impact_table(),
        impacted_events_ptr(nullptr),
        get_impact(get_impact_f) {
    if (event_rate_tree.total_rate() == 0.0) {
      std::cerr << "Warning: Total rate is zero." << std::endl;
    }
  }

  // Select an event and return its ID and the time step
  std::pair<EventIDType, double> select_event() {
    // Because this function only selects events and does not process them,
    // it cannot update any rates impacted by the selected event until the next
    // call.
    update_impacted_event_rates();

    // Rates should now be updated. Calculate total rate and time step
    double _total_rate = event_rate_tree.total_rate();
    double time_step = this->calculate_time_step(_total_rate);

    // Query tree to select event
    double query_value =
        _total_rate * this->random_generator->sample_unit_interval();
    EventIDType selected_event_id = event_rate_tree.query_tree(query_value);

    // Update impacted event list and return
    set_impacted_events(selected_event_id);
    return std::make_pair(selected_event_id, time_step);
  }

  // Select an event and return its ID and the time step
  // - This version does not set the impacted events
  std::pair<EventIDType, double> only_select_event() {
    // Because this function only selects events and does not process them,
    // it cannot update any rates impacted by the selected event until the next
    // call.
    update_impacted_event_rates();

    // Rates should now be updated. Calculate total rate and time step
    double _total_rate = event_rate_tree.total_rate();
    double time_step = this->calculate_time_step(_total_rate);

    // Query tree to select event
    double query_value =
        _total_rate * this->random_generator->sample_unit_interval();
    EventIDType selected_event_id = event_rate_tree.query_tree(query_value);

    return std::make_pair(selected_event_id, time_step);
  }

  // Set the impact events pointer based on an accepted event ID
  void set_impacted_events(const EventIDType &accepted_event_id) {
    assert(impacted_events_ptr ==
           nullptr);  // pointer should be null before proceeding
    impacted_events_ptr = &get_impact(accepted_event_id);
    return;
  }

  // Return total event rate, for events in the state before `select_event` is
  // called
  double total_rate() const { return event_rate_tree.total_rate(); }

  // Get the rate of a specific event
  double get_rate(const EventIDType &event_id) const {
    return event_rate_tree.get_rate(event_id);
  }

 private:
  // Tree storing event IDs and their corresponding rates
  EventRateTree<EventIDType> event_rate_tree;

  // Lookup table indicating, for a given event that is accepted, which events'
  // rates are impacted (optional, only used if impact_table is provided to
  // the constructor)
  const std::map<EventIDType, std::vector<EventIDType>> impact_table;

  // Pointer to vector of impacted events whose rates have not been updated
  mutable const std::vector<EventIDType> *impacted_events_ptr;

  // Function object to get impacted events from the accepted event ID
  GetImpactType get_impact;

  // Update the stored rates for impacted events
  void update_impacted_event_rates() {
    if (impacted_events_ptr != nullptr) {
      for (const EventIDType &event_id : *impacted_events_ptr) {
        event_rate_tree.update_rate(event_id, this->calculate_rate(event_id));
      }
      impacted_events_ptr = nullptr;
    }
    return;
  }

  // Add missing event IDs to an impact table (with empty vectors as values)
  // and return it
  std::map<EventIDType, std::vector<EventIDType>> fill_impact_table(
      std::map<EventIDType, std::vector<EventIDType>> table_to_fill,
      std::vector<EventIDType> event_id_list) {
    for (const EventIDType &event_id : event_id_list) {
      table_to_fill[event_id];
    }
    return table_to_fill;
  }

  // Friend for testing
  friend class ::RejectionFreeEventSelectorTest;
};

/*
 * Event selector implemented using rejection-free KMC algorithm
 * - For integer EventIDType only
 * - Uses a binary sum tree (log complexity) constructed using std::vector
 */
template <typename EventIDType, typename RateCalculatorType,
          typename EngineType = std::mt19937_64,
          typename GetImpactType = GetImpactFromTable<EventIDType>>
class VectorRejectionFreeEventSelector
    : public EventSelectorBase<EventIDType, RateCalculatorType, EngineType> {
 public:
  // Construct given a rate calculator, event ID list, get impact function, and
  // random number generator
  VectorRejectionFreeEventSelector(
      const std::shared_ptr<RateCalculatorType> &rate_calculator_ptr,
      std::size_t _event_list_size, GetImpactType get_impact_f,
      std::shared_ptr<RandomGeneratorT<EngineType>> random_generator =
          std::shared_ptr<RandomGeneratorT<EngineType>>())
      : EventSelectorBase<EventIDType, RateCalculatorType, EngineType>(
            rate_calculator_ptr, random_generator),
        event_list_size(_event_list_size),
        impacted_events_ptr(nullptr),
        get_impact(get_impact_f) {
    // Construct `event_rates` data structure:
    std::size_t capacity = 1;
    event_rates.emplace_back(capacity, 0.0);
    while (capacity <= event_list_size) {
      capacity *= 2;
      event_rates.emplace_back(capacity, 0.0);
    }

    // Calculate rates:
    for (std::size_t i = 0; i < event_list_size; ++i) {
      event_rates.back()[i] = rate_calculator_ptr->calculate_rate(i);
    }

    // Sum rates:
    if (event_list_size == 0) {
      std::cerr << "Warning: Event list size is zero." << std::endl;
      return;
    }

    std::size_t curr_level = event_rates.size() - 2;
    while (true) {
      auto curr_level_it = event_rates[curr_level].begin();
      auto prev_level_it = event_rates[curr_level + 1].begin();
      auto curr_level_end = event_rates[curr_level].end();
      std::size_t i = 0;
      while (curr_level_it != curr_level_end) {
        *curr_level_it += *prev_level_it;
        ++prev_level_it;
        *curr_level_it += *prev_level_it;
        ++prev_level_it;
        ++i;
        ++curr_level_it;
      }
      if (curr_level == 0) {
        break;
      }
      --curr_level;
    }
  }

  // Select an event and return its ID and the time step
  std::pair<EventIDType, double> select_event() {
    // Because this function only selects events and does not process them,
    // it cannot update any rates impacted by the selected event until the next
    // call.
    update_impacted_event_rates();

    // Rates should now be updated. Calculate total rate and time step
    double _total_rate = this->total_rate();
    double time_step = this->calculate_time_step(_total_rate);

    // Query tree to select event
    double query_value =
        _total_rate * this->random_generator->sample_unit_interval();
    EventIDType selected_event_id = this->query_tree(query_value);

    // Update impacted event list and return
    set_impacted_events(selected_event_id);
    return std::make_pair(selected_event_id, time_step);
  }

  // Select an event and return its ID and the time step
  // - This version does not set the impacted events
  std::pair<EventIDType, double> only_select_event() {
    // Because this function only selects events and does not process them,
    // it cannot update any rates impacted by the selected event until the next
    // call.
    update_impacted_event_rates();

    // Rates should now be updated. Calculate total rate and time step
    double _total_rate = this->total_rate();
    double time_step = this->calculate_time_step(_total_rate);

    // Query tree to select event
    double query_value =
        _total_rate * this->random_generator->sample_unit_interval();
    EventIDType selected_event_id = this->query_tree(query_value);

    return std::make_pair(selected_event_id, time_step);
  }

  // Set the impact events pointer based on an accepted event ID
  void set_impacted_events(const EventIDType &accepted_event_id) {
    assert(impacted_events_ptr ==
           nullptr);  // pointer should be null before proceeding
    impacted_events_ptr = &get_impact(accepted_event_id);
    return;
  }

  // Return total event rate, for events in the state before `select_event` is
  // called
  double total_rate() const { return event_rates[0][0]; }

  // Get the rate of a specific event
  double get_rate(const EventIDType &event_id) const {
    return event_rates.back()[event_id];
  }

 private:
  //  // Tree storing event IDs and their corresponding rates
  //  EventRateTree<EventIDType> event_rate_tree;
  //
  //  // Lookup table indicating, for a given event that is accepted, which
  //  events'
  //  // rates are impacted (optional, only used if impact_table is provided to
  //  // the constructor)
  //  const std::map<EventIDType, std::vector<EventIDType>> impact_table;

  std::size_t event_list_size;

  // Event rates and sums
  // - event_rates[0][0] is the total rate
  // - event_rates[i][j] = event_rates[i+1][j*2] + event_rates[i+1][j*2 + 1]
  // - event_rates.back()[k] is the rate of EventID==k
  // - event_rates.back()[k] == 0.0 for k >= event_list_size
  std::vector<std::vector<double>> event_rates;

  // Pointer to vector of impacted events whose rates have not been updated
  mutable const std::vector<EventIDType> *impacted_events_ptr;

  // Function object to get impacted events from the accepted event ID
  GetImpactType get_impact;

  // Update `event_rates` for a given event ID
  void update(const EventIDType &event_id, double new_rate) {
    // If the rate has not changed, just return
    std::size_t curr_level = event_rates.size() - 1;
    std::size_t index = event_id;
    auto &existing_rate = event_rates[curr_level][index];
    if (existing_rate == new_rate) {
      return;
    }

    // If the rate has changed, set the new rate
    existing_rate = new_rate;

    // Update the sums
    if (event_rates.size() == 1) {
      return;
    }

    std::size_t prev_level = curr_level;
    --curr_level;
    index /= 2;
    std::size_t prev_index = index * 2;
    while (true) {
      event_rates[curr_level][index] = event_rates[prev_level][prev_index] +
                                       event_rates[prev_level][prev_index + 1];
      index /= 2;
      prev_index = index * 2;
      if (curr_level == 0) {
        break;
      }
      --curr_level;
      --prev_level;
    }
  }

  std::size_t query_tree(double query_value) const {
    assert(query_value > 0.0);  // query value must be positive
    assert(query_value <=
           total_rate());  // query value cannot exceed total rate

    std::size_t index = 0;
    for (std::size_t level = 1; level < event_rates.size(); ++level) {
      index *= 2;
      double const &first = event_rates[level][index];
      if (query_value > first) {
        // choose `second` ({level, index + 1}),
        // otherwise choose `first` ({level, index})
        query_value -= first;
        index += 1;
      }
    }
    return index;
  }

  // Update the stored rates for impacted events
  void update_impacted_event_rates() {
    if (impacted_events_ptr != nullptr) {
      for (const EventIDType &event_id : *impacted_events_ptr) {
        this->update(event_id, this->calculate_rate(event_id));
      }
      impacted_events_ptr = nullptr;
    }
    return;
  }

  void check_sum_tree() const {
    // std::cout << "Checking sum tree... n_levels=" << event_rates.size()
    //           << std::endl;
    for (std::size_t i = 0; i < event_rates.size(); ++i) {
      double sum = 0.0;
      for (std::size_t j = 0; j < event_rates[i].size(); ++j) {
        if (i + 1 < event_rates.size() &&
            event_rates[i + 1][2 * j] + event_rates[i + 1][2 * j + 1] !=
                event_rates[i][j]) {
          std::cout << "- ** level=" << i << " j=" << j
                    << " value=" << event_rates[i][j] << " ** " << std::endl;
          std::cout << "- ** level=" << i + 1 << " j=" << 2 * j
                    << " value=" << event_rates[i + 1][2 * j] << " ** "
                    << std::endl;
          std::cout << "- ** level=" << i + 1 << " j=" << 2 * j + 1
                    << " value=" << event_rates[i + 1][2 * j + 2] << " ** "
                    << std::endl;
          std::cout << "- ** sum="
                    << event_rates[i + 1][2 * j] + event_rates[i + 1][2 * j + 1]
                    << " ** " << std::endl;
          throw std::runtime_error(
              "Error in sum tree construction: invalid sum.");
        }
        // std::cout << "- level=" << i << " j=" << j
        //           << " value=" << event_rates[i][j] << std::endl;
        sum += event_rates[i][j];
      }
      // std::cout << "- level=" << i << " sum=" << sum << std::endl;
    }
    return;
  }
};

/*
 * Event selector implemented using rejection-free KMC algorithm
 * - For integer EventIDType only
 * - Uses a direct sum (linear complexity) of the event rates
 */
template <typename EventIDType, typename RateCalculatorType,
          typename EngineType = std::mt19937_64,
          typename GetImpactType = GetImpactFromTable<EventIDType>>
class DirectSumRejectionFreeEventSelector
    : public EventSelectorBase<EventIDType, RateCalculatorType, EngineType> {
 public:
  // Construct given a rate calculator, event ID list, get impact function, and
  // random number generator
  DirectSumRejectionFreeEventSelector(
      const std::shared_ptr<RateCalculatorType> &rate_calculator_ptr,
      std::size_t _event_list_size, GetImpactType get_impact_f,
      std::shared_ptr<RandomGeneratorT<EngineType>> random_generator =
          std::shared_ptr<RandomGeneratorT<EngineType>>())
      : EventSelectorBase<EventIDType, RateCalculatorType, EngineType>(
            rate_calculator_ptr, random_generator),
        event_list_size(_event_list_size),
        event_rates(event_list_size, 0.0),
        cumulative_rate(event_list_size, 0.0),
        impacted_events_ptr(nullptr),
        get_impact(get_impact_f) {
    if (event_list_size == 0) {
      std::cerr << "Warning: Event list size is zero." << std::endl;
      return;
    }

    // Calculate rates:
    for (std::size_t i = 0; i < event_list_size; ++i) {
      event_rates[i] = rate_calculator_ptr->calculate_rate(i);
    }

    // Update cumulative rate:
    update_cumulative_rate();
  }

  // Select an event and return its ID and the time step
  std::pair<EventIDType, double> select_event() {
    // Because this function only selects events and does not process them,
    // it cannot update any rates impacted by the selected event until the next
    // call.
    update_impacted_event_rates();

    // Rates should now be updated. Calculate total rate and time step
    double _total_rate = this->total_rate();
    double time_step = this->calculate_time_step(_total_rate);

    // Query tree to select event
    double query_value =
        _total_rate * this->random_generator->sample_unit_interval();
    EventIDType selected_event_id = this->query_list(query_value);

    // Update impacted event list and return
    set_impacted_events(selected_event_id);
    return std::make_pair(selected_event_id, time_step);
  }

  // Select an event and return its ID and the time step
  // - This version does not set the impacted events
  std::pair<EventIDType, double> only_select_event() {
    // Because this function only selects events and does not process them,
    // it cannot update any rates impacted by the selected event until the next
    // call.
    update_impacted_event_rates();

    // Rates should now be updated. Calculate total rate and time step
    double _total_rate = this->total_rate();
    double time_step = this->calculate_time_step(_total_rate);

    // Query tree to select event
    double query_value =
        _total_rate * this->random_generator->sample_unit_interval();
    EventIDType selected_event_id = this->query_list(query_value);

    return std::make_pair(selected_event_id, time_step);
  }

  // Set the impact events pointer based on an accepted event ID
  void set_impacted_events(const EventIDType &accepted_event_id) {
    assert(impacted_events_ptr ==
           nullptr);  // pointer should be null before proceeding
    impacted_events_ptr = &get_impact(accepted_event_id);
    return;
  }

  // Return total event rate, for events in the state before `select_event` is
  // called
  double total_rate() const { return cumulative_rate.back(); }

  // Get the rate of a specific event
  double get_rate(const EventIDType &event_id) const {
    return event_rates[event_id];
  }

 private:
  // Total number of events:
  std::size_t event_list_size;

  // Event rates:
  std::vector<double> event_rates;

  // Cumulative rate: sum of all rates up to and including event i
  std::vector<double> cumulative_rate;

  // Pointer to vector of impacted events whose rates have not been updated
  mutable const std::vector<EventIDType> *impacted_events_ptr;

  // Function object to get impacted events from the accepted event ID
  GetImpactType get_impact;

  // Update `event_rates` for a given event ID
  void update(const EventIDType &event_id, double new_rate) {
    event_rates[event_id] = new_rate;
  }

  // Query the cumulative_rate list to select an event.
  //
  // - The query value should be in the range (0, total_rate]
  // - Select event i, such that R(i-1) < u <= R(i), where u is the query value
  //   and R(i) is the cumulative rate of all events up to and including event
  //   i.
  //
  std::size_t query_list(double query_value) const {
    assert(query_value > 0.0);  // query value must be positive
    assert(query_value <=
           total_rate());  // query value cannot exceed total rate

    for (std::size_t index = 0; index < event_rates.size(); ++index) {
      if (query_value <= cumulative_rate[index]) {
        return index;
      }
    }

    // Should never reach this point
    throw std::runtime_error(
        "Error in query_tree: query value exceeds total rate.");
  }

  // Update the stored rates for impacted events
  void update_impacted_event_rates() {
    if (impacted_events_ptr != nullptr) {
      for (const EventIDType &event_id : *impacted_events_ptr) {
        this->update(event_id, this->calculate_rate(event_id));
      }
      // Update cumulative rate:
      update_cumulative_rate();

      impacted_events_ptr = nullptr;
    }
    return;
  }

  // Update the cumulative rate list
  void update_cumulative_rate() {
    double sum = 0.0;
    for (std::size_t i = 0; i < event_list_size; ++i) {
      sum += event_rates[i];
      cumulative_rate[i] = sum;
    }
    return;
  }
};

}  // namespace lotto

#endif
