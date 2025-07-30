#include "TagStatistics.hpp"

#include <fort/hermes/FileContext.hpp>
#include <fort/hermes/Error.hpp>

#include "Typedefs.hpp"
#include "DenseMap.hpp"
#include "TimeUtils.hpp"

#include "TrackingDataDirectoryError.hpp"

namespace fort {
namespace myrmidon {
namespace priv {


TagStatistics TagStatisticsHelper::Create(TagID tagID,const Time & firstTime) {
	TagStatistics res;
	res.ID = tagID;
	res.FirstSeen = firstTime;
	res.LastSeen= firstTime;
	res.Counts = Eigen::Matrix<uint64_t ,Eigen::Dynamic,1>(10);
	res.Counts.setZero();
	res.Counts(TagStatistics::TOTAL_SEEN) = 1;
	return res;
}

TagStatistics::CountHeader TagStatisticsHelper::ComputeGap(const Time & lastSeen, const Time & currentTime) {

	const static std::map<int64_t,TagStatistics::CountHeader> gapBounds
		= {
		   {0,TagStatistics::CountHeader(0)},
		   {(500 * Duration::Millisecond).Nanoseconds(),TagStatistics::GAP_500MS},
		   {(  1 * Duration::Second).Nanoseconds(), TagStatistics::GAP_1S},
		   {( 10 * Duration::Second).Nanoseconds(), TagStatistics::GAP_10S},
		   {(  1 * Duration::Minute).Nanoseconds(), TagStatistics::GAP_1M},
		   {( 10 * Duration::Minute).Nanoseconds(), TagStatistics::GAP_10M},
		   {(  1 * Duration::Hour).Nanoseconds(), TagStatistics::GAP_1H},
		   {( 10 * Duration::Hour).Nanoseconds(), TagStatistics::GAP_10H},
	};
	Duration gap = currentTime.Sub(lastSeen);
	auto fi = gapBounds.upper_bound(gap.Nanoseconds());
	if ( fi == gapBounds.end() ) {
		return TagStatistics::GAP_MORE;
	}
	return fi->second;
}



std::tuple<TagStatisticsHelper::Timed,FixableError::Ptr>
TagStatisticsHelper::BuildStats(const std::string & hermesFile) {
	Timed res;


	auto & stats = res.TagStats;
	hermes::FileContext file(hermesFile,false);
	hermes::FrameReadout ro;

	struct LastSeen {
		priv::FrameID FrameID;
		Time          FrameTime;
	};


	std::map<TagID,LastSeen> lastSeens;
	bool hasStart = false;
	FrameID last = 0;
	for (;;) {
		try {
			file.Read(&ro);
			last = ro.frameid();
		} catch ( const fort::hermes::EndOfFile & ) {
			for ( const auto & [tagID,last] : lastSeens ) {
				if ( last.FrameTime < res.End ) {
					UpdateGaps(stats.at(tagID),last.FrameTime,res.End);
				}
			}

			return {res,nullptr};

		} catch ( const hermes::UnexpectedEndOfFileSequence & e ) {
			return {res,
			        std::make_unique<CorruptedHermesFileError>("Could not fully read '"
			                                                   + hermesFile + "'",
			                                                   hermesFile,
			                                                   last)};

		} catch ( const std::exception & e ) {
			throw std::runtime_error("Could not build statistic for '"
			                         + hermesFile + "':" + e.what());
		}
		FrameID current = ro.frameid();

		// current time stripped from any monotonic data
		auto currentTime = TimeFromFrameReadout(ro,1).Round(1);
		if ( hasStart == false ) {
			hasStart = true;
			res.Start = currentTime;
		}

		res.End = currentTime;
		for ( const auto & tag : ro.tags() ) {
			auto key = tag.id();
			if ( stats.count(key) == 0 ) {
				lastSeens.insert(std::make_pair(key,LastSeen{current,currentTime}));
				auto tagStats = TagStatisticsHelper::Create(tag.id(),currentTime);
				if ( currentTime > res.Start ) {
					UpdateGaps(tagStats,res.Start,currentTime);
				}
				stats.insert(std::make_pair(key,tagStats));
			} else {
				auto & last = lastSeens.at(key);
				auto & tagStats = stats.at(key);
				if ( last.FrameID == current ) {
					tagStats.Counts(TagStatistics::CountHeader::MULTIPLE_SEEN) += 1;
				} else {
					tagStats.Counts(TagStatistics::CountHeader::TOTAL_SEEN) += 1;
					if ( last.FrameID < current-1) {
						UpdateGaps(tagStats,last.FrameTime,currentTime);
					}
					tagStats.LastSeen = currentTime;
				}
				last.FrameID = current;
				last.FrameTime = currentTime;
			}
		}
	}
}
void TagStatisticsHelper::UpdateGaps(TagStatistics & stats,
                                     const Time & lastSeen,
                                     const Time & currentTime) {
	auto gap = ComputeGap(lastSeen,currentTime);
	if ( gap < TagStatistics::GAP_500MS ) {
		return;
	}
	stats.Counts(gap) += 1;
}

void TagStatisticsHelper::Merge(Timed & stats, const Timed & other) {

	if ( stats.End > other.Start ) {
		throw std::runtime_error("Could ony merge time-upward");
	}
	for ( const auto & [tagID,tagStats] : other.TagStats ) {
		auto fi = stats.TagStats.find(tagID);
		if ( fi == stats.TagStats.end() ) {
			stats.TagStats.insert(std::make_pair(tagID,tagStats));
		} else {
			fi->second = MergeTimed(fi->second,stats.End,tagStats,other.Start);
		}
	}
	stats.End = other.End;
}

void TagStatisticsHelper::Merge(TagStatistics::ByTagID & stats, const TagStatistics::ByTagID & other) {
	for ( const auto & [tagID,tagStats] : other ) {
		auto fi = stats.find(tagID);
		if ( fi == stats.end() ) {
			stats.insert(std::make_pair(tagID,tagStats));
		} else {
			fi->second = MergeSpaced(fi->second,tagStats);
		}
	}
}


TagStatistics
TagStatisticsHelper::MergeTimed(const TagStatistics & old, const Time & oldEnd,
                                const TagStatistics & newer, const Time & newerStart) {
	if ( old.ID != newer.ID ) {
		throw std::invalid_argument("Mismatched ID "
		                            + std::to_string(newer.ID)
		                            + " (expected:" + std::to_string(old.ID) + ")");
	}


	if ( oldEnd > newerStart ) {
		throw std::runtime_error("Older statistics must happen after newer one");
	}
	TagStatistics res(old);
	res.Counts += newer.Counts;
	bool computeNew = false;
	if ( newer.FirstSeen > newerStart ) {
		res.Counts(ComputeGap(newerStart,newer.FirstSeen)) -= 1;
		computeNew = true;
	}
	if ( res.LastSeen < oldEnd ) {
		res.Counts(ComputeGap(old.LastSeen,oldEnd)) -= 1;
		computeNew = true;
	}
	if ( computeNew ==  true ) {
		res.Counts(ComputeGap(old.LastSeen,newer.FirstSeen)) += 1;
	}

	res.LastSeen = newer.LastSeen;
	return res;
}

TagStatistics TagStatisticsHelper::MergeSpaced(const TagStatistics & a, const TagStatistics & b) {
	if ( a.ID != b.ID ) {
		throw std::invalid_argument("Mismatched ID "
		                            + std::to_string(a.ID)
		                            + " (expected:" + std::to_string(b.ID) + ")");
	}
	TagStatistics res(a);
	res.Counts += b.Counts;
	res.LastSeen = a.LastSeen > b.LastSeen ? a.LastSeen : b.LastSeen;
	res.FirstSeen = a.FirstSeen < b.FirstSeen ? a.FirstSeen : b.FirstSeen;
	return res;
}


} // namespace priv
} // namespace myrmidon
} // namespace fort
