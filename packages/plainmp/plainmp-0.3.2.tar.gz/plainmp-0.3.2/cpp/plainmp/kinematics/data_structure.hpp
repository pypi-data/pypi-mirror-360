/*
 * plainmp - library for fast motion planning
 *
 * Copyright (C) 2024 Hirokazu Ishida
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

#include <cstdint>
#include <vector>

namespace plainmp::kinematics {

template <class DataT>
class SizedCache {
 public:
  explicit SizedCache(size_t cache_size)
      : cache_size_(cache_size),
        data_(std::vector<DataT>(cache_size)),
        cache_predicate_vector_(std::vector<std::uint8_t>(cache_size, 0)) {}

  SizedCache() : SizedCache(0) {}

  inline void set_cache(size_t id, const DataT& data) {
    cache_predicate_vector_[id] = 1;
    data_[id] = data;
  }

  inline bool is_cached(size_t id) const {
    return (cache_predicate_vector_[id] == 1);
  }

  void extend() {
    cache_size_++;
    data_.push_back(DataT());
    cache_predicate_vector_.push_back(0);
    this->clear();
  }

  inline void clear() {
    std::fill(cache_predicate_vector_.begin(), cache_predicate_vector_.end(),
              0);
  }

  int cache_size_;
  std::vector<DataT> data_;
  // std::vector<bool> is not good for indexing
  std::vector<std::uint8_t> cache_predicate_vector_;
};

template <class ElementT>
class SizedStack {
 public:
  SizedStack() : SizedStack(0) {}
  SizedStack(size_t max_stack_size)
      : data_(std::vector<ElementT>(max_stack_size)), current_idx_(0) {}

  inline size_t size() const { return current_idx_; }
  inline bool empty() const { return current_idx_ == 0; }
  inline void reset() { current_idx_ = 0; }
  inline void push(const ElementT& elem) {
    data_[current_idx_] = elem;
    current_idx_++;
  }
  inline ElementT& top() const {
    return const_cast<ElementT&>(data_[current_idx_ - 1]);
  }
  inline void pop() { current_idx_--; }
  void extend() { data_.push_back(ElementT()); }

 private:
  std::vector<ElementT> data_;
  size_t current_idx_;
};

}  // namespace plainmp::kinematics
