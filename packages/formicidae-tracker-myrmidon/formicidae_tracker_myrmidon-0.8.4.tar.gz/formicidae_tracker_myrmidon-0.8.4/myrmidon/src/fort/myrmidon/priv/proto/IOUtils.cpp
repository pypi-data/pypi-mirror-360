#include "IOUtils.hpp"

#include <fort/myrmidon/utils/Checker.hpp>

#include <fort/myrmidon/Identification.hpp>
#include <fort/myrmidon/Shapes.hpp>

#include <fort/myrmidon/Time.pb.h>
#include <fort/myrmidon/AntDescription.pb.h>
#include <fort/myrmidon/Experiment.pb.h>
#include <fort/myrmidon/TrackingDataDirectory.pb.h>
#include <fort/myrmidon/TagCloseUpCache.pb.h>
#include <fort/myrmidon/TagFamily.pb.h>
#include <fort/myrmidon/Shapes.pb.h>
#include <fort/myrmidon/Zone.pb.h>
#include <fort/myrmidon/Space.pb.h>
#include <fort/myrmidon/Vector2d.pb.h>

#include <fort/myrmidon/priv/Experiment.hpp>
#include <fort/myrmidon/priv/Ant.hpp>
#include <fort/myrmidon/priv/TagCloseUp.hpp>
#include <fort/myrmidon/priv/Identifier.hpp>
#include <fort/myrmidon/priv/Measurement.hpp>
#include <fort/myrmidon/priv/Space.hpp>
#include <fort/myrmidon/priv/AntShapeType.hpp>
#include <fort/myrmidon/priv/TrackingDataDirectory.hpp>



namespace fort {
namespace myrmidon {
namespace priv {
namespace proto {


Time IOUtils::LoadTime(const pb::Time & pb, Time::MonoclockID mID) {
	if (pb.monotonic() != 0 ) {
		return Time::FromTimestampAndMonotonic(pb.timestamp(),pb.monotonic(),mID);
	} else {
		return Time::FromTimestamp(pb.timestamp());
	}

}

void IOUtils::SaveTime(pb::Time * pb,const Time & t) {
	t.ToTimestamp(pb->mutable_timestamp());
	if ( t.HasMono() ) {
		pb->set_monotonic(t.MonotonicValue());
	}
}



void IOUtils::LoadIdentification(const Experiment & e, const Ant & target,
                                 const fort::myrmidon::pb::Identification & pb) {
	auto start = Time::SinceEver();
	auto end =  Time::Forever();
	if ( pb.has_start() ) {
		start = Time::FromTimestamp(pb.start());
	}
	if ( pb.has_end() ) {
		end = Time::FromTimestamp(pb.end());
	}

	auto res = Identifier::AddIdentification(e.Identifier(),target.AntID(),pb.id(),start,end);
	if ( pb.tagsize() != 0.0 ) {
		res->SetTagSize(pb.tagsize());
	} else {
		res->SetTagSize(myrmidon::Identification::DEFAULT_TAG_SIZE);
	}
	if (pb.has_cachedpose() ) {
		Eigen::Vector2d antPosition;
		LoadVector(antPosition,pb.cachedpose().position());
		Identification::Accessor::SetAntPosition(*res,
		                                         antPosition,
		                                         pb.cachedpose().angle());
	}
	if ( pb.has_userdefinedpose() ) {
		Eigen::Vector2d antPosition;
		LoadVector(antPosition,pb.userdefinedpose().position());
		res->SetUserDefinedAntPose(antPosition,
		                           pb.userdefinedpose().angle());
	}
}

void IOUtils::SaveIdentification(fort::myrmidon::pb::Identification * pb,
                                 const Identification & ident) {
	pb->Clear();
	if ( ident.Start().IsSinceEver() == false ) {
		ident.Start().ToTimestamp(pb->mutable_start());
	}
	if ( ident.End().IsForever() == false ) {
		ident.End().ToTimestamp(pb->mutable_end());
	}
	pb->set_id(ident.TagValue());
	if ( ident.UseDefaultTagSize() == false ) {
		pb->set_tagsize(ident.TagSize());
	}

	fort::myrmidon::pb::IdentificationPose * poseToSave = nullptr;

	if ( ident.HasUserDefinedAntPose() == true ) {
		poseToSave = pb->mutable_userdefinedpose();
	} else {
		poseToSave = pb->mutable_cachedpose();
	}

	SaveVector(poseToSave->mutable_position(),ident.AntPosition());
	poseToSave->set_angle(ident.AntAngle());
}



template <typename T>
inline T Clamp(T v, T min, T max) {
	return std::min(std::max(v,min),max);
}

Color IOUtils::LoadColor(const pb::Color & pb) {
	return {
	        Clamp(uint32_t(pb.r()),uint32_t(0),uint32_t(255)),
	        Clamp(uint32_t(pb.g()),uint32_t(0),uint32_t(255)),
	        Clamp(uint32_t(pb.b()),uint32_t(0),uint32_t(255)),
	};
}

void  IOUtils::SaveColor(pb::Color * pb, const Color & c) {
	pb->set_r(std::get<0>(c));
	pb->set_g(std::get<1>(c));
	pb->set_b(std::get<2>(c));
}

Ant::DisplayState IOUtils::LoadAntDisplayState(int pb) {
	const static std::map<int,Ant::DisplayState> mapping =
		{
		 {pb::AntDisplayState::VISIBLE,Ant::DisplayState::VISIBLE},
		 {pb::AntDisplayState::HIDDEN,Ant::DisplayState::HIDDEN},
		 {pb::AntDisplayState::SOLO,Ant::DisplayState::SOLO},
		};
	auto fi = mapping.find(pb);
	if ( fi != mapping.end() ) {
		return fi->second;
	}
	return Ant::DisplayState::VISIBLE;
}

int IOUtils::SaveAntDisplayState(Ant::DisplayState s) {
	const static std::map<Ant::DisplayState,int> mapping =
		{
		 {Ant::DisplayState::VISIBLE,pb::AntDisplayState::VISIBLE},
		 {Ant::DisplayState::HIDDEN,pb::AntDisplayState::HIDDEN},
		 {Ant::DisplayState::SOLO,pb::AntDisplayState::SOLO},
		};
	auto fi = mapping.find(s);
	if ( fi != mapping.end() ) {
		return fi->second;
	}
	return pb::AntDisplayState::VISIBLE;
}


Value IOUtils::LoadValue(const pb::AntStaticValue & pb) {
	switch(pb.type()) {
	case 0:
		return pb.boolvalue();
	case 1:
		return pb.intvalue();
	case 2:
		return pb.doublevalue();
	case 3:
		return pb.stringvalue();
	case 4:
		return Time::FromTimestamp(pb.timevalue());
	default:
		throw std::logic_error("Unknown type " + std::to_string(pb.type()));
	}
}

void IOUtils::SaveValue(pb::AntStaticValue * pb, const Value & value) {
	pb->Clear();
	pb->set_type(pb::AntStaticValue_Type(value.index()));
	switch ( value.index() ) {
	case 0 :
		pb->set_boolvalue(std::get<bool>(value));
		break;
	case 1:
		pb->set_intvalue(std::get<int>(value));
		break;
	case 2:
		pb->set_doublevalue(std::get<double>(value));
		break;
	case 3:
		pb->set_stringvalue(std::get<std::string>(value));
		break;
	case 4:
		std::get<Time>(value).ToTimestamp(pb->mutable_timevalue());
		break;
	default:
		throw std::logic_error("Unknown Value index " + std::to_string(value.index()));
	}
}

void IOUtils::LoadAnt(Experiment & e, const fort::myrmidon::pb::AntDescription & pb) {
	auto ant = e.CreateAnt(pb.id());

	for ( const auto & ident : pb.identifications() ) {
		LoadIdentification(e,*ant,ident);
	}

	for ( const auto & s : pb.shape() ) {
		ant->AddCapsule(s.type(),LoadCapsule(s.capsule()));
	}

	ant->SetDisplayColor(LoadColor(pb.color()));
	ant->SetDisplayStatus(LoadAntDisplayState(pb.displaystate()));

	AntDataMap antData;
	for ( const auto & v : pb.namedvalues() ) {
		auto time = Time::SinceEver();
		if ( v.has_time() ) {
			time = Time::FromTimestamp(v.time());
		}
		antData[v.name()].push_back(std::make_pair(time,LoadValue(v.value())));
	}
	ant->SetValues(antData);
}

void IOUtils::SaveAnt(fort::myrmidon::pb::AntDescription * pb, const Ant & ant) {
	pb->Clear();
	pb->set_id(ant.AntID());

	for ( const auto & ident : ant.Identifications() ) {
		SaveIdentification(pb->add_identifications(),*ident);
	}

	for ( const auto & [type,capsule] : ant.Capsules() ) {
		auto spb = pb->add_shape();
		spb->set_type(type);
		SaveCapsule(spb->mutable_capsule(),*capsule);
	}

	SaveColor(pb->mutable_color(),ant.DisplayColor());
	pb->set_displaystate(pb::AntDisplayState(SaveAntDisplayState(ant.DisplayStatus())));

	for ( const auto & [name,tValues] : ant.DataMap() ) {
		for ( const auto & [time, value] : tValues ) {
			auto vPb = pb->add_namedvalues();
			vPb->set_name(name);
			if ( time.IsSinceEver() == false ) {
				time.ToTimestamp(vPb->mutable_time());
			}
			SaveValue(vPb->mutable_value(),value);
		}
	}
}


tags::Family IOUtils::LoadFamily(int pb) {
	static std::map<int,fort::tags::Family>
		mapping = {
		           {pb::UNSET,fort::tags::Family::Undefined},
		           {pb::TAG16H5,fort::tags::Family::Tag16h5},
		           {pb::TAG25H9,fort::tags::Family::Tag25h9},
		           {pb::TAG36ARTAG,fort::tags::Family::Tag36ARTag},
		           {pb::TAG36H10,fort::tags::Family::Tag36h10},
		           {pb::TAG36H11,fort::tags::Family::Tag36h11},
		           {pb::CIRCLE21H7,fort::tags::Family::Circle21h7},
		           {pb::CIRCLE49H12,fort::tags::Family::Circle49h12},
		           {pb::CUSTOM48H12,fort::tags::Family::Custom48h12},
		           {pb::STANDARD41H12,fort::tags::Family::Standard41h12},
		           {pb::STANDARD52H13,fort::tags::Family::Standard52h13},
	};
	auto fi = mapping.find(pb);
	if ( fi == mapping.end() ) {
		throw std::runtime_error("invalid protobuf enum value");
	}
	return fi->second;
}

int IOUtils::SaveFamily(tags::Family f) {
	static std::map<fort::tags::Family,int>
		mapping = {
		           {fort::tags::Family::Undefined,pb::UNSET},
		           {fort::tags::Family::Tag16h5,pb::TAG16H5},
		           {fort::tags::Family::Tag25h9,pb::TAG25H9},
		           {fort::tags::Family::Tag36ARTag,pb::TAG36ARTAG},
		           {fort::tags::Family::Tag36h10,pb::TAG36H10},
		           {fort::tags::Family::Tag36h11,pb::TAG36H11},
		           {fort::tags::Family::Circle21h7,pb::CIRCLE21H7},
		           {fort::tags::Family::Circle49h12,pb::CIRCLE49H12},
		           {fort::tags::Family::Custom48h12,pb::CUSTOM48H12},
		           {fort::tags::Family::Standard41h12,pb::STANDARD41H12},
		           {fort::tags::Family::Standard52h13,pb::STANDARD52H13},
	};
	auto fi = mapping.find(f);
	if ( fi == mapping.end() ) {
		throw std::runtime_error("invalid Experiment::TagFamily enum value");
	}
	return fi->second;
}

Measurement::ConstPtr IOUtils::LoadMeasurement(const pb::Measurement & pb) {
	Eigen::Vector2d start,end;
	LoadVector(start,pb.start());
	LoadVector(end,pb.end());
	return std::make_shared<Measurement>(pb.tagcloseupuri(),
	                                     pb.type(),
	                                     start,end,
	                                     pb.tagsizepx());
}


void IOUtils::LoadZone(Space & space,
                       const pb::Zone & pb) {
	auto z = space.CreateZone(pb.name(),pb.id());
	for ( const auto & dPb : pb.definitions() ) {
		Zone::Geometry::ConstPtr geometry;
		std::vector<Shape::Ptr> shapes;
		for ( const auto & sPb : dPb.shapes() ) {
			shapes.push_back(LoadShape(sPb));
		}

		auto start = Time::SinceEver();
		auto end = Time::Forever();

		if ( dPb.has_start() ) {
			start = Time::FromTimestamp(dPb.start());
		}
		if ( dPb.has_end() ) {
			end = Time::FromTimestamp(dPb.end());
		}

		z->AddDefinition(shapes,start,end);

	}
}

void IOUtils::SaveZone(pb::Zone * pb, const Zone & zone) {
	pb->Clear();
	pb->set_id(zone.ID());
	pb->set_name(zone.Name());
	for ( const auto & d : zone.Definitions() ) {
		auto dPb = pb->add_definitions();
		if ( d->Start().IsSinceEver() == false ) {
			d->Start().ToTimestamp(dPb->mutable_start());
		}
		if ( d->End().IsForever() == false ) {
			d->End().ToTimestamp(dPb->mutable_end());
		}
		for ( const auto & s : d->Shapes() ) {
			SaveShape(dPb->add_shapes(),*s);
		}
	}
}

void IOUtils::LoadSpace(Experiment & e,
                        const pb::Space & pb,
                        bool loadTrackingDataDirectory) {
	auto s = e.CreateSpace(pb.name(),pb.id());
	for ( const auto & zPb : pb.zones() ) {
		LoadZone(*s,zPb);
	}
	if ( loadTrackingDataDirectory == false ) {
		return;
	}
	for ( const auto & tddRelPath : pb.trackingdatadirectories() ) {
		auto [tdd,errors] = TrackingDataDirectory::Open(e.Basedir() / tddRelPath, e.Basedir());
		e.AddTrackingDataDirectory(s,tdd);
	}
}

void IOUtils::SaveSpace(pb::Space * pb,
                        const Space & space) {
	pb->Clear();
	pb->set_id(space.ID());
	pb->set_name(space.Name());
	for ( const auto & tdd : space.TrackingDataDirectories() ) {
		pb->add_trackingdatadirectories(tdd->URI());
	}
	for ( const auto & [zoneID,z] : space.Zones() ) {
		SaveZone(pb->add_zones(),*z);
	}
}


void IOUtils::SaveMeasurement(pb::Measurement * pb, const Measurement & m) {
	pb->Clear();
	pb->set_tagcloseupuri(m.TagCloseUpURI());
	pb->set_type(m.Type());
	SaveVector(pb->mutable_start(),m.StartFromTag());
	SaveVector(pb->mutable_end(),m.EndFromTag());
	pb->set_tagsizepx(m.TagSizePx());
}


void IOUtils::LoadExperiment(Experiment & e,
                             const pb::Experiment & pb) {
	e.SetAuthor(pb.author());
	e.SetName(pb.name());
	e.SetComment(pb.comment());
	e.SetDefaultTagSize(pb.tagsize());

	for (const auto & ct : pb.custommeasurementtypes()) {
		if ( ct.id() == Measurement::HEAD_TAIL_TYPE ) {
			auto fi = e.MeasurementTypes().find(Measurement::HEAD_TAIL_TYPE);
			if ( fi == e.MeasurementTypes().cend() ) {
				throw std::logic_error("Experiment missing default MeasurementType::ID Measurement::HEAD_TAIL_TYPE");
			}
			fi->second->SetName(ct.name());
		} else {
			e.CreateMeasurementType(ct.name(),ct.id());
		}
	}

	for (const auto & ast : pb.antshapetypes() ) {
		e.CreateAntShapeType(ast.name(),ast.id());
	}

	for (const auto & column : pb.antmetadata() ) {
		auto defaultValue = LoadValue(column.defaultvalue());
		auto c = e.SetMetaDataKey(column.name(),defaultValue);
	}
}



void IOUtils::SaveExperiment(fort::myrmidon::pb::Experiment * pb, const Experiment & e) {
	pb->Clear();
	pb->set_name(e.Name());
	pb->set_author(e.Author());
	pb->set_comment(e.Comment());
	pb->set_tagsize(e.DefaultTagSize());


	for ( const auto & [MTID,t] : e.MeasurementTypes() ) {
		auto mtPb = pb->add_custommeasurementtypes();
		mtPb->set_id(t->MTID());
		mtPb->set_name(t->Name());
	}

	for ( const auto & [typeID,shapeType] : e.AntShapeTypes() ) {
		auto stPb = pb->add_antshapetypes();
		stPb->set_id(shapeType->TypeID());
		stPb->set_name(shapeType->Name());
	}

	for ( const auto & [name,key] : e.AntMetadataPtr()->Keys() ) {
		auto cPb = pb->add_antmetadata();
		cPb->set_name(key->Name());
		SaveValue(cPb->mutable_defaultvalue(),key->DefaultValue());
	}

}

void IOUtils::LoadFrameReference(FrameReference * ref,
                                 const pb::TimedFrame & pb,
                                 const std::string & parentURI,
                                 Time::MonoclockID monoID) {
	*ref = FrameReference(parentURI,pb.frameid(),LoadTime(pb.time(),monoID));
}

void IOUtils::SaveFrameReference(pb::TimedFrame * pb,
                                 const FrameReference & ref) {
		pb->set_frameid(ref.FrameID());
		SaveTime(pb->mutable_time(),ref.Time());
}

void IOUtils::LoadTrackingIndexSegment(TrackingDataDirectory::TrackingIndex::Segment * s,
                                       const pb::TrackingSegment & pb,
                                       const std::string & parentURI,
                                       Time::MonoclockID monoID) {

	LoadFrameReference(&(s->first),pb.frame(),parentURI,monoID);
	s->second = pb.filename();
}

void IOUtils::SaveTrackingIndexSegment(pb::TrackingSegment * pb,
                                       const TrackingDataDirectory::TrackingIndex::Segment & si) {
	SaveFrameReference(pb->mutable_frame(),si.first);
	pb->set_filename(si.second);
}


MovieSegment::ConstPtr
IOUtils::LoadMovieSegment(const fort::myrmidon::pb::MovieSegment & pb,
                          const fs::path & parentAbsoluteFilePath,
                          const std::string & parentURI) {
	FORT_MYRMIDON_CHECK_PATH_IS_ABSOLUTE(parentAbsoluteFilePath);

	MovieSegment::ListOfOffset offsets;
	for ( const auto & o : pb.offsets() ) {
		offsets.push_back(std::make_pair(o.movieframeid(),o.offset()));
	}

	return std::make_shared<MovieSegment>(pb.id(),
	                                      parentAbsoluteFilePath / pb.path(),
	                                      parentURI,
	                                      pb.trackingstart(),
	                                      pb.trackingend(),
	                                      pb.moviestart(),
	                                      pb.movieend(),
	                                      offsets);
}

void IOUtils::SaveMovieSegment(fort::myrmidon::pb::MovieSegment * pb,
                               const MovieSegment & ms,
                               const fs::path & parentAbsoluteFilePath) {

	if (parentAbsoluteFilePath.is_absolute() == false ) {
		throw std::invalid_argument("parentAbsoluteFilePath:'"
		                            + parentAbsoluteFilePath.string()
		                            + "' is not an absolute path");
	}
	pb->Clear();

	pb->set_id(ms.ID());
	pb->set_path(fs::relative(ms.AbsoluteFilePath(),parentAbsoluteFilePath).generic_string());
	pb->set_trackingstart(ms.StartFrame());
	pb->set_trackingend(ms.EndFrame());
	pb->set_moviestart(ms.StartMovieFrame());
	pb->set_movieend(ms.EndMovieFrame());
	for ( const auto & o : ms.Offsets() ) {
		auto pbo = pb->add_offsets();
		pbo->set_movieframeid(o.first);
		pbo->set_offset(o.second);
	}
}

TagCloseUp::ConstPtr IOUtils::LoadTagCloseUp(const pb::TagCloseUp & pb,
                                             const fs::path & absoluteBasedir,
                                             std::function<FrameReference (FrameID)> resolver) {
	FORT_MYRMIDON_CHECK_PATH_IS_ABSOLUTE(absoluteBasedir);

	Vector2dList corners;
	if ( pb.corners_size() != 4 ) {
		throw std::invalid_argument("protobuf message does not contains 4 corners");
	}
	corners.resize(4);
	for(size_t i = 0; i < 4; ++i ) {
		LoadVector(corners[i],pb.corners(i));
	}
	Eigen::Vector2d position;
	LoadVector(position,pb.position());

	return std::make_shared<TagCloseUp>(absoluteBasedir / pb.imagepath(),
	                                    resolver(pb.frameid()),
	                                    pb.value(),
	                                    position,
	                                    pb.angle(),
	                                    corners);
}

void IOUtils::SaveTagCloseUp(pb::TagCloseUp * pb,
                             const TagCloseUp & tcu,
                             const fs::path & absoluteBasedir) {
	FORT_MYRMIDON_CHECK_PATH_IS_ABSOLUTE(absoluteBasedir);

	pb->Clear();

	pb->set_frameid(tcu.Frame().FrameID());
	pb->set_imagepath(fs::relative(tcu.AbsoluteFilePath(),absoluteBasedir).generic_string());
	SaveVector(pb->mutable_position(),tcu.TagPosition());
	pb->set_angle(tcu.TagAngle());
	pb->set_value(tcu.TagValue());
	for (const auto & c : tcu.Corners()) {
		SaveVector(pb->add_corners(),c);
	}

}

Capsule::Ptr IOUtils::LoadCapsule(const pb::Capsule & pb) {
	Eigen::Vector2d c1,c2;
	LoadVector(c1,pb.c1());
	LoadVector(c2,pb.c2());
	return std::make_shared<Capsule>(c1,c2,
	                                 pb.r1(),
	                                 pb.r2());
}

void IOUtils::SaveCapsule(pb::Capsule * pb,const Capsule & capsule) {
	SaveVector(pb->mutable_c1(),capsule.C1());
	SaveVector(pb->mutable_c2(),capsule.C2());
	pb->set_r1(capsule.R1());
	pb->set_r2(capsule.R2());
}

Circle::Ptr IOUtils::LoadCircle(const pb::Circle & pb) {
	Eigen::Vector2d center;
	LoadVector(center,pb.center());
	return std::make_shared<Circle>(center,pb.radius());
}

void IOUtils::SaveCircle(pb::Circle * pb, const Circle & circle) {
	pb->Clear();
	SaveVector(pb->mutable_center(),circle.Center());
	pb->set_radius(circle.Radius());
}

Polygon::Ptr IOUtils::LoadPolygon(const pb::Polygon & pb) {
	Vector2dList vertices;
	vertices.reserve(pb.vertices_size());
	for ( const auto & v : pb.vertices() ) {
		Eigen::Vector2d vv;
		LoadVector(vv,v);
		vertices.push_back(vv);
	}
	return std::make_shared<Polygon>(vertices);
}

void IOUtils::SavePolygon(pb::Polygon * pb, const Polygon & polygon) {
	pb->Clear();
	for ( size_t i = 0; i < polygon.Size(); ++i) {
		SaveVector(pb->add_vertices(),polygon.Vertex(i));
	}
}

Shape::Ptr IOUtils::LoadShape(const pb::Shape & pb) {
	if ( pb.has_capsule() == true ) {
		return LoadCapsule(pb.capsule());
	}

	if ( pb.has_circle() == true ) {
		return LoadCircle(pb.circle());
	}

	if ( pb.has_polygon() == true) {
		return LoadPolygon(pb.polygon());
	}
	return Shape::Ptr();
}

void IOUtils::SaveShape(pb::Shape * pb, const Shape & shape) {
	switch(shape.ShapeType()) {
	case myrmidon::Shape::Type::CAPSULE:
		SaveCapsule(pb->mutable_capsule(),static_cast<const Capsule &>(shape));
		return;
	case myrmidon::Shape::Type::CIRCLE:
		SaveCircle(pb->mutable_circle(),static_cast<const Circle &>(shape));
		return;
	case myrmidon::Shape::Type::POLYGON:
		SavePolygon(pb->mutable_polygon(),static_cast<const Polygon &>(shape));
		return;
	default:
		return;
	}
}







} //namespace proto
} //namespace priv
} //namespace myrmidon
} //namespace fort
