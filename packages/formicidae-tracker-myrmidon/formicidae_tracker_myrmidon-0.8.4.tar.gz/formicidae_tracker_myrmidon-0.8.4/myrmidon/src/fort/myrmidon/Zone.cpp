#include "Zone.hpp"

#include <fort/myrmidon/Shapes.hpp>

#include "handle/ZoneHandle.hpp"
#include "handle/ZoneDefinitionHandle.hpp"

#include "priv/Zone.hpp"

namespace fort {
namespace myrmidon {



Zone::Zone(std::unique_ptr<ZoneHandle> handle)
	: d_p(std::move(handle)) {
}

Zone::~Zone() = default;

ZoneDefinition::ZoneDefinition(std::unique_ptr<ZoneDefinitionHandle> handle)
	: d_p(std::move(handle)) {
}

ZoneDefinition::~ZoneDefinition() = default;

const Shape::List & ZoneDefinition::Shapes() const {
	return d_p->Get().Shapes();
}

void ZoneDefinition::SetShapes(const Shape::List & shapes) {
	d_p->Get().SetShapes(shapes);
}


const Time & ZoneDefinition::Start() const {
	return d_p->Get().Start();
}

const Time & ZoneDefinition::End() const {
	return d_p->Get().End();
}

void ZoneDefinition::SetStart(const Time & start) {
	d_p->Get().SetStart(start);
}

void ZoneDefinition::SetEnd(const Time & end) {
	d_p->Get().SetEnd(end);
}

ZoneDefinition::Ptr Zone::AddDefinition(const Shape::List & shapes,
                                        const Time & start,
                                        const Time & end) {
	return d_p->AddDefinition(shapes,start,end);
}

const ZoneDefinitionList & Zone::Definitions() const {
	return d_p->Definitions();
}

void Zone::DeleteDefinition(size_t index) {
	d_p->DeleteDefinition(index);
}

const std::string & Zone::Name() const {
	return d_p->Get().Name();
}

void Zone::SetName(const std::string & name) {
	d_p->Get().SetName(name);
}

ZoneID Zone::ID() const {
	return d_p->Get().ID();
}



} // namespace myrmidon
} // namespace fort
