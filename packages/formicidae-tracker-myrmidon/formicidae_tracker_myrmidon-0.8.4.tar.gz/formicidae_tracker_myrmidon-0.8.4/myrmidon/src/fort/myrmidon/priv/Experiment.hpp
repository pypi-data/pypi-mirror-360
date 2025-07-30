#pragma once

#include <cstdint>
#include <map>
#include <string>

#include <fort/tags/fort-tags.hpp>

#include <fort/myrmidon/types/ComputedMeasurement.hpp>
#include <fort/myrmidon/types/Reporter.hpp>
#include <fort/myrmidon/types/Typedefs.hpp>

#include <fort/myrmidon/utils/FileSystem.hpp>

#include "AntMetadata.hpp"
#include "ForwardDeclaration.hpp"
#include "LocatableTypes.hpp"

namespace fort {
namespace myrmidon {
namespace priv {

using namespace fort::myrmidon;

// Entry point of the myrmidon private interface
//
// An <priv::Experiment> is responsible to hold the links to the
// <TrackingDataDirectory> and to provide the <Identifier> for an
// actual Ant colony.
//
// It also provide the interface to read/write <priv::Experiment> to
// the filesystem.
//
// user may only to initialize a single object of this type, as
// <priv::Ant> will be only uniquely identified by theyr
// <myrmidon::Ant::ID> when they originate from the same
// <Identifier>. Anyway dataset are very large and we should not try
// to anlayse several of them in the same program.
class Experiment : public FileSystemLocatable {
public:
	typedef std::map<uint32_t, MeasurementConstPtr>  MeasurementByType;
	typedef std::map<std::string, MeasurementByType> MeasurementByTagCloseUp;

	const static MeasurementTypeID NEXT_AVAILABLE_MEASUREMENT_TYPE_ID = 0;
	const static AntShapeTypeID    NEXT_AVAILABLE_ANT_SHAPE_TYPE_ID   = 0;

	// A Pointer to an Experiment.
	typedef std::shared_ptr<Experiment>       Ptr;
	// A Pointer to a const Experiment.
	typedef std::shared_ptr<const Experiment> ConstPtr;

	// Opens an existing experiment given its fs::path
	// @filename the fs::path to the ".myrmidon" file
	// @return a <Ptr> to the <Experiment>.
	static Ptr Open(const fs::path &filename);

	// Opens an existing experiment given its fs::path, without
	// opening any actual data.
	//
	// @filename the fs::path to the ".myrmidon" file
	//
	// @return a <Ptr> to the <Experiment>.
	static Ptr OpenDataLess(const fs::path &filename);

	// Creates a new <Experiment> given a fs::path
	// @filename the fs::path to the ".myrmidon" file
	//
	// Creates a new <Experiment> associated with the
	// <fs::path>. **This function does not create any file on
	// itself.** Use either <NewFile> or <Save>
	// @return a <Ptr> to the empty <Experiment>
	static Ptr Create(const fs::path &filename);

	virtual ~Experiment();

	// Saves te Experiment to the filesystem
	// @filename the path to save too
	//
	//  Saves the <Experiment> to the filesystem. It consists only of
	//  lightweight metadata of each Ants, Identification, Measurement
	//  shapes. The actual tracking data is kept in the actual
	//  directory referred byt the TrackingDatadirectory.
	//
	// Saves the <priv::Experiment> data to the filesystem
	void Save(const fs::path &filename);

	// The absolute path of the Experiment
	// @return the absolute fs::path of the <priv::Experiment> on the
	//         filesysten
	const fs::path &AbsoluteFilePath() const override;

	// The parent dir of the Experiment
	//
	// Since <TrackingDataDirectory> are pointer to the actual data
	// directory on the filesystem, any Path is relative to this
	// <Basedir>
	// @return a fs::path to the base directory of this
	//         <priv::Experiment>.
	const fs::path &Basedir() const;

	SpacePtr CreateSpace(const std::string &name, SpaceID spaceID = 0);

	void DeleteSpace(SpaceID spaceID);

	const priv::SpaceByID &Spaces() const;

	const TrackingDataDirectoryByURI &TrackingDataDirectories() const;

	bool TrackingDataDirectoryIsDeletable(const std::string &URI) const;

	void DeleteTrackingDataDirectory(const std::string &URI);

	void AddTrackingDataDirectory(
	    const SpacePtr &space, const TrackingDataDirectoryPtr &tdd
	);

	std::pair<SpacePtr, TrackingDataDirectoryPtr>
	LocateTrackingDataDirectory(const std::string &tddURI) const;

	SpacePtr LocateSpace(const std::string &spaceName) const;

	AntPtr CreateAnt(AntID aID = 0);

	// Accessor to the underlying Identifier
	//
	// @return a reference to the underlying <Identifier>
	inline const fort::myrmidon::priv::IdentifierPtr &Identifier() const {
		return d_identifier;
	}

	// The name of the Experiment.
	//
	// @return a reference to the experiment name
	const std::string &Name() const;
	// Sets the Experiment's name.
	//
	// @name the new <priv::Experiment> name
	void               SetName(const std::string &name);

	// The author of the Experiment
	//
	// @return a reference to the author name
	const std::string &Author() const;
	// Sets the experiment's author
	//
	// @author the new value for the experiement author
	void               SetAuthor(const std::string &author);

	// Comments about the experiment
	//
	// @return a reference to the <priv::Experiment> comment
	const std::string &Comment() const;
	// Sets the comment of the Experiment
	//
	// @comment the new experiment comment
	void               SetComment(const std::string &comment);

	// The kind of tag used in the experiment
	//
	// @return the family of tag used in the experiment
	fort::tags::Family Family() const;

	// The default physical tag size
	//
	// Usually an Ant colony are tagged with a majority of tag of a
	// given size. This is this size. Some individuals (like Queens)
	// may often use a bigger tag size that should be set in their
	// Identification. This value is use for <Measurement>.
	//
	// @return the default tag size for the experiment in mm
	double DefaultTagSize() const;
	// Sets the default tag siye in mm
	//
	// @defaultTagSize the tag size in mm for the ma
	void   SetDefaultTagSize(double defaultTagSize);

	MeasurementTypePtr CreateMeasurementType(
	    const std::string &name,
	    MeasurementTypeID  MTID = NEXT_AVAILABLE_MEASUREMENT_TYPE_ID
	);

	void DeleteMeasurementType(MeasurementTypeID MTID);

	const MeasurementTypeByID &MeasurementTypes() const;

	// Adds or modifies a Measurement
	//
	// Adds a <Measurement> to the <priv::Experiment>.  Could also be
	// used to modifies an existing measurement.
	// @m the <Measurement> to add.
	void SetMeasurement(const MeasurementConstPtr &m);

	// Removes a Measurement
	//
	// @URI the URI of the measurement to remove
	void DeleteMeasurement(const std::string &URI);

	// Lists all Measurement of the experiment.
	//
	// @list a vector that will be filled with all measurements in the
	// experiment.
	const MeasurementByTagCloseUp &Measurements() const;

	// Computes all Measurement of a type for an Ant
	//
	// @result a vector that will be filled with the corresponding
	//         <ComputedMeasurement>
	// @AID the desired <Ant> designated by its <Ant::ID>
	// @type the type of measurement we are looking for.
	void ComputeMeasurementsForAnt(
	    ComputedMeasurement::List &result, AntID antID, MeasurementTypeID typeID
	) const;

	AntShapeTypePtr CreateAntShapeType(
	    const std::string &name,
	    AntShapeTypeID     TypeID = NEXT_AVAILABLE_ANT_SHAPE_TYPE_ID
	);

	void DeleteAntShapeType(AntShapeTypeID TypeID);

	const AntShapeTypeByID &AntShapeTypes() const;

	const AntShapeTypePtr &AntShapeTypesPtr() const;

	const AntMetadata::Ptr &AntMetadataPtr() const;

	AntMetadata::Key::Ptr
	SetMetaDataKey(const std::string &name, const Value &type);

	void DeleteMetaDataKey(const std::string &name);

	void
	RenameMetaDataKey(const std::string &oldName, const std::string &newName);

	void
	CloneAntShape(AntID sourceAntID, bool scaleToSize, bool overwriteShapes);

	CollisionSolverConstPtr CompileCollisionSolver(bool collisionsIgnoreZones
	) const;

	// Computes the conventional ratio beween corner size and
	// nominated tag file.
	//
	// Due to different convention in tag size denomination (ARTag tag
	// size is the black border distance, Apriltag is the overall tag
	// size). We need this function to find the right ratio. Otherwise
	// we may make 10 to 20% error when measuring Ant.
	//
	// For ARTag, this ratio should be one. For Apriltag, depending on
	// the family cracteristics, it is a number < 1.0 (0.8 for
	// 36h11/36h10, 7.0/9.0 for Standard41h12).
	// @f the considered family
	// @return the right ratio
	static double CornerWidthRatio(fort::tags::Family f);

	void EnsureAllDataIsLoaded(
	    ProgressReporter::Ptr &&progressCallback, bool fixCorruptedData
	) const;

private:
	typedef std::map<
	    MeasurementTypeID,
	    std::map<
	        TagID,
	        std::map<std::string, std::map<Time, MeasurementConstPtr>>>>
	    SortedMeasurement;

	typedef AlmostContiguousIDContainer<MeasurementTypeID, MeasurementType>
	    MeasurementTypeContainer;

	Experiment &operator=(const Experiment &) = delete;
	Experiment(const Experiment &)            = delete;

	Experiment(const fs::path &filepath);

	void CheckTDDIsDeletable(const std::string &URI) const;

	fs::path      d_absoluteFilepath;
	fs::path      d_basedir;
	UniversePtr   d_universe;
	IdentifierPtr d_identifier;

	std::string d_name;
	std::string d_author;
	std::string d_comment;
	double      d_defaultTagSize;

	MeasurementByTagCloseUp  d_measurementByURI;
	SortedMeasurement        d_measurements;
	MeasurementTypeContainer d_measurementTypes;

	AntShapeTypeContainerPtr             d_antShapeTypes;
	fort::myrmidon::priv::AntMetadataPtr d_antMetadata;
};

} // namespace priv
} // namespace myrmidon
} // namespace fort
