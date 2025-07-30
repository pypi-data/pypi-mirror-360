#pragma once

#include "DenseMap.hpp"

#include <algorithm>
#include <functional>
#include <set>

namespace fort {
namespace myrmidon {
namespace priv {

template <typename TID, typename T> class AlmostContiguousIDContainer {
public:
	typedef DenseMap<TID, std::shared_ptr<T>>       ObjectByID;
	typedef DenseMap<TID, std::shared_ptr<const T>> ConstObjectByID;
	typedef std::set<TID>                           SetOfObjectID;
	typedef std::function<std::shared_ptr<T>(TID)>  Creator;

	class AlreadyExistingObject : public std::runtime_error {
	public:
		AlreadyExistingObject(TID ID) noexcept
		    : std::runtime_error(
		          std::string(typeid(T).name()) + " " + std::to_string(ID) +
		          " already exists"
		      ){};
		virtual ~AlreadyExistingObject() noexcept {};
	};

	class UnmanagedObject : public std::out_of_range {
	public:
		UnmanagedObject(TID ID) noexcept
		    : std::out_of_range(
		          std::string(typeid(T).name()) + " " + std::to_string(ID) +
		          " is not managed"
		      ){};
		virtual ~UnmanagedObject() noexcept {};
	};

	const static TID NEXT_AVAILABLE_OBJECT_ID = 0;

	AlmostContiguousIDContainer()
	    : d_continuous(false) {}

	std::shared_ptr<T>
	CreateObject(Creator creator, TID ID = NEXT_AVAILABLE_OBJECT_ID) {
		if (ID == NEXT_AVAILABLE_OBJECT_ID) {
			ID = NextAvailableObjectID();
		}

		if (d_objectIDs.count(ID) != 0) {
			throw AlreadyExistingObject(ID);
		}

		auto res = creator(ID);
		d_objects.insert(std::make_pair(ID, res));
		d_objectIDs.insert(ID);
		return res;
	}

	void DeleteObject(TID ID) {
		auto fi = d_objects.find(ID);
		if (fi == d_objects.end()) {
			throw UnmanagedObject(ID);
		}
		if (ID != d_objects.size()) {
			d_continuous = false;
		}
		d_objects.erase(fi);
		d_objectIDs.erase(ID);
	}

	const ObjectByID &Objects() const {
		return d_objects;
	}

	size_t Count(TID ID) const {
		return d_objects.count(ID);
	}

	TID NextAvailableObjectID() {
		if (d_continuous == true) {
			return d_objects.size() + 1;
		}
		TID  res          = 0;
		auto missingIndex = std::find_if(
		    d_objectIDs.begin(),
		    d_objectIDs.end(),
		    [&res](TID toTest) { return ++res != toTest; }
		);
		if (missingIndex == d_objectIDs.end()) {
			d_continuous = true;
			return d_objects.size() + 1;
		}

		return res;
	}

private:
	ObjectByID    d_objects;
	SetOfObjectID d_objectIDs;
	bool          d_continuous;
};

} // namespace priv
} // namespace myrmidon
} // namespace fort
