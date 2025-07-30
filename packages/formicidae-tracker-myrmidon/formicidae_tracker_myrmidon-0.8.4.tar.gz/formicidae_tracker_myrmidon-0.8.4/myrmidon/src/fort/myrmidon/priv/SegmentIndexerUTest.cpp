#include <gtest/gtest.h>

#include "SegmentIndexer.hpp"

namespace fort {
namespace myrmidon {
namespace priv {

class SegmentIndexerUTest : public ::testing::Test {
protected:
	void SetUp() {
		for(size_t i = 0; i < 10; ++i) {
			std::ostringstream os;
			os << i;
			d_testdata.push_back(std::make_pair(FrameReference("",10*i+1,Time::FromTimeT(10*i+1)),os.str()));
		}

		EXPECT_NO_THROW({
				for(const auto & d : d_testdata) {
					d_si.Insert(d.first,d.second);
				}
			});

	}
	std::vector<fort::myrmidon::priv::SegmentIndexer<std::string>::Segment> d_testdata;
	fort::myrmidon::priv::SegmentIndexer<std::string> d_si;
};


TEST_F(SegmentIndexerUTest,CanStoreAnIndex) {


	std::vector<SegmentIndexer<std::string>::Segment> res;
	EXPECT_NO_THROW({
			res = d_si.Segments();
		});

	ASSERT_EQ(res.size(),d_testdata.size());
	for(size_t i =0 ; i < res.size(); ++i ){
		EXPECT_EQ(res[i].first.FrameID(),d_testdata[i].first.FrameID()) << " for segment " << i;
		EXPECT_TRUE(res[i].first.Time().Equals(d_testdata[i].first.Time())) << " for segment " << i;
		EXPECT_EQ(res[i].second,d_testdata[i].second) << " for segment " << i;
	}

}


TEST_F(SegmentIndexerUTest,CanFindSegment) {
	struct TestData {
		uint64_t F;
		std::string Expected;
	};

	std::vector<TestData> data
		= {
		   {1,"0"},
		   {10,"0"},
		   {11,"1"},
		   {42,"4"},
		   {1001,"9"},
	};

	for(const auto & d : data) {
		std::pair<FrameReference,std::string> res;
		EXPECT_NO_THROW({
				res = d_si.Find(Time::FromTimeT(d.F));
			});
		EXPECT_EQ(res.second,d.Expected);
		EXPECT_NO_THROW({
				res = d_si.Find(d.F);
			});
		EXPECT_EQ(res.second,d.Expected);
	}

	EXPECT_THROW({
			auto res = d_si.Find(0);
		},std::out_of_range);

	EXPECT_THROW({
			auto res = d_si.Find(Time::FromTimeT(0));
		},std::out_of_range);

}


TEST_F(SegmentIndexerUTest,EnforceIncreasingInvariant) {
	SegmentIndexer<std::string> si;
	EXPECT_NO_THROW(si.Insert(FrameReference("",1,Time::FromTimeT(1)),"0"));
	EXPECT_NO_THROW(si.Insert(FrameReference("",11,Time::FromTimeT(11)),"1"));
	EXPECT_THROW({si.Insert(FrameReference("",21,Time::FromTimeT(6)),"2");},std::invalid_argument);
	EXPECT_THROW({si.Insert(FrameReference("",6,Time::FromTimeT(21)),"2");},std::invalid_argument);
	// It is permitted to make two segment have the same end value
	EXPECT_NO_THROW(si.Insert(FrameReference("",21,Time::FromTimeT(21)),"0"));

}

} // namespace priv
} // namespace myrmidon
} // namespace fort
