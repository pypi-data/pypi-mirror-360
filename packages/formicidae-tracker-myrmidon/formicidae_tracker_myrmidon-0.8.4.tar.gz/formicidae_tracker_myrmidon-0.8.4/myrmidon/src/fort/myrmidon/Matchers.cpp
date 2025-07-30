#include "Matchers.hpp"

#include "priv/Matchers.hpp"

namespace fort {
namespace myrmidon {

Matcher::Ptr Matcher::And(std::vector<Ptr> matchers) {
	std::vector<PPtr> pMatchers;
	pMatchers.reserve(matchers.size());
	for ( const auto & m : matchers ) { pMatchers.push_back(m->d_p); }
	return Matcher::Ptr(new Matcher(priv::Matcher::And(pMatchers)));
}

Matcher::Ptr Matcher::Or(std::vector<Ptr> matchers) {
	std::vector<PPtr> pMatchers;
	pMatchers.reserve(matchers.size());
	for ( const auto & m : matchers ) { pMatchers.push_back(m->d_p); }
	return Matcher::Ptr(new Matcher(priv::Matcher::Or(pMatchers)));
}

Matcher::Ptr Matcher::AntID(fort::myrmidon::AntID ID) {
	return Matcher::Ptr(new Matcher(priv::Matcher::AntIDMatcher(ID)));
}

Matcher::Ptr Matcher::AntMetaData(const std::string & key,
                                  const Value & value) {
	return Matcher::Ptr(new Matcher(priv::Matcher::AntColumnMatcher(key,value)));
}

Matcher::Ptr Matcher::AntDistanceSmallerThan(double distance) {
	return Matcher::Ptr(new Matcher(priv::Matcher::AntDistanceSmallerThan(distance)));
}

Matcher::Ptr Matcher::AntDistanceGreaterThan(double distance) {
	return Matcher::Ptr(new Matcher(priv::Matcher::AntDistanceGreaterThan(distance)));
}

Matcher::Ptr Matcher::AntAngleGreaterThan(double angle) {
	return Matcher::Ptr(new Matcher(priv::Matcher::AntAngleGreaterThan(angle)));
}

Matcher::Ptr Matcher::AntAngleSmallerThan(double angle) {
	return Matcher::Ptr(new Matcher(priv::Matcher::AntAngleSmallerThan(angle)));
}

Matcher::Ptr Matcher::InteractionType(AntShapeTypeID type1,
                                      AntShapeTypeID type2) {
	return Matcher::Ptr(new Matcher(priv::Matcher::InteractionType(type1,type2)));
}

Matcher::Ptr Matcher::AntDisplacement(double under,
                                      Duration minimumGap) {

	return Matcher::Ptr(new Matcher(priv::Matcher::AntDisplacement(under,minimumGap)));
}


Matcher::PPtr Matcher::ToPrivate() const {
	return d_p;
}

std::ostream & operator<<(std::ostream & out,
                          const fort::myrmidon::Matcher & m) {
	return out << *m.d_p;
}

} // namespace myrmidon
} // namespace fort
