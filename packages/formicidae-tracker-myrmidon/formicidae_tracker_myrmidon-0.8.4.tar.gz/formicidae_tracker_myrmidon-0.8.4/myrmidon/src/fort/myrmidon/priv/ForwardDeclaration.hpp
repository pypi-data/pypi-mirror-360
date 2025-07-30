#pragma once

#include <memory>
#include <vector>
#include <map>
#include <string>

#include "DenseMap.hpp"
#include "ContiguousIDContainer.hpp"

#include <fort/myrmidon/types/Typedefs.hpp>


#define FORT_MYRMIDON_FDECLARE_CLASS(ClassName) \
	class ClassName; \
	typedef std::shared_ptr<ClassName> ClassName ## Ptr; \
	typedef std::shared_ptr<const ClassName> ClassName ## ConstPtr;


namespace fort {
namespace myrmidon {
namespace priv {

class Experiment;
typedef std::shared_ptr<Experiment> ExperimentPtr;

class Ant;
typedef std::shared_ptr<Ant> AntPtr;

FORT_MYRMIDON_FDECLARE_CLASS(Identification)

// Forward decalation for an <priv::IdentifierIF>
FORT_MYRMIDON_FDECLARE_CLASS(IdentifierIF)

// Forward decalation for an <priv::Identifier>
FORT_MYRMIDON_FDECLARE_CLASS(Identifier)

class TrackingDataDirectory;
// Forward decalation for an <priv::TrackingDataDirectory>
typedef std::shared_ptr<TrackingDataDirectory>   TrackingDataDirectoryPtr;

typedef std::map<std::string,TrackingDataDirectoryPtr> TrackingDataDirectoryByURI;

class RawFrame;
// Forward decalation for an <priv::RawFrame::ConstPtr>
typedef std::shared_ptr<const RawFrame>   RawFrameConstPtr;


// Forward declaration for a <priv::MovieSegment>
FORT_MYRMIDON_FDECLARE_CLASS(MovieSegment)

// Forward declaration for a <priv::TagCloseUp>
FORT_MYRMIDON_FDECLARE_CLASS(TagCloseUp)

//Forward declaration for a <priv::AntPoseEstimate>
FORT_MYRMIDON_FDECLARE_CLASS(AntPoseEstimate)

//Forward declaration for a <priv::Measurement>
FORT_MYRMIDON_FDECLARE_CLASS(Measurement)

//Forward declaration for a <priv::MeasurementType>
FORT_MYRMIDON_FDECLARE_CLASS(MeasurementType)

//Forward declaration for a <priv::Space>
class Space;
typedef std::shared_ptr<Space> SpacePtr;

class Universe;
typedef std::shared_ptr<Universe> UniversePtr;

// Forward declaration for a <priv::Zone>
class Zone;
typedef std::shared_ptr<Zone> ZonePtr;

// Forward declaration for a <priv::AntShapeType>
FORT_MYRMIDON_FDECLARE_CLASS(AntShapeType)



// A Map of <Ant> identified by their <Ant::ID>
typedef DenseMap<AntID,AntPtr> AntByID;

// A List of <Identification>
typedef std::vector<IdentificationPtr>  IdentificationList;

typedef uint32_t                        SpaceID;
typedef DenseMap<SpaceID,SpacePtr>      SpaceByID;

typedef uint32_t                      ZoneID;
typedef DenseMap<ZoneID,ZonePtr>      ZoneByID;


// Forward declaration of <priv::MeasurementType::ID>
typedef uint32_t MeasurementTypeID;
// Maps the <MeasurementType> by their <MeasurementType::ID>
typedef DenseMap<MeasurementTypeID,MeasurementTypePtr>      MeasurementTypeByID;



typedef uint32_t AntShapeTypeID;
typedef DenseMap<AntShapeTypeID,AntShapeTypePtr>      AntShapeTypeByID;

FORT_MYRMIDON_FDECLARE_CLASS(AntShapeTypeContainer)

FORT_MYRMIDON_FDECLARE_CLASS(AntMetadata)

// Forward declaration for a <priv::InteractionSolver>
FORT_MYRMIDON_FDECLARE_CLASS(CollisionSolver)

} // namespace priv
} // namespace myrmidon
} // namespace fort


#undef FORT_MYRMIDON_FDECLARE_CLASS
