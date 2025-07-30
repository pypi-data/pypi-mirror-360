#pragma once

#include <utility>
#include <vector>
#include <stdexcept>

namespace fort {
namespace myrmidon {
namespace priv {

template <typename Key,typename T>
class DenseMap {
public:
	typedef Key                    key_type;
	typedef std::pair<const Key,T> value_type;

	class const_iterator;

	class iterator {
	public:
		iterator(const typename std::vector<std::pair<Key,T>>::iterator & iter,
		         const typename std::vector<std::pair<Key,T>>::iterator & begin,
		         const typename std::vector<std::pair<Key,T>>::iterator & end)
			: d_iter(iter)
			, d_begin(begin)
			, d_end(end) {
		}

		iterator& operator++() {
			if ( d_iter == d_end ) {
				return *this;
			}
			do {
				++d_iter;
			}while(d_iter != d_end && d_iter->first == 0);
			return *this;
		}

		iterator& operator--() {
			if ( d_iter == d_begin ) {
				return *this;
			}
			do {
				--d_iter;
			}while(d_iter != d_begin && d_iter->first == 0);
			while( d_iter != d_end && d_iter->first == 0) {
				++d_iter;
			}
			return *this;
		}


		iterator operator++(int) {iterator retval = *this; ++(*this); return retval;}
		iterator operator--(int) {iterator retval = *this; --(*this); return retval;}

		bool operator==(const iterator & other) const {return d_iter == other.d_iter;}
		bool operator!=(const iterator & other) const {return !(*this == other);}
		DenseMap::value_type & operator*() {
			return reinterpret_cast<std::pair<const Key,T>&>(*d_iter);
		}
		DenseMap::value_type * operator->() {
			return reinterpret_cast<std::pair<const Key,T>*>(&(*d_iter));
		}
		// iterator traits
		using difference_type = long;
		using value_type = DenseMap::value_type;
		using pointer = const DenseMap::value_type*;
		using reference = const DenseMap::value_type&;
		using iterator_category = std::forward_iterator_tag;
	private :
		friend class DenseMap::const_iterator;
		typename std::vector<std::pair<Key,T>>::iterator d_iter,d_begin,d_end;
	};

	class const_iterator {
	public:
		const_iterator(const typename std::vector<std::pair<Key,T>>::const_iterator & iter,
		               const typename std::vector<std::pair<Key,T>>::const_iterator & begin,
		               const typename std::vector<std::pair<Key,T>>::const_iterator & end)
			: d_iter(iter)
			, d_begin(begin)
			, d_end(end) {
		}

		const_iterator(const iterator & iter)
			: d_iter(iter.d_iter)
			, d_end(iter.d_end) {
		}

		const_iterator& operator++() {
			if ( d_iter == d_end ) {
				return *this;
			}
			do {
				++d_iter;
			}while(d_iter != d_end && d_iter->first == 0);
			return *this;
		}

		const_iterator& operator--() {
			if ( d_iter == d_begin ) {
				return *this;
			}
			do {
				--d_iter;
			}while(d_iter != d_begin && d_iter->first == 0);
			while( d_iter != d_end && d_iter->first == 0) {
				++d_iter;
			}
			return *this;
		}

		const_iterator operator++(int) {const_iterator retval = *this; ++(*this); return retval;}
		const_iterator operator--(int) {const_iterator retval = *this; --(*this); return retval;}
		bool operator==(const const_iterator & other) const {return d_iter == other.d_iter;}
		bool operator!=(const const_iterator & other) const {return !(*this == other);}
		const DenseMap::value_type & operator*() const {
			return reinterpret_cast<const std::pair<const Key,T>&>(*d_iter);
		}
		const DenseMap::value_type * operator->() const {
			return reinterpret_cast<const std::pair<const Key,T>*>(&(*d_iter));
		}
		// iterator traits
		using difference_type = long;
		using value_type = const DenseMap::value_type;
		using pointer = const DenseMap::value_type*;
		using reference = const DenseMap::value_type&;
		using iterator_category = std::forward_iterator_tag;
	private :
		typename std::vector<std::pair<Key,T>>::const_iterator d_iter,d_begin,d_end;
	};

	T & at(const Key & key) {
		if ( key == 0 || key > d_values.size() || d_values[key-1].first == 0 ) {
			throw std::out_of_range(std::to_string(key) + " is out of range");
		}
		return d_values[key-1].second;
	}

	const T & at(const Key & key) const {
		if ( key == 0 || key > d_values.size() || d_values[key-1].first == 0 ) {
			throw std::out_of_range(std::to_string(key) + " is out of range");
		}
		return d_values[key-1].second;
	}

	iterator begin() noexcept {
		auto b = d_values.begin();
		while ( b != d_values.end() && b->first == 0 ) {
			++b;
		}
		return iterator(b,d_values.begin(),d_values.end());
	}
	const_iterator begin() const noexcept {
		auto b = d_values.cbegin();
		while ( b != d_values.cend() && b->first == 0 ) {
			++b;
		}
		return const_iterator(b,d_values.cbegin(),d_values.cend());
	}
	const_iterator cbegin() const noexcept {
		auto b = d_values.cbegin();
		while ( b != d_values.cend() && b->first == 0 ) {
			++b;
		}
		return const_iterator(b,d_values.cbegin(),d_values.cend());
	}

	iterator end() noexcept {
		return iterator(d_values.end(),d_values.begin(),d_values.end());
	}
	const_iterator end() const noexcept {
		return const_iterator(d_values.cend(),d_values.begin(),d_values.cend());
	}
	const_iterator cend() const noexcept {
		return const_iterator(d_values.cend(),d_values.begin(),d_values.cend());
	}

	const_iterator lower_key(const Key & key) const noexcept {
		if ( key == 0 || d_values.empty() ){
			return cend();
		}
		if ( key > d_values.size() ) {
			return const_iterator(d_values.end()-1,d_values.cbegin(),d_values.cend());
		}

		if ( key == 1 ) {
			return d_values[0].first == 0 ? cend() : cbegin();
		}

		for ( auto iter = d_values.cbegin()+(key-1); iter != d_values.cbegin(); --iter) {
			if (iter->first != 0 ) {
				return const_iterator(iter,d_values.cbegin(),d_values.cend());
			}
		}

		return cend();
	}

	const_iterator upper_key(const Key & key) const noexcept {
		if ( key > d_values.size()
		     || d_values.empty()
		     || key == 0){
			return cend();
		}

		for ( auto iter = d_values.cbegin()+(key-1); iter != d_values.cend(); ++iter) {
			if (iter->first != 0 ) {
				return const_iterator(iter,d_values.cbegin(),d_values.cend());
			}
		}
		return cend();
	}

	bool empty() const noexcept {
		return d_values.empty();
	}

	size_t size() const noexcept {
		return d_size;
	}

	size_t count(const Key & key) const noexcept {
		if ( key == 0 || key > d_values.size() ) {
			return 0;
		}
		return d_values[key-1].first == 0 ? 0 : 1;
	}

	void clear() noexcept {
		d_size = 0;
		d_values.clear();
	}

	std::pair<iterator,bool> insert(const value_type & v) {
		const auto & k = v.first;
		if ( k == 0 ) {
			throw std::invalid_argument("Key 0 is reserved in this implementation");
		}
		if ( k > d_values.size() ) {
			d_values.resize(k,std::make_pair(0,T()));
		}
		if ( d_values[k-1].first != 0 ) {
			return std::make_pair(iterator(d_values.begin() + (k-1),d_values.begin(),d_values.end()),false);
		}
		d_values[k-1].first = v.first;
		d_values[k-1].second = v.second;
		++d_size;
		return std::make_pair(iterator(d_values.end()-1,d_values.begin(),d_values.end()),true);
	}

	void erase( const_iterator pos ) {
		auto k = pos->first;
		if ( k == 0 || k > d_values.size() || d_values[k-1].first == 0) {
			return;
		}
		d_values[k-1] = std::make_pair(0,T());
		--d_size;
		auto last = d_values.end();
		do {
			--last;
		} while( last != d_values.begin() && last->first == 0 );
		d_values.erase(last+1,d_values.end() + (k-1),d_values.end());
	}

	void erase( iterator pos ) {
		auto k = pos->first;
		if ( k == 0 || k > d_values.size() || d_values[k-1].first == 0) {
			return;
		}
		d_values[k-1] = std::make_pair(0,T());
		--d_size;
		auto last = d_values.end();
		do {
			--last;
		} while( last != d_values.begin() && last->first == 0 );
		d_values.erase(last+1,d_values.end());
	}

	size_t erase ( const key_type & key) {
		if ( key == 0 || key > d_values.size() || d_values[key-1].first == 0 ) {
			return 0;
		}
		erase(iterator(d_values.begin() + (key-1),d_values.begin(),d_values.end()));
		return 1;
	}
\
	const_iterator find( const key_type & key) const {
		if ( key == 0 || key > d_values.size() || d_values[key-1].first == 0) {
			return cend();
		}
		return const_iterator(d_values.cbegin()+(key-1),d_values.begin(),d_values.end());
	}

	iterator find( const key_type & key) {
		if ( key == 0 || key > d_values.size() || d_values[key-1].first == 0) {
			return end();
		}
		return iterator(d_values.begin()+(key-1),d_values.begin(),d_values.end());

	}


	DenseMap()
		: d_size(0) {
	}

private:
	std::vector<std::pair<Key,T>> d_values;
	size_t                        d_size;
};


} // namespace priv
} // namespace myrmidon
} // namespace fort
