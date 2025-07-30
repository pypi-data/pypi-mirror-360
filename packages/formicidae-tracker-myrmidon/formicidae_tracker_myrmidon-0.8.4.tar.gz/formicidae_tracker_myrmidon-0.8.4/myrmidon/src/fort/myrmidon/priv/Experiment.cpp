#include "Experiment.hpp"

#include <sys/file.h>
#include <unistd.h>

#include <fstream>

#include <fort/myrmidon/utils/Checker.hpp>
#include <fort/myrmidon/utils/Defer.hpp>
#include <fort/myrmidon/utils/PosixCall.h>

#include <fort/myrmidon/Shapes.hpp>

#include "Ant.hpp"
#include "AntMetadata.hpp"
#include "AntPoseEstimate.hpp"
#include "AntShapeType.hpp"
#include "CollisionSolver.hpp"
#include "ExperimentReadWriter.hpp"
#include "Identifier.hpp"
#include "Measurement.hpp"
#include "Query.hpp"
#include "Space.hpp"
#include "TagCloseUp.hpp"
#include "TrackingDataDirectory.hpp"

#include <tbb/parallel_for.h>

extern "C" {
#include <libavutil/log.h>
}

namespace fort {
namespace myrmidon {
namespace priv {

Experiment::Experiment(const fs::path &filepath)
    : d_absoluteFilepath(fs::absolute(fs::weakly_canonical(filepath)))
    , d_basedir(d_absoluteFilepath.parent_path())
    , d_identifier(Identifier::Create())
    , d_universe(std::make_shared<Universe>())
    , d_defaultTagSize(1.0)
    , d_antShapeTypes(std::make_shared<AntShapeTypeContainer>()) {
	av_log_set_level(AV_LOG_QUIET);
	CreateMeasurementType("head-tail", Measurement::HEAD_TAIL_TYPE);

	auto onNameChange =
	    [this](const std::string &oldName, const std::string &newName) {
		    for (const auto &[aID, a] : d_identifier->Ants()) {
			    if (a->DataMap().count(oldName) == 0) {
				    continue;
			    }
			    AntDataMap map = a->DataMap();
			    map.insert(std::make_pair(newName, map.at(oldName)));
			    map.erase(oldName);
			    a->SetValues(map);
		    }
	    };

	auto onTypeChange =
	    [this](const std::string &name, ValueType oldType, ValueType newType) {
		    if (oldType == newType) {
			    return;
		    }
		    for (const auto &[aID, a] : d_identifier->Ants()) {
			    if (a->DataMap().count(name) == 1) {
				    throw std::runtime_error(
				        "Could not change type for key '" + name +
				        "': Ant{ID:" + a->FormattedID() +
				        "} contains timed data"
				    );
			    }
		    }
	    };

	auto onDefaultChange = [this](
	                           const std::string &name,
	                           const Value       &oldValue,
	                           const Value       &newValue
	                       ) {
		for (const auto &[aID, ant] : d_identifier->Ants()) {
			try {
				for (auto &[time, value] : ant->DataMap().at(name)) {
					if (value == oldValue) {
						value = newValue;
					}
				}
			} catch (const std::exception &) {
			}
			ant->CompileData();
		}
	};

	d_antMetadata = std::make_shared<AntMetadata>(
	    onNameChange,
	    onTypeChange,
	    onDefaultChange
	);
}

Experiment::~Experiment() {}

class ExperimentLock {
public:
	typedef std::shared_ptr<ExperimentLock> Ptr;

	ExperimentLock(const fs::path &filepath, bool shared) {

		int opts = O_RDWR;
		int lock = LOCK_EX | LOCK_NB;
		if (shared == true) {
			opts = O_RDONLY;
			lock = LOCK_SH | LOCK_NB;
		}

		d_fd = open(filepath.c_str(), opts);
		if (d_fd < 0) {
			throw MYRMIDON_SYSTEM_ERROR(open, errno);
		}

		try {
			p_call(flock, d_fd, lock);
		} catch (std::system_error &e) {
			if (e.code() != std::errc::resource_unavailable_try_again) {
				throw std::runtime_error(
				    "Could not acquire lock on '" + filepath.string() +
				    "': " + e.what()
				);
			}

			if (shared == true) {
				throw std::runtime_error(
				    "Could not acquire shared lock on '" + filepath.string() +
				    "':  another program has write access on it"
				);
			} else {
				throw std::runtime_error(
				    "Could not acquire exclusive lock on '" +
				    filepath.string() +
				    "':  another program has write or read access on it"
				);
			}
		}
	}

	~ExperimentLock() {
		flock(d_fd, LOCK_UN);
		close(d_fd);
	}

private:
	int d_fd;
};

Experiment::Ptr Experiment::Create(const fs::path &filename) {
	return std::shared_ptr<Experiment>(new Experiment(filename));
}

Experiment::Ptr Experiment::Open(const fs::path &filepath) {
	return ExperimentReadWriter::Open(filepath);
}

Experiment::Ptr Experiment::OpenDataLess(const fs::path &filepath) {
	return ExperimentReadWriter::Open(filepath, true);
}

void Experiment::Save(const fs::path &filepath) {
	auto basedir    = fs::weakly_canonical(d_absoluteFilepath).parent_path();
	auto newBasedir = fs::weakly_canonical(filepath).parent_path();
	// TODO: should not be an error.
	if (basedir != newBasedir) {
		throw std::invalid_argument(
		    "Changing experiment file directory is not yet supported"
		);
	}

	{
		std::ofstream touching;
		touching.open(filepath.c_str(), std::ios_base::app);
	}

	ExperimentReadWriter::Save(*this, filepath);
	if (filepath != d_absoluteFilepath) {
		d_absoluteFilepath = filepath;
	}
}

Space::Ptr Experiment::CreateSpace(const std::string &name, SpaceID spaceID) {
	return Universe::CreateSpace(d_universe, spaceID, name);
}

void Experiment::DeleteSpace(SpaceID spaceID) {
	d_universe->DeleteSpace(spaceID);
}

const SpaceByID &Experiment::Spaces() const {
	return d_universe->Spaces();
}

const TrackingDataDirectoryByURI &Experiment::TrackingDataDirectories() const {
	return d_universe->TrackingDataDirectories();
}

void Experiment::CheckTDDIsDeletable(const std::string &URI) const {
	auto fi = std::find_if(
	    d_measurementByURI.begin(),
	    d_measurementByURI.end(),
	    [URI](const std::pair<fs::path, MeasurementByType> &elem) -> bool {
		    if (fs::path(elem.first).lexically_relative(URI).empty() == true) {
			    return false;
		    }
		    return elem.second.empty() == false;
	    }
	);
	if (fi != d_measurementByURI.end()) {
		auto reason = "Could not remove TrackingDataDirectory '" + URI +
		              "': it contains measurement '" + fi->first + "'";
		throw std::runtime_error(reason);
	}
}

bool Experiment::TrackingDataDirectoryIsDeletable(const std::string &URI
) const {
	try {
		CheckTDDIsDeletable(URI);
	} catch (const std::exception &e) {
		return false;
	}
	return true;
}

void Experiment::DeleteTrackingDataDirectory(const std::string &URI) {
	CheckTDDIsDeletable(URI);
	d_universe->DeleteTrackingDataDirectory(URI);
}

void Experiment::AddTrackingDataDirectory(
    const Space::Ptr &space, const TrackingDataDirectory::Ptr &tdd
) {
	auto tddFamily = tdd->DetectionSettings().Family;
	auto myFamily  = Family();
	if (myFamily != tags::Family::Undefined &&
	    tddFamily != tags::Family::Undefined && myFamily != tddFamily) {
		throw std::invalid_argument(
		    "Family for TrackingDataDirectory '" + tdd->URI() + "' (" +
		    tags::GetFamilyName(tddFamily) +
		    ") does not match family of other directories (" +
		    tags::GetFamilyName(myFamily)
		);
	}
	Space::Accessor::AddTrackingDataDirectory(space, tdd);
}

const std::string &Experiment::Name() const {
	return d_name;
}

void Experiment::SetName(const std::string &name) {
	d_name = name;
}

const std::string &Experiment::Author() const {
	return d_author;
}

void Experiment::SetAuthor(const std::string &author) {
	d_author = author;
}

const std::string &Experiment::Comment() const {
	return d_comment;
}

void Experiment::SetComment(const std::string &comment) {
	d_comment = comment;
}

const fs::path &Experiment::AbsoluteFilePath() const {
	return d_absoluteFilepath;
}

const fs::path &Experiment::Basedir() const {
	return d_basedir;
}

fort::tags::Family Experiment::Family() const {
	const auto &tdds = TrackingDataDirectories();
	if (tdds.empty()) {
		return tags::Family::Undefined;
	}
	return tdds.begin()->second->DetectionSettings().Family;
}

Ant::Ptr Experiment::CreateAnt(fort::myrmidon::AntID antID) {
	return d_identifier->CreateAnt(d_antShapeTypes, d_antMetadata, antID);
}

void Experiment::SetMeasurement(const Measurement::ConstPtr &m) {
	if (d_measurementTypes.Objects().count(m->Type()) == 0) {
		throw std::out_of_range(
		    "Unknown MeasurementType::ID " + std::to_string(m->Type())
		);
	}

	auto [tddURI, frameID, tagID, mtID] = Measurement::DecomposeURI(m->URI());
	Measurement::ConstPtr oldM;

	auto fi = d_universe->TrackingDataDirectories().find(tddURI);
	if (fi == d_universe->TrackingDataDirectories().end()) {
		std::ostringstream oss;
		oss << "Unknown data directory '" << tddURI << "'";
		throw std::invalid_argument(oss.str());
	}

	auto ref = fi->second->FrameReferenceAt(frameID);

	try {
		oldM = d_measurementByURI.at(m->TagCloseUpURI()).at(m->Type());
	} catch (const std::exception &e) {
	}

	d_measurementByURI[m->TagCloseUpURI()][m->Type()]    = m;
	d_measurements[m->Type()][tagID][tddURI][ref.Time()] = m;

	if (m->Type() != Measurement::HEAD_TAIL_TYPE) {
		return;
	}

	try {
		d_identifier->SetAntPoseEstimate(std::make_shared<AntPoseEstimate>(
		    ref,
		    tagID,
		    m->EndFromTag(),
		    m->StartFromTag()
		));
	} catch (const std::exception &e) {
		if (oldM) {
			d_measurementByURI[m->TagCloseUpURI()][m->Type()]    = oldM;
			d_measurements[m->Type()][tagID][tddURI][ref.Time()] = oldM;
		} else {
			DeleteMeasurement(m->URI());
		}
		throw;
	}
}

void Experiment::DeleteMeasurement(const std::string &URI) {
	auto [tddURI, frameID, tagID, mtID] = Measurement::DecomposeURI(URI);

	auto tfi = d_universe->TrackingDataDirectories().find(tddURI);
	if (tfi == d_universe->TrackingDataDirectories().end()) {
		std::ostringstream oss;
		oss << "Unknown data directory '" << tddURI << "'";
		throw std::invalid_argument(oss.str());
	}
	auto ref = tfi->second->FrameReferenceAt(frameID);

	if (mtID == Measurement::HEAD_TAIL_TYPE) {
		d_identifier->DeleteAntPoseEstimate(std::make_shared<AntPoseEstimate>(
		    ref,
		    tagID,
		    Eigen::Vector2d(0, 0),
		    0.0
		));
	}

	auto tagCloseUpURI = TagCloseUp::FormatURI(tddURI, frameID, tagID);
	auto fi            = d_measurementByURI.find(tagCloseUpURI);
	if (fi == d_measurementByURI.end()) {
		throw std::runtime_error("Unknown measurement '" + URI + "'");
	}
	auto ffi = fi->second.find(mtID);
	if (ffi == fi->second.end()) {
		throw std::runtime_error("Unknown measurement '" + URI + "'");
	}
	fi->second.erase(ffi);
	if (fi->second.empty()) {
		d_measurementByURI.erase(fi);
	}
	auto sfi = d_measurements.find(mtID);
	if (sfi == d_measurements.end()) {
		throw std::logic_error("Sorting error");
	}
	auto sffi = sfi->second.find(tagID);
	if (sffi == sfi->second.end()) {
		throw std::logic_error("Sorting error");
	}
	auto sfffi = sffi->second.find(tddURI);
	if (sfffi == sffi->second.end()) {
		throw std::logic_error("Sorting error");
	}
	auto sffffi = sfffi->second.find(ref.Time());
	if (sffffi == sfffi->second.end()) {
		throw std::logic_error("Sorting error");
	}

	sfffi->second.erase(sffffi);
	if (sfffi->second.empty() == false) {
		return;
	}
	sffi->second.erase(sfffi);
	if (sffi->second.empty() == false) {
		return;
	}
	sfi->second.erase(sffi);
	if (sfi->second.empty() == false) {
		return;
	}
	d_measurements.erase(sfi);
}

const Experiment::MeasurementByTagCloseUp &Experiment::Measurements() const {
	return d_measurementByURI;
}

double Experiment::DefaultTagSize() const {
	return d_defaultTagSize;
}

void Experiment::SetDefaultTagSize(double defaultTagSize) {
	d_defaultTagSize = defaultTagSize;
}

double Experiment::CornerWidthRatio(tags::Family f) {
	if (f == tags::Family::Tag36ARTag) {
		return 1.0;
	}

	static std::map<tags::Family, double> cache;
	auto                                  fi = cache.find(f);
	if (fi != cache.end()) {
		return fi->second;
	}
	auto [familyConstructor, familyDestructor] = tags::GetFamily(f);
	auto  familyDefinition                     = familyConstructor();
	Defer cleanup([familyDefinition = familyDefinition,
	               familyDestructor = familyDestructor]() {
		familyDestructor(familyDefinition);
	});
	auto  res = double(familyDefinition->width_at_border) /
	           double(familyDefinition->total_width);
	cache[f] = res;
	return res;
}

void Experiment::ComputeMeasurementsForAnt(
    std::vector<ComputedMeasurement> &result,
    myrmidon::AntID                   antID,
    MeasurementType::ID               typeID
) const {
	auto afi = d_identifier->Ants().find(antID);
	if (afi == d_identifier->Ants().cend()) {
		throw std::out_of_range("Unknown AntID " + std::to_string(antID));
	}
	result.clear();
	double cornerWidthRatio;
	try {
		cornerWidthRatio = CornerWidthRatio(Family());
	} catch (const std::invalid_argument &e) {
		return;
	}

	auto typedMeasurement = d_measurements.find(typeID);
	if (typedMeasurement == d_measurements.cend()) {
		return;
	}

	for (const auto &ident : afi->second->Identifications()) {
		double tagSizeMM = d_defaultTagSize;
		if (ident->UseDefaultTagSize() == false) {
			tagSizeMM = ident->TagSize();
		}
		tagSizeMM *= cornerWidthRatio;

		auto measurementsByTDD =
		    typedMeasurement->second.find(ident->TagValue());
		if (measurementsByTDD == typedMeasurement->second.cend()) {
			continue;
		}

		for (const auto &measurements : measurementsByTDD->second) {
			auto start = measurements.second.cbegin();
			if (ident->Start().IsSinceEver() == false) {
				start = measurements.second.lower_bound(ident->Start());
			}

			auto end = measurements.second.cend();
			if (ident->End().IsForever() == false) {
				end = measurements.second.upper_bound(ident->End());
			}
			for (; start != end; ++start) {
				double distancePixel = (start->second->StartFromTag() -
				                        start->second->EndFromTag())
				                           .norm();
				double distanceMM =
				    distancePixel * tagSizeMM / start->second->TagSizePx();
				result.push_back(ComputedMeasurement{
				    .Time        = start->first,
				    .LengthMM    = distanceMM,
				    .LengthPixel = distancePixel,
				});
			}
		}
	}
}

MeasurementType::Ptr Experiment::CreateMeasurementType(
    const std::string &name, MeasurementType::ID MTID
) {
	return d_measurementTypes.CreateObject(
	    [&name](MeasurementType::ID MTID) {
		    return std::make_shared<MeasurementType>(MTID, name);
	    },
	    MTID
	);
}

void Experiment::DeleteMeasurementType(MeasurementType::ID MTID) {
	auto fi = d_measurementTypes.Objects().find(MTID);
	if (d_measurements.count(MTID) != 0) {
		throw std::runtime_error(
		    "Could not remove MeasurementTypeID '" + fi->second->Name() +
		    "' has experiment still contains measurement"
		);
	}

	if (MTID == Measurement::HEAD_TAIL_TYPE) {
		throw std::invalid_argument(
		    "Could not remove default measurement type 'head-tail'"
		);
	}
	try {
		d_measurementTypes.DeleteObject(MTID);
	} catch (const MeasurementTypeContainer::UnmanagedObject &) {
		throw std::out_of_range(
		    "Unknown MeasurementTypeID " + std::to_string(MTID)
		);
	}
}

const MeasurementTypeByID &Experiment::MeasurementTypes() const {
	return d_measurementTypes.Objects();
}

std::pair<Space::Ptr, TrackingDataDirectoryPtr>
Experiment::LocateTrackingDataDirectory(const std::string &tddURI) const {
	return d_universe->LocateTrackingDataDirectory(tddURI);
}

Space::Ptr Experiment::LocateSpace(const std::string &spaceName) const {
	return d_universe->LocateSpace(spaceName);
}

AntShapeType::Ptr
Experiment::CreateAntShapeType(const std::string &name, AntShapeTypeID typeID) {
	return d_antShapeTypes->Create(name, typeID);
}

void Experiment::DeleteAntShapeType(AntShapeTypeID typeID) {
	auto fi = d_antShapeTypes->Find(typeID);
	if (fi == d_antShapeTypes->End()) {
		throw std::out_of_range(
		    "Unknown AntShapeTypeID " + std::to_string(typeID)
		);
	}

	for (const auto &[aID, a] : d_identifier->Ants()) {
		for (const auto &[type, c] : a->Capsules()) {
			if (type == typeID) {
				throw std::runtime_error(
				    "Could not delete AntShapeType{ID:" +
				    std::to_string(fi->first) + ", Name:'" +
				    fi->second->Name() + "'}: Ant{ID:" + FormatAntID(aID) +
				    "} has a capsule of this type"
				);
			}
		}
	}
	d_antShapeTypes->Delete(typeID);
}

const AntShapeTypeByID &Experiment::AntShapeTypes() const {
	return d_antShapeTypes->Types();
}

const fort::myrmidon::priv::AntMetadataPtr &Experiment::AntMetadataPtr() const {
	return d_antMetadata;
}

AntMetadata::Key::Ptr
Experiment::SetMetaDataKey(const std::string &name, const Value &defaultValue) {
	auto res = AntMetadata::SetKey(d_antMetadata, name, defaultValue);
	for (const auto &[antID, ant] : d_identifier->Ants()) {
		ant->CompileData();
	}
	return res;
}

void Experiment::DeleteMetaDataKey(const std::string &key) {
	for (const auto &[aID, a] : d_identifier->Ants()) {
		if (a->DataMap().count(key) != 0) {
			throw std::runtime_error(
			    "Cannot remove metadata key '" + key +
			    "': Ant{ID:" + FormatAntID(aID) + "} contains timed data"
			);
		}
	}

	d_antMetadata->Delete(key);

	for (const auto &[aID, a] : d_identifier->Ants()) {
		a->CompileData();
	}
}

void Experiment::RenameMetaDataKey(
    const std::string &oldName, const std::string &newName
) {
	auto fi = d_antMetadata->Keys().find(oldName);
	if (fi == d_antMetadata->Keys().end()) {
		throw std::out_of_range("Unknown key '" + oldName + "'");
	}
	fi->second->SetName(newName);
}

void Experiment::CloneAntShape(
    fort::myrmidon::AntID sourceAntID, bool scaleToSize, bool overwriteShapes
) {
	auto sourceIt = d_identifier->Ants().find(sourceAntID);
	if (sourceIt == d_identifier->Ants().cend()) {
		throw std::out_of_range("Cannot find ant " + FormatAntID(sourceAntID));
	}

	auto source = sourceIt->second;
	if (source->Capsules().empty() && overwriteShapes == false) {
		return;
	}

	auto computeSize = [this](fort::myrmidon::AntID antID) -> double {
		std::vector<ComputedMeasurement> measurements;
		try {
			ComputeMeasurementsForAnt(
			    measurements,
			    antID,
			    Measurement::HEAD_TAIL_TYPE
			);
		} catch (const std::exception &e) {
			return 0.0;
		}
		double res = 0.0;
		for (const auto &m : measurements) {
			res += m.LengthMM / measurements.size();
		}
		return res;
	};

	double baseSize = computeSize(sourceAntID);
	if (baseSize == 0.0 && scaleToSize == true) {
		throw std::runtime_error(
		    "Ant " + FormatAntID(sourceAntID) + " has a size of zero"
		);
	}
	for (const auto &[aID, ant] : d_identifier->Ants()) {
		if (aID == sourceAntID ||
		    (overwriteShapes == false && ant->Capsules().empty() == false)) {
			continue;
		}
		ant->ClearCapsules();
		double scale = 1.0;
		if (scaleToSize == true) {
			double antSize = computeSize(aID);
			if (antSize > 0.0) {
				scale = antSize / baseSize;
			}
		}
		for (const auto &[typeID, sourceCapsule] : source->Capsules()) {
			auto destCapsule = std::make_shared<Capsule>(
			    scale * sourceCapsule->C1(),
			    scale * sourceCapsule->C2(),
			    scale * sourceCapsule->R1(),
			    scale * sourceCapsule->R2()
			);
			ant->AddCapsule(typeID, std::move(destCapsule));
		}
	}
}

CollisionSolver::ConstPtr
Experiment::CompileCollisionSolver(bool collisionsIgnoreZones) const {
	return std::make_shared<CollisionSolver>(
	    d_universe->Spaces(),
	    d_identifier->Ants(),
	    collisionsIgnoreZones
	);
}

void Experiment::EnsureAllDataIsLoaded(
    ProgressReporter::Ptr &&progress, bool fixCorruptedData
) const {
	std::vector<TrackingDataDirectory::Loader> loaders;

	for (const auto &[URI, tdd] : TrackingDataDirectories()) {
		std::vector<std::vector<TrackingDataDirectory::Loader>> toLoad;

		if (!tdd->TagCloseUpsComputed()) {
			toLoad.push_back(tdd->PrepareTagCloseUpsLoaders());
		}
		if (!tdd->TagStatisticsComputed()) {
			toLoad.push_back(tdd->PrepareTagStatisticsLoaders());
		}
		if (!tdd->FullFramesComputed()) {
			toLoad.push_back(tdd->PrepareFullFramesLoaders());
		}

		for (auto c : toLoad) {
			loaders.insert(loaders.end(), c.begin(), c.end());
		}
	}
	Query::ProcessLoaders(loaders, std::move(progress), fixCorruptedData);
}

} // namespace priv
} // namespace myrmidon
} // namespace fort
