#include "TDDCache.hpp"




#include <fort/myrmidon/utils/NotYetImplemented.hpp>
#include <fort/myrmidon/utils/Checker.hpp>

#include "IOUtils.hpp"


namespace fort {
namespace myrmidon {
namespace priv {
namespace proto {

const std::string TDDCache::CACHE_FILENAME = "myrmidon-tdd-pb.cache";
const uint32_t TDDCache::CACHE_VERSION = 2;
TrackingDataDirectory::Ptr TDDCache::Load(const fs::path & absoluteFilePath ,
                                          const std::string & URI) {

	FORT_MYRMIDON_CHECK_PATH_IS_ABSOLUTE(absoluteFilePath);

	Time::MonoclockID monoID = TrackingDataDirectory::GetUID(absoluteFilePath);
	FrameReference start,end;
	auto ti = std::make_shared<TrackingDataDirectory::TrackingIndex>();
	auto mi = std::make_shared<TrackingDataDirectory::MovieIndex>();
	auto cache = std::make_shared<TrackingDataDirectory::FrameReferenceCache>();

	auto cachePath = absoluteFilePath / CACHE_FILENAME;

	ReadWriter::Read(cachePath,
	                 [&start,&end,URI,monoID](const pb::TrackingDataDirectory & pb) {
		                 if ( pb.cacheversion() != CACHE_VERSION) {
			                 throw std::runtime_error("Cache file has wrong version '"
			                                          + std::to_string(pb.cacheversion())
			                                          + "' expected '"
			                                          + std::to_string(CACHE_VERSION)
			                                          + "'");
		                 }
		                 IOUtils::LoadFrameReference(&start,pb.start(),URI,monoID);
		                 IOUtils::LoadFrameReference(&end,pb.end(),URI,monoID);
	                 },
	                 [=](const pb::TrackingDataDirectoryFileLine & line) {
		                 if ( line.has_movie() == true ) {
			                 if ( line.has_moviestarttime() == false ) {
				                 throw std::runtime_error("Movie is missing start time");
			                 }
			                 auto movieStartTime = IOUtils::LoadTime(line.moviestarttime(),monoID);
			                 auto ms = IOUtils::LoadMovieSegment(line.movie(),
			                                                     absoluteFilePath,
			                                                     URI);
			                 mi->Insert(FrameReference(URI,ms->StartFrame(),movieStartTime),ms);
		                 }
		                 if ( line.has_segment() == true ) {
			                 TrackingDataDirectory::TrackingIndex::Segment s;
			                 IOUtils::LoadTrackingIndexSegment(&s,
			                                                   line.segment(),
			                                                   URI,
			                                                   monoID);
			                 ti->Insert(s);
		                 }
		                 if ( line.has_cachedframe() == true ) {
			                 FrameReference ref;
			                 IOUtils::LoadFrameReference(&ref,line.cachedframe(),URI,monoID);
			                 cache->insert(std::make_pair(ref.FrameID(),ref));
		                 }
	                 });

	return TrackingDataDirectory::Create(URI,
	                                     absoluteFilePath,
	                                     start.FrameID(),
	                                     end.FrameID(),
	                                     start.Time(),
	                                     end.Time(),
	                                     ti,
	                                     mi,
	                                     cache);
}

void TDDCache::Save(const TrackingDataDirectory::Ptr & tdd) {
	auto cachePath = tdd->AbsoluteFilePath() / CACHE_FILENAME;

	pb::TrackingDataDirectory h;
	IOUtils::SaveFrameReference(h.mutable_start(),
	                            FrameReference(tdd->URI(),
	                                           tdd->StartFrame(),
	                                           tdd->Start()));
	IOUtils::SaveFrameReference(h.mutable_end(),
	                            FrameReference(tdd->URI(),
	                                           tdd->EndFrame(),
	                                           tdd->End()));
	h.set_cacheversion(CACHE_VERSION);
	std::vector<std::function<void (pb::TrackingDataDirectoryFileLine &)> > lines;

	for ( const auto & ts : tdd->TrackingSegments().Segments() ) {
		lines.push_back([ts,tdd](pb::TrackingDataDirectoryFileLine & line){
			                IOUtils::SaveTrackingIndexSegment(line.mutable_segment(),
			                                                  ts);
		                });
	}

	for ( const auto & ms : tdd->MovieSegments().Segments() ) {
		lines.push_back([ms,tdd](pb::TrackingDataDirectoryFileLine & line){
			                IOUtils::SaveMovieSegment(line.mutable_movie(),
			                                          *ms.second,
			                                          tdd->AbsoluteFilePath());
			                IOUtils::SaveTime(line.mutable_moviestarttime(),
			                                  ms.first.Time());
		                });
	}

	for ( const auto & [frameID,ref] : tdd->ReferenceCache() ) {
		lines.push_back([ref= std::ref(ref) ](pb::TrackingDataDirectoryFileLine & line){
			                IOUtils::SaveFrameReference(line.mutable_cachedframe(),
			                                            ref);
		                });
	}

	ReadWriter::Write(cachePath,
	                  h,
	                  lines);
}


} //namespace proto
} //namespace priv
} //namespace myrmidon
} //namespace fort
