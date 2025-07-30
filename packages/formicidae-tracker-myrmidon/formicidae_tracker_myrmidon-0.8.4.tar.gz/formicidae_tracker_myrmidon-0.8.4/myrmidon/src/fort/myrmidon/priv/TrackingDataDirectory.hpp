#pragma once

#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <tuple>
#include <utility>

#include <fort/tags/options.hpp>

#include <fort/hermes/FileContext.hpp>

#include <fort/myrmidon/types/FixableError.hpp>
#include <fort/myrmidon/utils/FileSystem.hpp>

#include "ForwardDeclaration.hpp"
#include "MovieSegment.hpp"
#include "SegmentIndexer.hpp"
#include "TagStatistics.hpp"
#include "TimeValid.hpp"

namespace fort {
namespace myrmidon {

namespace pb {
class TrackingDataDirectory;
}

namespace priv {

// Reference to a directory containing tracking data
//
// This object references an actuakl directory on the filesystem that
// contains the tracking data.
//
// Each directory has a start and end time and a start and end frame
class TrackingDataDirectory
    : public TimeValid,
      public FileSystemLocatable,
      public Identifiable,
      public std::enable_shared_from_this<TrackingDataDirectory> {
public:
	using Ptr = std::shared_ptr<TrackingDataDirectory>;

	typedef int32_t                              UID;
	typedef SegmentIndexer<std::string>          TrackingIndex;
	typedef SegmentIndexer<MovieSegmentConstPtr> MovieIndex;
	typedef std::map<FrameID, FrameReference>    FrameReferenceCache;
	typedef std::shared_ptr<const FrameReferenceCache>
	    FrameReferenceCacheConstPtr;

	typedef std::pair<fs::path, std::shared_ptr<TagID>> TagCloseUpFileAndFilter;
	typedef std::multimap<FrameID, TagCloseUpFileAndFilter> TagCloseUpListing;

	typedef std::function<void(int, int)> ProgressCallback;

	class const_iterator {
	public:
		const_iterator(const Ptr &tdd, uint64_t current);

		const_iterator &operator=(const const_iterator &other);
		const_iterator(const const_iterator &other);

		const_iterator &operator=(const_iterator &&other);
		const_iterator(const_iterator &&other);

		const_iterator &operator++();
		bool            operator==(const const_iterator &other) const;
		bool            operator!=(const const_iterator &other) const;

		FrameID Index() const;

		const RawFrameConstPtr &operator*();
		using difference_type   = int64_t;
		using value_type        = RawFrameConstPtr;
		using pointer           = const RawFrameConstPtr *;
		using reference         = const RawFrameConstPtr &;
		using iterator_category = std::forward_iterator_tag;

		//	private:
		friend class TrackingDataDirectory;
		const static RawFrameConstPtr NULLPTR;

		void OpenAt(uint64_t frameID);

		Ptr LockParent() const;

		std::weak_ptr<TrackingDataDirectory> d_parent;
		FrameID                              d_current;

		std::unique_ptr<fort::hermes::FileContext> d_file;
		fort::hermes::FrameReadout                 d_message;
		RawFrameConstPtr                           d_frame;
	};

	static UID GetUID(const fs::path &absoluteFilePath);

	static TagCloseUpListing ListTagCloseUpFiles(const fs::path &subdir);

	// Opens an actual TrackingDataDirectory on the filesystem
	// @path path to the tracking data directory.
	// @experimentRoot root of the <Experiment>
	// @return a new <trackingDataDirectory> with all field populated
	// accordingly
	//
	// Opens an actual TrackingDataDirectory on the filesystem, and
	// populate its data form its actual content. This function will
	// look for tracking data file open the first and last segment to
	// obtain infoirmation on the first and last frame.
	static std::tuple<TrackingDataDirectory::Ptr, FixableErrorList> Open(
	    const fs::path         &TDpath,
	    const fs::path         &experimentRoot,
	    const ProgressCallback &progress = [](int, int) {}
	);

	static TrackingDataDirectory::Ptr Create(
	    const std::string                 &uri,
	    const fs::path                    &absoluteFilePath,
	    uint64_t                           startFrame,
	    uint64_t                           endFrame,
	    const Time	                    &start,
	    const Time	                    &end,
	    const TrackingIndex::Ptr          &segments,
	    const MovieIndex::Ptr             &movies,
	    const FrameReferenceCacheConstPtr &referenceCache
	);

	virtual ~TrackingDataDirectory();

	inline UID GetUID() const {
		return d_uid;
	}

	// The directory path designator
	//
	// Gets the path designating the TrackingDataDirectory
	// @return a path relative to the experiment <Experiment>
	const std::string &URI() const override;

	// The directory absolute path
	//
	// Gets the actual path on the filesystem of the TrackingDataDirectory
	// @return the actual path on the filesystem
	const fs::path &AbsoluteFilePath() const override;

	// Gets the first frame number.
	//
	// @return the first <FrameID> in this directory
	FrameID StartFrame() const;

	// Gets the last frame number
	//
	// @return the last <FrameID> in this directory
	FrameID EndFrame() const;

	// Gets the time of the first frame in this directory
	// @return the time of the first frame in this directory
	const Time &Start() const;

	// Gets the time of the last frame in this directory
	// @return the time of the last frame in this directory
	const Time &End() const;

	const_iterator begin() const;

	const_iterator end() const;

	const_iterator FrameAt(FrameID frameID) const;

	const_iterator FrameAfter(const Time &t) const;

	FrameReference FrameReferenceAt(FrameID frameID) const;

	FrameReference FrameReferenceAfter(const Time &t) const;

	const TrackingIndex &TrackingSegments() const;

	const MovieIndex &MovieSegments() const;

	const FrameReferenceCache &ReferenceCache() const;

	class ComputedRessourceUnavailable : public std::runtime_error {
	public:
		ComputedRessourceUnavailable(const std::string &typeName) noexcept;
		virtual ~ComputedRessourceUnavailable() noexcept;
	};

	const std::vector<TagCloseUpConstPtr>    &TagCloseUps() const;
	const std::map<FrameReference, fs::path> &FullFrames() const;
	const TagStatisticsHelper::Timed         &TagStatistics() const;

	bool TagCloseUpsComputed() const;
	bool TagStatisticsComputed() const;
	bool FullFramesComputed() const;

	typedef std::function<FixableError::Ptr()> Loader;

	std::vector<Loader> PrepareTagCloseUpsLoaders();
	std::vector<Loader> PrepareTagStatisticsLoaders();
	std::vector<Loader> PrepareFullFramesLoaders();

	const tags::ApriltagOptions &DetectionSettings() const;

	std::pair<const_iterator, const_iterator>
	IteratorRange(const Time &start, const Time &end);

	static std::vector<std::pair<const_iterator, const_iterator>>
	IteratorRanges(
	    const std::vector<Ptr> &list, const Time &start, const Time &end
	);

	void SaveToCache() const;

private:
	typedef std::pair<FrameID, Time> TimedFrame;
	typedef std::map<Time, FrameID>  FrameIDByTime;

	friend class FullFramesReducer;
	friend class TagCloseUpsReducer;
	friend class TagStatisticsReducer;

	static void
	CheckPaths(const fs::path &path, const fs::path &experimentRoot);

	static std::tuple<
	    std::vector<fs::path>,
	    std::map<uint32_t, std::pair<fs::path, fs::path>>>
	LookUpFiles(const fs::path &absoluteFilePath);

	static MovieSegment::List LoadMovieSegments(
	    const std::map<uint32_t, std::pair<fs::path, fs::path>> &moviesPaths,
	    const std::string	                                   &parentURI
	);

	static TrackingDataDirectory::Ptr
	LoadFromCache(const fs::path &absoluteFilePath, const std::string &URI);

	static std::tuple<TimedFrame, TimedFrame, FixableError::Ptr> BuildIndexes(
	    const std::string           &URI,
	    Time::MonoclockID            monoID,
	    const std::vector<fs::path> &hermesFile,
	    const TrackingIndex::Ptr    &trackingIndexer
	);

	static void BuildFrameReferenceCache(
	    const std::string             &URI,
	    Time::MonoclockID              monoID,
	    const fs::path                &tddPath,
	    const TrackingIndex::ConstPtr &trackingIndexer,
	    FrameReferenceCache           &cache,
	    const ProgressCallback        &progress,
	    FixableErrorList              &errors
	);

	static std::tuple<Ptr, FixableErrorList> OpenFromFiles(
	    const fs::path         &absoluteFilePath,
	    const std::string      &URI,
	    const ProgressCallback &progress
	);

	TrackingDataDirectory(
	    const std::string                 &uri,
	    const fs::path                    &absoluteFilePath,
	    uint64_t                           startFrame,
	    uint64_t                           endFrame,
	    const Time	                    &start,
	    const Time	                    &end,
	    const TrackingIndex::Ptr          &segments,
	    const MovieIndex::Ptr             &movies,
	    const FrameReferenceCacheConstPtr &referenceCache
	);

	std::shared_ptr<std::map<FrameReference, fs::path>>
	EnumerateFullFrames(const fs::path &subpath) const noexcept;

	void LoadComputedFromCache();

	void LoadDetectionSettings();

	fs::path    d_absoluteFilePath;
	std::string d_URI;
	FrameID     d_startFrame, d_endFrame;
	UID         d_uid;

	TrackingIndex::Ptr          d_segments;
	MovieIndex::Ptr             d_movies;
	FrameReferenceCacheConstPtr d_referencesByFID;
	FrameIDByTime               d_frameIDByTime;
	tags::ApriltagOptions       d_detectionSettings;

	// cached data
	std::shared_ptr<std::vector<TagCloseUpConstPtr>>    d_tagCloseUps;
	std::shared_ptr<std::map<FrameReference, fs::path>> d_fullFrames;
	std::shared_ptr<TagStatisticsHelper::Timed>         d_tagStatistics;
};

std::ostream &operator<<(
    std::ostream &out, const fort::myrmidon::priv::TrackingDataDirectory &a
);

} // namespace priv
} // namespace myrmidon
} // namespace fort
