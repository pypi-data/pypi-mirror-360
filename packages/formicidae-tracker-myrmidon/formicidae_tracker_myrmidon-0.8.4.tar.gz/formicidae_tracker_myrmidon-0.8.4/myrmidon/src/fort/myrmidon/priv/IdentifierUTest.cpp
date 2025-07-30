#include <gtest/gtest.h>

#include "Identifier.hpp"
#include "Ant.hpp"
#include "AntShapeType.hpp"
#include "AntMetadata.hpp"

#include <google/protobuf/util/time_util.h>

#include "../UtilsUTest.hpp"

#include <random>

namespace fort {
namespace myrmidon {
namespace priv {

class IdentifierUTest : public ::testing::Test {};


typedef AlmostContiguousIDContainer<fort::myrmidon::AntID,Ant> Container;

TEST_F(IdentifierUTest,AntsAreCreatedSequentially) {
	auto i = Identifier::Create();
	auto shapeTypes = std::make_shared<AntShapeTypeContainer>();
	auto metadata = std::make_shared<AntMetadata>();
	try{
		size_t startSize = i->Ants().size();
		size_t toCreate = 5;

		for(size_t ii = 0; ii < toCreate; ++ii) {
			auto ant = i->CreateAnt(shapeTypes,metadata);
			ASSERT_EQ(ant->AntID(),i->Ants().size());
		}
		ASSERT_EQ(i->Ants().size(),startSize + toCreate);

		i->DeleteAnt(startSize+1);
		i->DeleteAnt(startSize+3);

		auto ant = i->CreateAnt(shapeTypes,metadata);
		ASSERT_EQ(ant->AntID(),startSize+1);

		ant = i->CreateAnt(shapeTypes,metadata);
		ASSERT_EQ(ant->AntID(),startSize+3);

		ant = i->CreateAnt(shapeTypes,metadata);
		ASSERT_EQ(ant->AntID(),i->Ants().size());

	} catch ( const std::exception & e) {
		ADD_FAILURE() << "Got unexpected exception: " << e.what();
	}

	EXPECT_THROW({
			i->CreateAnt(shapeTypes,metadata,1);
		},Container::AlreadyExistingObject);
}


TEST_F(IdentifierUTest,AntsCanBeDeleted) {
	auto i = Identifier::Create();
	auto shapeTypes = std::make_shared<AntShapeTypeContainer>();
	auto metadata = std::make_shared<AntMetadata>();
	AntPtr a;
	EXPECT_NO_THROW({
			a = i->CreateAnt(shapeTypes,metadata);
		});

	EXPECT_THROW({
			i->DeleteAnt(a->AntID()+1);
		}, std::out_of_range);

	IdentificationPtr ident;
	EXPECT_NO_THROW({
			ident = Identifier::AddIdentification(i,a->AntID(), 123, Time::SinceEver(), Time::Forever());
		});

	EXPECT_THROW({
			i->DeleteAnt(a->AntID());
		}, std::runtime_error);


	EXPECT_NO_THROW({
			i->DeleteIdentification(ident);
			i->DeleteAnt(a->AntID());
		});
}


TEST_F(IdentifierUTest,AntCanBeAttachedToIdentification) {
	auto i = Identifier::Create();
	auto shapeTypes = std::make_shared<AntShapeTypeContainer>();
	auto metadata = std::make_shared<AntMetadata>();
	auto a = i->CreateAnt(shapeTypes,metadata);
	EXPECT_THROW({
			Identifier::AddIdentification(i,a->AntID()+1,123,Time::SinceEver(),Time::Forever());
		},std::out_of_range);

	IdentificationPtr ident1,ident2;
	EXPECT_NO_THROW(ident1 = Identifier::AddIdentification(i,a->AntID(),123,Time::SinceEver(),Time::Forever()));

	auto ii = Identifier::Create();
	auto aa = ii->CreateAnt(shapeTypes,metadata);
	ident2 = Identifier::AddIdentification(ii,aa->AntID(),124,Time::SinceEver(),Time::Forever());

	EXPECT_THROW({
			i->DeleteIdentification(ident2);
		},Identifier::UnmanagedIdentification);

	EXPECT_NO_THROW(ii->DeleteIdentification(ident2));
	EXPECT_THROW(ii->DeleteIdentification(ident2),Identifier::UnmanagedIdentification);

}

TEST_F(IdentifierUTest,CanIdentifyAntByTag) {
	auto i = Identifier::Create();
	auto shapeTypes = std::make_shared<AntShapeTypeContainer>();
	auto metadata = std::make_shared<AntMetadata>();
	auto a = i->CreateAnt(shapeTypes,metadata);
	auto start = Time::Parse("2019-11-02T22:00:20.021+01:00");
	auto end = Time::Parse("2019-11-02T22:30:25.863+01:00");
	auto secondStart = Time::Parse("2019-11-02T22:34:25.412+01:00");
	auto ident = Identifier::AddIdentification(i,a->AntID(),123,start,end);

	EXPECT_EQ(i->UseCount(123),1);
	EXPECT_EQ(i->UseCount(124),0);

	EXPECT_EQ(i->Identify(123,start),ident);
	EXPECT_EQ(i->Identify(123,start.Add(1 * Duration::Minute)),ident);
	EXPECT_EQ(i->Identify(124,start.Add(1 * Duration::Minute)),IdentificationPtr());
	EXPECT_EQ(i->Identify(123,start.Add(-1 * Duration::Nanosecond)),IdentificationPtr());
	EXPECT_EQ(i->Identify(123,end),IdentificationPtr());
	EXPECT_EQ(i->Identify(123,end.Add(-1)),ident);


	EXPECT_THROW({
			i->UpperUnidentifiedBound(123,start);
		}, std::invalid_argument);
	EXPECT_EQ(i->UpperUnidentifiedBound(124,start),Time::Forever());
	EXPECT_EQ(i->UpperUnidentifiedBound(123,start.Add(-1)),start);
	EXPECT_EQ(i->UpperUnidentifiedBound(123,end),Time::Forever());

	EXPECT_THROW({
			i->LowerUnidentifiedBound(123,start);
		}, std::invalid_argument);
	EXPECT_EQ(i->LowerUnidentifiedBound(124,start),Time::SinceEver());
	EXPECT_EQ(i->LowerUnidentifiedBound(123,end),end);
	EXPECT_EQ(i->LowerUnidentifiedBound(123,start.Add(-1)),Time::SinceEver());

	EXPECT_NO_THROW({
			Identifier::AddIdentification(i,a->AntID(),123,secondStart,Time::Forever());
		});


	Time freeStart,freeEnd;
	EXPECT_FALSE(i->FreeRangeContaining(freeStart,freeEnd,123,start));
	EXPECT_TIME_EQ(freeStart,Time());
	EXPECT_TIME_EQ(freeEnd,Time());

	EXPECT_TRUE(i->FreeRangeContaining(freeStart,freeEnd,123,end));
	EXPECT_TIME_EQ(freeStart,end);
	EXPECT_TIME_EQ(freeEnd,secondStart);

	EXPECT_THROW(Identifier::Accessor::IdentificationsForTag(*i,1),Identifier::UnmanagedTag);
	i->SetAntPositionUpdateCallback([](const Identification::Ptr & , const std::vector<AntPoseEstimateConstPtr> &){
	                                });
	EXPECT_NO_THROW(Identifier::Accessor::UpdateIdentificationAntPosition(*i,ident));

	auto idents = i->IdentificationsAt(end,true);
	EXPECT_EQ(idents.size(),0);
	idents = i->IdentificationsAt(end,false);
	EXPECT_EQ(idents.size(),1);
	EXPECT_EQ(idents[1],std::numeric_limits<TagID>::max());
	idents = i->IdentificationsAt(start,false);
	EXPECT_EQ(idents.size(),1);
	EXPECT_EQ(idents[1],123);

}


TEST_F(IdentifierUTest,Compilation) {
	std::random_device r;
	// Choose a random mean between 1 and 6
    std::default_random_engine e1(r());

    std::uniform_int_distribution<uint32_t> duration(0, 600000);
    std::uniform_real_distribution<double> uniform(0, 1.0);
    auto identifier = Identifier::Create();
    auto shapeTypes = std::make_shared<AntShapeTypeContainer>();
    auto metadata = std::make_shared<AntMetadata>();
	std::set<Time> times;
	std::set<TagID> tags;
	const size_t NB_ANTS = 100;
	for ( size_t i = 0; i < NB_ANTS; ++i) {
		auto a = identifier->CreateAnt(shapeTypes,
		                               metadata);
		std::set<Time> antTimes;

		while( uniform(e1) < 0.8 ) {
			antTimes.insert(Time::FromTimeT(0).Add(duration(e1) * Duration::Millisecond));
		}
		Time lastTime = Time::SinceEver();

		for ( const auto & t : antTimes ) {
			times.insert(t);
			auto tagID = NB_ANTS * a->Identifications().size() + i;
			tags.insert(tagID);
			Identifier::AddIdentification(identifier,
			                              a->AntID(),tagID,
			                              lastTime,
			                              t);
			lastTime = t;
		}

		auto tagID = NB_ANTS * a->Identifications().size() + i;
		tags.insert(tagID);
		Identifier::AddIdentification(identifier,
		                              a->AntID(),
		                              tagID,
		                              lastTime,Time::Forever());
	}

	auto start = Time::Now();
	auto compiled = Identifier::Compile(identifier);
	auto end = Time::Now();

	std::vector<Duration> flatTimes,compiledTimes;

	auto testEqualityAtTime =
		[identifier,compiled,tags,&flatTimes,&compiledTimes](const Time & time) -> ::testing::AssertionResult {
			for ( const auto & t : tags ) {
				auto start = Time::Now();
				auto expected = identifier->Identify(t,time);
				auto middle = Time::Now();
				auto res = compiled->Identify(t,time);
				auto end = Time::Now();

				if ( !expected ) {
					if ( !res == false ) {
						return ::testing::AssertionFailure() << " tag should not have been identified";
					}
					flatTimes.push_back(middle.Sub(start));
					compiledTimes.push_back(end.Sub(middle));
					continue;
				}
				if ( !res ) {
					return ::testing::AssertionFailure()
						<< "tag " << t << " should have been identified to "
						<< expected->Target()->AntID() << " idents: "
						<< expected->Target()->Identifications().size();

				}

				if ( res->Target()->AntID() != expected->Target()->AntID() ) {
					return ::testing::AssertionFailure()
						<< "Got identification target mismatch, expected: "
						<< expected->Target()->AntID()
						<< " got: " << res->Target()->AntID();

				}
				flatTimes.push_back(middle.Sub(start));
				compiledTimes.push_back(end.Sub(middle));
			}
			return ::testing::AssertionSuccess();
		};

	size_t i  = 0;
	for ( const auto & t : times ) {
		EXPECT_TRUE(testEqualityAtTime(t.Add(-1))) << i;
		EXPECT_TRUE(testEqualityAtTime(t)) << i;
		EXPECT_TRUE(testEqualityAtTime(t.Add(1))) << i;
		++i;
	}


#ifdef MYRMIDON_TEST_TIMING
	auto computeMean =
		[](const std::vector<Duration> & durations) -> double {
			double res = 0;
			for ( const auto & d: durations) {
				res += d.Microseconds() / durations.size();
			}
			return res;
		};
	double meanFlatTime = computeMean(flatTimes);
	double meanCompiledTime = computeMean(compiledTimes);
	EXPECT_TRUE(meanFlatTime >  meanCompiledTime )
		<< "flat time is " << meanFlatTime  <<"us "
		<< "compiled time is " << meanCompiledTime << "us";
#endif


}


} // namespace fort
} // namespace myrmidon
} // namespace priv
