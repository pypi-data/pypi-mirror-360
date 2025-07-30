#include "Space.hpp"

#include "TrackingDataDirectory.hpp"
#include <fort/myrmidon/utils/StringManipulation.hpp>

namespace fort {
namespace myrmidon {
namespace priv {

Space::TDDOverlap::TDDOverlap(const TrackingDataDirectory::Ptr & a,
                              const TrackingDataDirectory::Ptr & b) noexcept
	: std::domain_error(BuildWhat(a,b))
	, d_a(a)
	, d_b(b) {
}

const TrackingDataDirectoryPtr & Space::TDDOverlap::A() const {
	return d_a;
}

const TrackingDataDirectoryPtr & Space::TDDOverlap::B() const {
	return d_b;
}

std::string Space::TDDOverlap::BuildWhat(const TrackingDataDirectory::Ptr & a,
                                         const TrackingDataDirectory::Ptr & b) noexcept {
	std::ostringstream oss;

	oss << *a << " and " << *b << " overlaps in time";

	return oss.str();
}

Space::UnmanagedTrackingDataDirectory::UnmanagedTrackingDataDirectory(const std::string & URI) noexcept
	: std::invalid_argument("Unknown TDD{URI:'" + URI + "'}") {
}

Space::UnmanagedSpace::UnmanagedSpace(SpaceID spaceID) noexcept
	: std::out_of_range("Unknown SpaceID " + std::to_string(spaceID)) {
}

Space::InvalidName::InvalidName(const std::string & name,
                                const std::string & reason) noexcept
	: std::invalid_argument("Invalid Space name '" + name + "': " + reason) {
}

Space::SpaceNotEmpty::SpaceNotEmpty(const Space & z)
	: std::runtime_error(BuildReason(z)) {
}

std::string Space::SpaceNotEmpty::BuildReason(const Space & z) {
	std::ostringstream oss;
	oss << "Space{ID:" << z.ID() << ", Name:'" << z.Name()
	    << "'} is not empty (contains:";
	std::string sep = "{'";
	for ( const auto & tdd : z.d_tdds ) {
		oss << sep << tdd->URI();
		sep = "','";
	}
	oss << "'})";
	return oss.str();
}

Space::TDDAlreadyInUse::TDDAlreadyInUse(const std::string & tddURI, SpaceID spaceID)
	: std::invalid_argument("TDD{URI:'"
	                        + tddURI
	                        + "'} is in use in Space{ID:"
	                        + std::to_string(spaceID) + "}") {
}

Space::Ptr Universe::CreateSpace(const Ptr & itself,
                                 SpaceID spaceID,
                                 const std::string & name) {
	return itself->d_spaces.CreateObject([&itself,&name](SpaceID spaceID) {
		                                     return Space::Ptr(new Space(spaceID,name,itself));
	                                     });
}

void Universe::DeleteSpace(SpaceID spaceID) {
	auto fi = d_spaces.Objects().find(spaceID);
	if ( fi == d_spaces.Objects().end() ) {
		throw Space::UnmanagedSpace(spaceID);
	}

	if ( fi->second->d_tdds.empty() == false ) {
		throw Space::SpaceNotEmpty(*fi->second);
	}

	d_spaces.DeleteObject(spaceID);
}

void Universe::DeleteTrackingDataDirectory(const std::string & URI) {
	for ( const auto & [spaceID,s] : d_spaces.Objects() ) {
		try {
			s->DeleteTrackingDataDirectory(URI);
			return;
		} catch ( const Space::UnmanagedTrackingDataDirectory & e) {
		}
	}
	throw Space::UnmanagedTrackingDataDirectory(URI);
}


const SpaceByID & Universe::Spaces() const {
	return d_spaces.Objects();
}

Space::Space(SpaceID spaceID, const std::string & name, const Universe::Ptr & universe)
	: d_universe(universe)
	, d_spaceID(spaceID) {
	SetName(name);
}

Space::~Space() {}

const TrackingDataDirectoryByURI &
Universe::TrackingDataDirectories() const {
	return d_tddsByURI;
}


void Space::Accessor::AddTrackingDataDirectory(const Space::Ptr & itself,
                                               const TrackingDataDirectoryPtr & tdd) {
	itself->AddTrackingDataDirectory(tdd);
}

void Space::AddTrackingDataDirectory(const TrackingDataDirectory::Ptr & tdd) {
	if ( utils::HasPrefix(tdd->URI(),"spaces/") == true ) {
		throw std::runtime_error("Invalid TDD path '" + tdd->URI() + "': starts with 'spaces/'");
	}

	auto newList = d_tdds;
	newList.push_back(tdd);
	auto fi = TimeValid::SortAndCheckOverlap(newList.begin(),newList.end());
	if ( fi.first != fi.second ) {
		throw TDDOverlap(*fi.first,*fi.second);
	}

	auto universe = LockUniverse();

	if ( universe->d_tddsByURI.count(tdd->URI()) != 0 ) {
		auto si = std::find_if(universe->d_spaces.Objects().begin(),
		                       universe->d_spaces.Objects().end(),
		                       [&tdd](const std::pair<SpaceID,Space::Ptr> & iter) {
			                       auto ti = std::find_if(iter.second->d_tdds.begin(),
			                                              iter.second->d_tdds.end(),
			                                              [&tdd](const TrackingDataDirectory::Ptr & tddb) {
				                                              return tdd->URI() == tddb->URI();
			                                              });
			                       return ti != iter.second->d_tdds.end();
		                       });
		if ( si == universe->d_spaces.Objects().end()){
			throw std::logic_error("Internal data error");
		}

		throw TDDAlreadyInUse(tdd->URI(),si->second->ID());
	}

	d_tdds = newList;
	universe->d_tddsByURI.insert(std::make_pair(tdd->URI(),tdd));
}

void Space::DeleteTrackingDataDirectory(const std::string & URI) {
	auto fi = std::find_if(d_tdds.begin(),
	                       d_tdds.end(),
	                       [&URI](const TrackingDataDirectory::Ptr & tdd) {
		                       return URI == tdd->URI();
	                       });
	if ( fi == d_tdds.end() ) {
		throw UnmanagedTrackingDataDirectory(URI);
	}
	auto universe = LockUniverse();
	universe->d_tddsByURI.erase(URI);

	d_tdds.erase(fi);
}

const std::string & Space::URI() const {
	return d_URI;
}

const std::string & Space::Name() const {
	return d_name;
}

SpaceID Space::ID() const {
	return d_spaceID;
}


void Space::SetName(const std::string & name) {
	fs::path URI = fs::path("spaces") / std::to_string(d_spaceID);
	if (name.empty()) {
		throw InvalidName(name,"it is empty");
	}
	if (fs::path(name).filename() != fs::path(name)) {
		throw InvalidName(name,"invalid character in path");
	}

	auto universe = LockUniverse();

	auto zi = std::find_if(universe->d_spaces.Objects().begin(),
	                       universe->d_spaces.Objects().end(),
	                       [&name](const std::pair<SpaceID,Space::Ptr> & iter ) {
		                       return iter.second->Name() == name;
	                       });
	if (zi != universe->d_spaces.Objects().end()) {
		throw InvalidName(name,"is already used by another Space");
	}

	if ( universe->d_tddsByURI.count(name) != 0 ) {
		throw InvalidName(name,"is already used by another TDD");
	}

	d_name = name;
	d_URI = URI.generic_string();
}

const std::vector<TrackingDataDirectory::Ptr> & Space::TrackingDataDirectories() const {
	return d_tdds;
}

Universe::Ptr Space::LockUniverse() const {
	auto locked = d_universe.lock();
	if ( !locked ) {
		throw DeletedReference<Universe>();
	}
	return locked;
}

std::pair<Space::Ptr,TrackingDataDirectory::Ptr>
Universe::LocateTrackingDataDirectory(const std::string & tddURI) const {
	auto tddi = d_tddsByURI.find(tddURI) ;
	if ( tddi == d_tddsByURI.end() ) {
		return std::make_pair(Space::Ptr(),TrackingDataDirectory::Ptr());
	}

	auto si = std::find_if(d_spaces.Objects().begin(),
	                       d_spaces.Objects().end(),
	                       [&tddURI]( const std::pair<SpaceID,Space::ConstPtr> & iter) {
		                       auto ti = std::find_if(iter.second->d_tdds.begin(),
		                                              iter.second->d_tdds.end(),
		                                              [&tddURI]( const TrackingDataDirectory::Ptr & tdd) {
			                                              return tdd->URI() == tddURI;
		                                              });
		                       return ti != iter.second->d_tdds.end();
	                       });
	if ( si ==  d_spaces.Objects().end()) {
		return std::make_pair(Space::Ptr(),TrackingDataDirectory::Ptr());
	}

	return std::make_pair(si->second,tddi->second);
}

Space::Ptr Universe::LocateSpace(const std::string & spaceName) const {
	auto si = std::find_if(d_spaces.Objects().begin(),
	                       d_spaces.Objects().end(),
	                       [&spaceName] ( const std::pair<SpaceID,Space::ConstPtr> & iter) {
		                       return iter.second->Name() == spaceName;
	                       });
	if ( si == d_spaces.Objects().end()) {
		return Space::Ptr();
	}
	return si->second;
}

Zone::Ptr Universe::CreateZone(ZoneID zoneID,
                               const std::string & name,
                               const std::string & parentURI) {
	try {
		return d_zones.CreateObject([&name,&parentURI](ZoneID zoneID_) { return Zone::Create(zoneID_,name,parentURI); },zoneID);
	} catch ( const AlmostContiguousIDContainer<ZoneID,Zone>::AlreadyExistingObject & ) {
		return d_zones.CreateObject([&name,&parentURI](ZoneID zoneID_) { return Zone::Create(zoneID_,name,parentURI); },0);
	}
}

void Universe::DeleteZone(ZoneID zoneID) {
	try {
		d_zones.DeleteObject(zoneID);
	} catch ( const AlmostContiguousIDContainer<ZoneID, Zone>::UnmanagedObject &) {
		throw std::out_of_range("Unknown ZoneID " + std::to_string(zoneID));
	}
}


Zone::Ptr Space::CreateZone(const std::string & name, ZoneID zoneID) {
	auto zone = LockUniverse()->CreateZone(zoneID,name,d_URI);
	d_zones.insert({zone->ID(),zone});
	return zone;
}


void Space::DeleteZone(ZoneID zoneID) {
	LockUniverse()->DeleteZone(zoneID);
	d_zones.erase(zoneID);
}


const ZoneByID & Space::Zones() const {
	return d_zones;
}





} //namespace priv
} //namespace myrmidon
} //namespace fort
