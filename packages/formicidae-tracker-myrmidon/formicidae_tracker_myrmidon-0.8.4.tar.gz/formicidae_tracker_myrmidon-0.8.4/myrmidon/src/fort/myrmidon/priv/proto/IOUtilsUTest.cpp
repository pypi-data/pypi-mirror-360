#include <gtest/gtest.h>

#include "IOUtils.hpp"

#include <fort/myrmidon/AntDescription.pb.h>
#include <fort/myrmidon/Experiment.pb.h>
#include <fort/myrmidon/Shapes.pb.h>
#include <fort/myrmidon/Space.pb.h>
#include <fort/myrmidon/TagCloseUpCache.pb.h>
#include <fort/myrmidon/TagFamily.pb.h>
#include <fort/myrmidon/Time.pb.h>
#include <fort/myrmidon/TrackingDataDirectory.pb.h>
#include <fort/myrmidon/Vector2d.pb.h>
#include <fort/myrmidon/Zone.pb.h>

#include <google/protobuf/util/message_differencer.h>
#include <google/protobuf/util/time_util.h>

#include <fort/myrmidon/Shapes.hpp>
#include <fort/myrmidon/TestSetup.hpp>
#include <fort/myrmidon/UtilsUTest.hpp>
#include <fort/myrmidon/utest-data/UTestData.hpp>

#include <fort/myrmidon/priv/Ant.hpp>
#include <fort/myrmidon/priv/AntMetadata.hpp>
#include <fort/myrmidon/priv/AntShapeType.hpp>
#include <fort/myrmidon/priv/Experiment.hpp>
#include <fort/myrmidon/priv/Identifier.hpp>
#include <fort/myrmidon/priv/Measurement.hpp>
#include <fort/myrmidon/priv/Space.hpp>
#include <fort/myrmidon/priv/TagCloseUp.hpp>
#include <fort/myrmidon/priv/TrackingDataDirectory.hpp>

namespace fort {
namespace myrmidon {
namespace priv {
namespace proto {

class IOUtilsUTest : public ::testing::Test {};

TEST_F(IOUtilsUTest, TimeIO) {
	google::protobuf::Timestamp pbt;
	google::protobuf::util::TimeUtil::FromString(
	    "2019-01-T10:12:34.567+01:00",
	    &pbt
	);

	struct TestData {
		Time     T;
		int64_t  Seconds;
		int64_t  Nanos;
		uint64_t Mono;
	};

	std::vector<TestData> data = {
	    // An empty time
	    {Time(), 0, 0, 0},
	    // A Timestamp
	    {Time::FromTimeT(1234), 1234, 0, 0},
	    // A more complicated timestamp
	    {Time::FromTimestamp(pbt), pbt.seconds(), pbt.nanos(), 0},
	    // A Time with a monotonic value
	    {Time::FromTimestampAndMonotonic(pbt, 123456789, 42),
	     pbt.seconds(),
	     pbt.nanos(),
	     123456789},
	};

	for (const auto &d : data) {
		pb::Time t;
		pb::Time expected;
		expected.mutable_timestamp()->set_seconds(d.Seconds);
		expected.mutable_timestamp()->set_nanos(d.Nanos);
		expected.set_monotonic(d.Mono);
		IOUtils::SaveTime(&t, d.T);

		EXPECT_MESSAGE_EQ(t, expected);

		auto res = IOUtils::LoadTime(t, 42);

		EXPECT_TIME_EQ(res, d.T);
	}
}

TEST_F(IOUtilsUTest, IdentificationIO) {
	struct TestData {
		Time            Start, End;
		double          TagSize;
		TagID           Value;
		bool            HasPose;
		Eigen::Vector3d Pose;
	};

	std::vector<TestData> data = {
	    {Time::SinceEver(),
	     Time::Forever(),
	     0.0,
	     123,
	     false,
	     Eigen::Vector3d(1, 2, 0.3)},
	    {Time::FromTimeT(2),
	     Time::Forever(),
	     2.3,
	     23,
	     false,
	     Eigen::Vector3d(3, 2, 0.1)},
	    {Time::SinceEver(),
	     Time::FromTimeT(2),
	     0.0,
	     34,
	     false,
	     Eigen::Vector3d(4, 5, 0.0)},
	    {Time::SinceEver(),
	     Time::Forever(),
	     0.0,
	     123,
	     true,
	     Eigen::Vector3d(1, 2, 0.15)},
	};

	auto e = Experiment::Create(
	    TestSetup::UTestData().Basedir() / "test-identification-io.myrmidon"
	);
	auto a = e->CreateAnt();
	for (const auto &d : data) {
		auto ident = Identifier::AddIdentification(
		    e->Identifier(),
		    a->AntID(),
		    d.Value,
		    d.Start,
		    d.End
		);
		// ident->SetAntPosition(Eigen::Vector2d(d.X,d.Y), d.Angle);
		ident->SetTagSize(d.TagSize);
		pb::Identification identPb;
		pb::Identification expected;
		if (d.Start.IsInfinite() == false) {
			d.Start.ToTimestamp(expected.mutable_start());
		}
		if (d.End.IsInfinite() == false) {
			d.End.ToTimestamp(expected.mutable_end());
		}
		if (d.HasPose) {
			ident->SetUserDefinedAntPose(d.Pose.block<2, 1>(0, 0), d.Pose.z());
			auto e = expected.mutable_userdefinedpose();
			IOUtils::SaveVector(
			    e->mutable_position(),
			    d.Pose.block<2, 1>(0, 0)
			);
			e->set_angle(d.Pose.z());
		} else {
			Identification::Accessor::SetAntPosition(
			    *ident,
			    d.Pose.block<2, 1>(0, 0),
			    d.Pose.z()
			);
			auto e = expected.mutable_cachedpose();
			IOUtils::SaveVector(
			    e->mutable_position(),
			    d.Pose.block<2, 1>(0, 0)
			);
			e->set_angle(d.Pose.z());
		}

		expected.set_id(d.Value);
		expected.set_tagsize(d.TagSize);

		IOUtils::SaveIdentification(&identPb, *ident);
		EXPECT_MESSAGE_EQ(identPb, expected);

		e->Identifier()->DeleteIdentification(ident);
		ASSERT_TRUE(a->Identifications().empty());
		IOUtils::LoadIdentification(*e, *a, identPb);

		EXPECT_EQ(a->Identifications().size(), 1);

		if (a->Identifications().empty()) {
			continue;
		}
		auto finalIdent = a->Identifications()[0];
		EXPECT_EQ(finalIdent->TagValue(), d.Value);
		EXPECT_TIME_EQ(finalIdent->Start(), d.Start);
		EXPECT_TIME_EQ(finalIdent->End(), d.End);
		if (d.HasPose == false) {
			EXPECT_FLOAT_EQ(finalIdent->AntPosition().x(), d.Pose.x());
			EXPECT_FLOAT_EQ(finalIdent->AntPosition().y(), d.Pose.y());
			EXPECT_FLOAT_EQ(finalIdent->AntAngle(), d.Pose.z());
		} else {
			EXPECT_VECTOR2D_EQ(
			    finalIdent->AntPosition(),
			    (d.Pose.block<2, 1>(0, 0))
			);
			EXPECT_DOUBLE_EQ(finalIdent->AntAngle(), d.Pose.z());
		}

		if (d.TagSize == 0.0) {
			EXPECT_TRUE(finalIdent->UseDefaultTagSize());
		} else {
			EXPECT_DOUBLE_EQ(finalIdent->TagSize(), d.TagSize);
		}
		EXPECT_NO_THROW({ EXPECT_EQ(finalIdent->Target().get(), a.get()); });
		e->Identifier()->DeleteIdentification(finalIdent);
	}
}

TEST_F(IOUtilsUTest, VectorIO) {
	struct TestData {
		double X, Y;
	};

	std::vector<TestData> testdata = {
	    {0.0, 0.0},
	    {1.23, 4.67},
	};

	for (const auto &d : testdata) {
		Eigen::Vector2d dV(d.X, d.Y), res;
		pb::Vector2d    v, expected;
		expected.set_x(dV.x());
		expected.set_y(dV.y());

		IOUtils::SaveVector(&v, dV);
		EXPECT_MESSAGE_EQ(v, expected);

		IOUtils::LoadVector(res, v);
		EXPECT_VECTOR2D_EQ(res, dV);
	}
}

TEST_F(IOUtilsUTest, CapsuleIO) {
	struct TestData {
		double AX, AY, AR;
		double BX, BY, BR;
	};

	std::vector<TestData> testdata = {
	    {0.0, 0.0, 1.0, 1.0, 1.0, 0.5},
	};

	for (const auto &d : testdata) {
		Eigen::Vector2d dA(d.AX, d.AY), dB(d.BX, d.BY);
		Capsule         dC(dA, dB, d.AR, d.BR);
		pb::Capsule     c, expected;
		IOUtils::SaveVector(expected.mutable_c1(), dA);
		IOUtils::SaveVector(expected.mutable_c2(), dB);
		expected.set_r1(d.AR);
		expected.set_r2(d.BR);

		IOUtils::SaveCapsule(&c, dC);
		EXPECT_MESSAGE_EQ(c, expected);

		auto res = IOUtils::LoadCapsule(c);
		EXPECT_CAPSULE_EQ(*res, dC);
	}
}

TEST_F(IOUtilsUTest, CircleIO) {
	struct TestData {
		double X, Y, R;
	};

	std::vector<TestData> testdata = {
	    {
	        0.0,
	        0.0,
	        1.0,
	    },
	    {1.0, 1.0, 0.5},
	};
	for (const auto &d : testdata) {
		Eigen::Vector2d dCenter(d.X, d.Y);
		auto            dC = std::make_shared<Circle>(dCenter, d.R);
		pb::Circle      c, expected;
		IOUtils::SaveVector(expected.mutable_center(), dCenter);
		expected.set_radius(d.R);

		IOUtils::SaveCircle(&c, *dC);
		EXPECT_MESSAGE_EQ(c, expected);

		auto res = IOUtils::LoadCircle(c);
		EXPECT_CIRCLE_EQ(*res, *dC);
	}
}

TEST_F(IOUtilsUTest, PolygonIO) {
	struct TestData {
		Vector2dList Vertices;
	};

	std::vector<TestData> testdata = {
	    {Vector2dList({{-1, -1}, {1, -1}, {1, 1}, {-1, 1}})},
	};

	for (const auto &d : testdata) {
		auto        dP = std::make_shared<Polygon>(d.Vertices);
		pb::Polygon p, expected;
		for (const auto &v : d.Vertices) {
			IOUtils::SaveVector(expected.add_vertices(), v);
		}

		IOUtils::SavePolygon(&p, *dP);
		EXPECT_MESSAGE_EQ(p, expected);

		auto res = IOUtils::LoadPolygon(p);
		EXPECT_POLYGON_EQ(*res, *dP);
	}
}

TEST_F(IOUtilsUTest, ShapeIO) {
	std::vector<Shape::Ptr> shapes = {
	    std::make_shared<Circle>(Eigen::Vector2d(1, 2), 3),
	    std::make_shared<Capsule>(
	        Eigen::Vector2d(1, 2),
	        Eigen::Vector2d(3, 4),
	        1,
	        0.9
	    ),
	    std::make_shared<Polygon>(Vector2dList({{1, 2}, {3, 4}, {1, 1}, {12, 0}}
	    )),
	};

	for (const auto dS : shapes) {
		pb::Shape s;
		IOUtils::SaveShape(&s, *dS);
		size_t i = 0;
		if (s.has_circle()) {
			++i;
		}
		if (s.has_capsule()) {
			++i;
		}
		if (s.has_polygon()) {
			++i;
		}
		EXPECT_EQ(i, 1);
		auto res = IOUtils::LoadShape(s);
		EXPECT_SHAPE_EQ(*res, *dS);
	}
}

TEST_F(IOUtilsUTest, ValueIO) {
	std::vector<Value> testdata = {
	    false,
	    true,
	    0,
	    42,
	    0.0,
	    42.0,
	    std::string(""),
	    std::string("some value"),
	    Time(),
	    Time::Parse("2019-11-02T23:46:32.123Z"),
	};

	for (const auto &d : testdata) {
		pb::AntStaticValue pb, expected;
		expected.set_type(pb::AntStaticValue_Type(d.index()));
		IOUtils::SaveValue(&pb, d);
		EXPECT_EQ(pb.type(), expected.type());
		auto res = IOUtils::LoadValue(pb);
		EXPECT_VALUE_EQ(res, d);
	}
}

TEST_F(IOUtilsUTest, AntIO) {
	struct IdentificationData {
		Time   Start, End;
		double X, Y, Angle;
		TagID  Value;
	};

	struct TestData {
		std::vector<IdentificationData> IData;
		std::vector<Capsule::Ptr>       Capsules;
		Color                           DisplayColor;
		Ant::DisplayState               DisplayState;
		AntDataMap                      DataMap;
	};

	std::vector<TestData> testdata = {
	    {
	        {
	            {
	                Time::SinceEver(),
	                Time::FromTimeT(1),
	                2.0,
	                3.0,
	                M_PI,
	                1,
	            },
	            {
	                Time::FromTimeT(2),
	                Time::Forever(),
	                2.0,
	                3.0,
	                M_PI,
	                2,
	            },
	        },
	        {std::make_shared<Capsule>(
	             Eigen::Vector2d(2.0, -4.0),
	             Eigen::Vector2d(23.1, -7.3),
	             1.0,
	             2.0
	         ),
	         std::make_shared<Capsule>(
	             Eigen::Vector2d(13.0, 23.0),
	             Eigen::Vector2d(6.1, 8.9),
	             5.0,
	             -3.0
	         )},
	        {127, 56, 94},
	        Ant::DisplayState::SOLO,
	        {
	            {
	                "alive",
	                {
	                    std::make_pair(Time::SinceEver(), true),
	                    std::make_pair(Time::FromTimeT(12), false),
	                },
	            },
	            {
	                "group",
	                {
	                    std::make_pair(Time::SinceEver(), std::string("nurse")),
	                },
	            },
	        },
	    },
	};

	auto e = Experiment::Create(
	    TestSetup::UTestData().Basedir() / "test-ant-io.myrmidon"
	);
	auto alive = e->SetMetaDataKey("alive", true);
	auto group = e->SetMetaDataKey("group", std::string());
	ASSERT_EQ(alive->Type(), ValueType::BOOL);
	ASSERT_EQ(group->Type(), ValueType::STRING);
	auto shapeType = e->CreateAntShapeType("whole-body");
	for (auto &d : testdata) {
		auto                             dA = e->CreateAnt();
		std::vector<Identification::Ptr> dIdents;

		pb::AntDescription a, expected;
		expected.set_id(dA->AntID());
		for (const auto &identData : d.IData) {
			auto ident = Identifier::AddIdentification(
			    e->Identifier(),
			    dA->AntID(),
			    identData.Value,
			    identData.Start,
			    identData.End
			);
			dIdents.push_back(ident);
			IOUtils::SaveIdentification(expected.add_identifications(), *ident);
		}

		for (const auto &c : d.Capsules) {
			dA->AddCapsule(shapeType->TypeID(), c);
			auto sPb = expected.add_shape();
			sPb->set_type(shapeType->TypeID());
			IOUtils::SaveCapsule(sPb->mutable_capsule(), *c);
		}

		dA->SetDisplayColor(d.DisplayColor);
		IOUtils::SaveColor(expected.mutable_color(), d.DisplayColor);
		dA->SetDisplayStatus(d.DisplayState);
		expected.set_displaystate(
		    pb::AntDisplayState(IOUtils::SaveAntDisplayState(d.DisplayState))
		);

		for (const auto &[name, tValues] : d.DataMap) {
			for (const auto &[time, value] : tValues) {
				dA->SetValue(name, value, time);
			}
		}

		for (const auto &[name, tValues] : dA->DataMap()) {
			for (const auto &[time, value] : tValues) {
				auto ev = expected.add_namedvalues();
				ev->set_name(name);
				IOUtils::SaveValue(ev->mutable_value(), value);
				if (time.IsSinceEver() == false) {
					time.ToTimestamp(ev->mutable_time());
				}
			}
		}

		IOUtils::SaveAnt(&a, *dA);
		std::string differences;

		EXPECT_MESSAGE_EQ(a, expected);

		EXPECT_THROW({ IOUtils::LoadAnt(*e, a); }, std::exception);

		EXPECT_NO_THROW({
			for (auto &i : dIdents) {
				e->Identifier()->DeleteIdentification(i);
			}
			e->Identifier()->DeleteAnt(dA->AntID());
		});

		IOUtils::LoadAnt(*e, a);
		auto fi = e->Identifier()->Ants().find(expected.id());
		EXPECT_TRUE(fi != e->Identifier()->Ants().cend());
		if (fi == e->Identifier()->Ants().cend()) {
			continue;
		}
		auto res = fi->second;
		EXPECT_EQ(res->AntID(), expected.id());
		EXPECT_EQ(res->Identifications().size(), dIdents.size());
		for (size_t i = 0;
		     i < std::min(res->Identifications().size(), dIdents.size());
		     ++i) {
			auto ii = res->Identifications()[i];
			auto ie = dIdents[i];
			EXPECT_EQ(ii->TagValue(), ie->TagValue());
			EXPECT_TIME_EQ(ii->Start(), ie->Start());
			EXPECT_TIME_EQ(ii->End(), ie->End());
			EXPECT_VECTOR2D_EQ(ii->AntPosition(), ie->AntPosition());
			EXPECT_NEAR(ii->AntAngle(), ie->AntAngle(), M_PI / 100000.0);
			EXPECT_EQ(ii->Target()->AntID(), ie->Target()->AntID());
		}

		EXPECT_EQ(res->Capsules().size(), d.Capsules.size());
		for (size_t i = 0;
		     i < std::min(d.Capsules.size(), res->Capsules().size());
		     ++i) {
			auto c  = res->Capsules()[i].second;
			auto ce = d.Capsules[i];
			EXPECT_EQ(res->Capsules()[i].first, shapeType->TypeID());
			EXPECT_CAPSULE_EQ(*c, *ce);
		}

		EXPECT_EQ(res->DisplayColor(), d.DisplayColor);

		EXPECT_EQ(res->DisplayStatus(), dA->DisplayStatus());
	}
}

TEST_F(IOUtilsUTest, MeasurementIO) {
	struct TestData {
		EIGEN_MAKE_ALIGNED_OPERATOR_NEW
		Eigen::Vector2d     Start, End;
		std::string         ParentURI;
		MeasurementType::ID TID;
		double              TagSizePx;
	};

	std::vector<TestData> testdata = {
	    {Eigen::Vector2d(12.356, -23.0),
	     Eigen::Vector2d(42.8, 0.00024),
	     "foo/bar/frames/1234/closeups/0x156",
	     1,
	     34.256},
	};

	for (const auto &d : testdata) {
		auto dM = std::make_shared<Measurement>(
		    d.ParentURI,
		    d.TID,
		    d.Start,
		    d.End,
		    d.TagSizePx
		);
		pb::Measurement expected, pbRes;
		expected.set_tagcloseupuri(d.ParentURI);
		expected.set_type(d.TID);
		IOUtils::SaveVector(expected.mutable_start(), d.Start);
		IOUtils::SaveVector(expected.mutable_end(), d.End);
		expected.set_tagsizepx(d.TagSizePx);

		IOUtils::SaveMeasurement(&pbRes, *dM);
		EXPECT_MESSAGE_EQ(pbRes, expected);

		auto res = IOUtils::LoadMeasurement(pbRes);
		EXPECT_EQ(res->URI(), dM->URI());

		EXPECT_EQ(res->TagCloseUpURI(), dM->TagCloseUpURI());

		EXPECT_EQ(res->Type(), dM->Type());
		EXPECT_VECTOR2D_EQ(res->StartFromTag(), dM->StartFromTag());
		EXPECT_VECTOR2D_EQ(res->EndFromTag(), dM->EndFromTag());
		EXPECT_DOUBLE_EQ(res->TagSizePx(), dM->TagSizePx());
	}
}

TEST_F(IOUtilsUTest, ExperimentIO) {
	auto e = Experiment::Create(
	    TestSetup::UTestData().Basedir() / "experiment-io.myrmidon"
	);
	auto res = Experiment::Create(
	    TestSetup::UTestData().Basedir() / "experiment-io-res.myrmidon"
	);
	pb::Experiment ePb, expected;

	TrackingDataDirectory::Ptr tdd;
	FixableErrorList           errors;
	EXPECT_NO_THROW({
		e->SetAuthor("Someone");
		expected.set_author("Someone");
		e->SetName("Some experiment");
		expected.set_name("Some experiment");
		e->SetComment("Some comment");
		expected.set_comment("Some comment");
		e->SetDefaultTagSize(1.6);
		expected.set_tagsize(1.6);

		std::tie(tdd, errors) = TrackingDataDirectory::Open(
		    TestSetup::UTestData().NestDataDirs().front().AbsoluteFilePath,
		    TestSetup::UTestData().Basedir()
		);
		auto s = e->CreateSpace("box");
		e->AddTrackingDataDirectory(s, tdd);

		e->MeasurementTypes()
		    .find(Measurement::HEAD_TAIL_TYPE)
		    ->second->SetName("my-head-tail");
		auto mt = expected.add_custommeasurementtypes();
		mt->set_id(Measurement::HEAD_TAIL_TYPE);
		mt->set_name("my-head-tail");

		e->CreateMeasurementType("antennas");
		mt = expected.add_custommeasurementtypes();
		mt->set_id(Measurement::HEAD_TAIL_TYPE + 1);
		mt->set_name("antennas");

		e->CreateAntShapeType("head");
		auto st = expected.add_antshapetypes();
		st->set_id(1);
		st->set_name("head");
		e->CreateAntShapeType("antenna-left");
		st = expected.add_antshapetypes();
		st->set_id(2);
		st->set_name("antenna-left");
		e->CreateAntShapeType("antenna-right");
		st = expected.add_antshapetypes();
		st->set_id(3);
		st->set_name("antenna-right");

		e->SetMetaDataKey("alive", false);
		auto c = expected.add_antmetadata();
		c->set_name("alive");
		IOUtils::SaveValue(c->mutable_defaultvalue(), Value(false));
		e->SetMetaDataKey("group", std::string());
		c = expected.add_antmetadata();
		c->set_name("group");
		IOUtils::SaveValue(c->mutable_defaultvalue(), Value(std::string()));
	});
	EXPECT_TRUE(errors.empty());

	ePb.Clear();

	IOUtils::SaveExperiment(&ePb, *e);
	EXPECT_MESSAGE_EQ(ePb, expected);

	IOUtils::LoadExperiment(*res, ePb);
	EXPECT_EQ(res->Author(), e->Author());
	EXPECT_EQ(res->Name(), e->Name());
	EXPECT_EQ(res->Comment(), e->Comment());
	// there are no space, so its undefined
	EXPECT_EQ(res->Family(), tags::Family::Undefined);
	auto s = res->CreateSpace("box");
	res->AddTrackingDataDirectory(s, tdd);
	// now we have a space, we are not undefined
	EXPECT_EQ(res->Family(), e->Family());

	EXPECT_EQ(
	    e->AntMetadataPtr()->Keys().size(),
	    res->AntMetadataPtr()->Keys().size()
	);
	for (const auto [name, key] : e->AntMetadataPtr()->Keys()) {
		auto ci = res->AntMetadataPtr()->Keys().find(name);
		if (ci == res->AntMetadataPtr()->Keys().cend()) {
			ADD_FAILURE() << "missing meta data key '" << name << "'";
		} else {
			EXPECT_EQ(ci->second->Type(), key->Type());
		}
	}
}

TEST_F(IOUtilsUTest, ZoneIO) {
	auto e = Experiment::Create(
	    TestSetup::UTestData().Basedir() / "zone-io.myrmidon"
	);
	auto s1 = e->CreateSpace("foo");

	auto dZ    = s1->CreateZone("hole");
	auto stamp = Time::FromTimeT(1);
	auto def1  = dZ->AddDefinition(
        {std::make_shared<Circle>(Eigen::Vector2d(0, 0), 10)},
        Time::SinceEver(),
        stamp
    );

	auto def2 = dZ->AddDefinition(
	    {std::make_shared<Circle>(Eigen::Vector2d(0, 0), 12)},
	    stamp,
	    Time::Forever()
	);

	pb::Zone z, expected;
	expected.set_id(dZ->ID());
	expected.set_name(dZ->Name());
	auto pbDef1 = expected.add_definitions();
	stamp.ToTimestamp(pbDef1->mutable_end());
	IOUtils::SaveShape(pbDef1->add_shapes(), *def1->Shapes().front());
	auto pbDef2 = expected.add_definitions();
	stamp.ToTimestamp(pbDef2->mutable_start());
	IOUtils::SaveShape(pbDef2->add_shapes(), *def2->Shapes().front());

	IOUtils::SaveZone(&z, *dZ);
	EXPECT_MESSAGE_EQ(z, expected);
	auto e2 = Experiment::Create(
	    TestSetup::UTestData().Basedir() / "zone-io.myrmidon"
	);
	auto s2 = e2->CreateSpace("foo");
	IOUtils::LoadZone(*s2, z);
	ASSERT_FALSE(s2->Zones().empty());
	auto res = s2->Zones().begin()->second;
	EXPECT_EQ(dZ->ID(), res->ID());
	EXPECT_EQ(dZ->Name(), res->Name());
	EXPECT_EQ(dZ->Definitions().size(), res->Definitions().size());
	for (size_t i = 0;
	     i < std::min(dZ->Definitions().size(), res->Definitions().size());
	     ++i) {
		const auto &expectedDefinition = dZ->Definitions()[i];
		const auto &definition         = res->Definitions()[i];
		EXPECT_TIME_EQ(definition->Start(), expectedDefinition->Start());
		EXPECT_TIME_EQ(definition->End(), expectedDefinition->End());
		ASSERT_FALSE(expectedDefinition->Shapes().empty());
		ASSERT_FALSE(definition->Shapes().empty());
		EXPECT_EQ(
		    definition->Shapes().size(),
		    expectedDefinition->Shapes().size()
		);
		for (size_t j = 0; j < std::min(
		                           expectedDefinition->Shapes().size(),
		                           definition->Shapes().size()
		                       );
		     ++j) {
			const auto &shape         = definition->Shapes()[j];
			const auto &expectedShape = expectedDefinition->Shapes()[j];
			EXPECT_EQ(shape->ShapeType(), expectedShape->ShapeType());
			EXPECT_SHAPE_EQ(*shape, *expectedShape);
		}
	}
}

TEST_F(IOUtilsUTest, SpaceIO) {
	auto e = Experiment::Create(
	    TestSetup::UTestData().Basedir() / "space-io.myrmidon"
	);
	auto e2 = Experiment::Create(
	    TestSetup::UTestData().Basedir() / "space2-io.myrmidon"
	);
	auto dS = e->CreateSpace("foo");
	auto tddPath =
	    TestSetup::UTestData().NestDataDirs().front().AbsoluteFilePath;
	auto [tdd, errors] =
	    TrackingDataDirectory::Open(tddPath, TestSetup::UTestData().Basedir());
	EXPECT_TRUE(errors.empty());
	e->AddTrackingDataDirectory(dS, tdd);
	auto      z = dS->CreateZone("bar");
	pb::Space expected, s;
	expected.set_id(dS->ID());
	expected.set_name(dS->Name());
	expected.add_trackingdatadirectories(tddPath.filename());
	IOUtils::SaveZone(expected.add_zones(), *z);

	IOUtils::SaveSpace(&s, *dS);
	EXPECT_MESSAGE_EQ(s, expected);
	IOUtils::LoadSpace(*e2, s);
	ASSERT_EQ(e2->Spaces().size(), 1);
	auto res = e2->Spaces().begin()->second;
	EXPECT_EQ(res->ID(), dS->ID());
	EXPECT_EQ(res->Name(), dS->Name());
	ASSERT_EQ(res->TrackingDataDirectories().size(), 1);
	EXPECT_EQ(
	    res->TrackingDataDirectories().front()->URI(),
	    tddPath.filename()
	);
	ASSERT_EQ(res->Zones().size(), 1);
	ASSERT_EQ(res->Zones().begin()->second->ID(), z->ID());
	ASSERT_EQ(res->Zones().begin()->second->Name(), z->Name());
}

TEST_F(IOUtilsUTest, TrackingIndexIO) {
	std::string       parentURI("foo");
	Time::MonoclockID monoID(42);
	auto si  = std::make_shared<TrackingDataDirectory::TrackingIndex>();
	auto res = std::make_shared<TrackingDataDirectory::TrackingIndex>();
	google::protobuf::RepeatedPtrField<pb::TrackingSegment> expected, pbRes;
	for (size_t i = 0; i < 20; ++i) {
		uint64_t fid = 100 * i;
		Time     t   = Time::FromTimestampAndMonotonic(
            Time::FromTimeT(i).ToTimestamp(),
            1000000001ULL * uint64_t(i) + 10,
            monoID
        );
		std::ostringstream os;
		os << i;
		FrameReference ref(parentURI, fid, t);
		si->Insert(ref, os.str());

		auto pb = expected.Add();
		IOUtils::SaveFrameReference(pb->mutable_frame(), ref);
		pb->set_filename(os.str());
	}
	ASSERT_EQ(si->Segments().size(), 20);

	for (const auto &s : si->Segments()) {
		auto pb = pbRes.Add();
		IOUtils::SaveTrackingIndexSegment(pb, s);
	}

	ASSERT_EQ(pbRes.size(), expected.size());
	for (size_t i = 0; i < pbRes.size(); ++i) {
		EXPECT_MESSAGE_EQ(pbRes.Get(i), expected.Get(i));
	}
	for (const auto &pb : pbRes) {
		TrackingDataDirectory::TrackingIndex::Segment s;
		IOUtils::LoadTrackingIndexSegment(&s, pb, parentURI, monoID);
		res->Insert(s.first, s.second);
	}
	auto ress      = res->Segments();
	auto expecteds = si->Segments();

	ASSERT_EQ(ress.size(), expecteds.size());
	for (size_t i = 0; i < ress.size(); ++i) {
		auto &iref      = ress[i].first;
		auto &ifilename = ress[i].second;

		EXPECT_EQ(iref.ParentURI(), parentURI);
		EXPECT_TIME_EQ(iref.Time(), expecteds[i].first.Time());
		EXPECT_EQ(ifilename, expecteds[i].second);
	}
}

TEST_F(IOUtilsUTest, MovieSegmentIO) {
	MovieSegment::Ptr      ms;
	MovieSegment::ConstPtr res;
	Time::MonoclockID      monoID(42);
	Time                   startTime = Time::FromTimestampAndMonotonic(
        Time::FromTimeT(1).ToTimestamp(),
        123456789,
        monoID
    );

	fort::myrmidon::pb::MovieSegment expected, pbRes;
	MovieSegment::ListOfOffset       offsets;
	offsets.push_back(std::make_pair(0, 1234));
	offsets.push_back(std::make_pair(42, 1236));
	offsets.push_back(std::make_pair(12, 1235));

	std::sort(offsets.begin(), offsets.end());
	std::reverse(offsets.begin(), offsets.end());

	auto tddPath = TestSetup::UTestData().WithVideoDataDir().AbsoluteFilePath;
	ms           = std::make_shared<MovieSegment>(
        0,
        tddPath / "stream.0000.mp4",
        tddPath.filename(),
        1234,
        1234 + 100 + 2,
        0,
        100,
        offsets
    );

	expected.set_path("stream.0000.mp4");
	expected.set_trackingstart(1234);
	expected.set_trackingend(1234 + 100 + 2);
	expected.set_moviestart(0);
	expected.set_movieend(100);
	for (const auto &o : offsets) {
		auto pbo = expected.add_offsets();
		pbo->set_movieframeid(o.first);
		pbo->set_offset(o.second);
	}

	IOUtils::SaveMovieSegment(&pbRes, *ms, tddPath);
	EXPECT_MESSAGE_EQ(pbRes, expected);

	res = IOUtils::LoadMovieSegment(pbRes, tddPath, tddPath.filename());

	EXPECT_EQ(
	    res->AbsoluteFilePath().string(),
	    ms->AbsoluteFilePath().string()
	);
	EXPECT_EQ(res->StartFrame(), ms->StartFrame());
	EXPECT_EQ(res->EndFrame(), ms->EndFrame());

	EXPECT_EQ(res->StartMovieFrame(), ms->StartMovieFrame());
	EXPECT_EQ(res->EndMovieFrame(), ms->EndMovieFrame());

	ASSERT_EQ(res->Offsets().size(), ms->Offsets().size());

	for (size_t i = 0; i < ms->Offsets().size(); ++i) {
		EXPECT_EQ(res->Offsets()[i], ms->Offsets()[i]);
	}

	// not using an absolute path as arguments
	EXPECT_THROW(
	    { IOUtils::SaveMovieSegment(&pbRes, *ms, "nest.0000"); },
	    std::invalid_argument
	);
	EXPECT_THROW(
	    { IOUtils::LoadMovieSegment(pbRes, "nest.0000", "nest.0000"); },
	    std::invalid_argument
	);
}

TEST_F(IOUtilsUTest, FamilyIO) {
	struct TestData {
		tags::Family  Family;
		pb::TagFamily Pb;
	};

	std::vector<TestData> testdata = {
	    {tags::Family::Tag36h11, pb::TAG36H11},
	    {tags::Family::Tag36h10, pb::TAG36H10},
	    {tags::Family::Tag36ARTag, pb::TAG36ARTAG},
	    {tags::Family::Tag16h5, pb::TAG16H5},
	    {tags::Family::Tag25h9, pb::TAG25H9},
	    {tags::Family::Circle21h7, pb::CIRCLE21H7},
	    {tags::Family::Circle49h12, pb::CIRCLE49H12},
	    {tags::Family::Custom48h12, pb::CUSTOM48H12},
	    {tags::Family::Standard41h12, pb::STANDARD41H12},
	    {tags::Family::Standard52h13, pb::STANDARD52H13},
	};

	for (const auto &d : testdata) {
		EXPECT_EQ(d.Family, IOUtils::LoadFamily(d.Pb));
		EXPECT_EQ(d.Pb, IOUtils::SaveFamily(d.Family));
	}
}

TEST_F(IOUtilsUTest, TagCloseUpIO) {
	auto tddPath =
	    TestSetup::UTestData().NestDataDirs().front().AbsoluteFilePath;
	auto basedir = tddPath / "ants";

	struct TestData {
		EIGEN_MAKE_ALIGNED_OPERATOR_NEW
		Eigen::Vector2d Position;
		fs::path        Filepath;
		FrameReference  Reference;
		TagID           TID;
		double          Angle;
		Vector2dList    Corners;
	};

	std::vector<TestData> testdata = {{
	    Eigen::Vector2d(23.0, -3.0),
	    "ant_123_frame_21.png",
	    FrameReference(tddPath.filename(), 21, Time::FromTimeT(2)),
	    123,
	    -M_PI / 5.0,
	    {
	        Eigen::Vector2d(43, 17.0),
	        Eigen::Vector2d(43, -23.0),
	        Eigen::Vector2d(3, -23.0),
	        Eigen::Vector2d(3, 17.0),
	    },
	}};

	for (const auto &d : testdata) {
		auto dTCU = std::make_shared<TagCloseUp>(
		    basedir / d.Filepath,
		    d.Reference,
		    d.TID,
		    d.Position,
		    d.Angle,
		    d.Corners
		);

		auto resolver = [&d](FrameID frameID) {
			return FrameReference(
			    d.Reference.ParentURI(),
			    frameID,
			    d.Reference.Time().Add(
			        (int64_t(frameID) - int64_t(d.Reference.FrameID())) *
			        Duration::Second
			    )
			);
		};

		pb::TagCloseUp expected, pbRes;
		IOUtils::SaveVector(expected.mutable_position(), d.Position);
		expected.set_angle(d.Angle);
		expected.set_value(d.TID);
		for (const auto &c : d.Corners) {
			IOUtils::SaveVector(expected.add_corners(), c);
		}
		expected.set_frameid(d.Reference.FrameID());
		expected.set_imagepath(d.Filepath.generic_string());

		IOUtils::SaveTagCloseUp(&pbRes, *dTCU, basedir);
		EXPECT_MESSAGE_EQ(pbRes, expected);
		auto res = IOUtils::LoadTagCloseUp(pbRes, basedir, resolver);

		EXPECT_EQ(res->Frame().URI(), dTCU->Frame().URI());
		EXPECT_TIME_EQ(res->Frame().Time(), dTCU->Frame().Time());
		EXPECT_EQ(res->URI(), dTCU->URI());
		EXPECT_EQ(res->AbsoluteFilePath(), dTCU->AbsoluteFilePath());
		EXPECT_VECTOR2D_EQ(res->TagPosition(), dTCU->TagPosition());
		EXPECT_DOUBLE_EQ(res->TagAngle(), dTCU->TagAngle());
		ASSERT_EQ(4, res->Corners().size());
		for (size_t i = 0; i < 4; ++i) {
			EXPECT_VECTOR2D_EQ(res->Corners()[i], dTCU->Corners()[i]);
		}

		EXPECT_THROW(
		    {
			    // Needs 4 corners
			    expected.clear_corners();
			    IOUtils::LoadTagCloseUp(expected, basedir, resolver);
		    },
		    std::invalid_argument
		);
	}
}

} // namespace proto
} // namespace priv
} // namespace myrmidon
} // namespace fort
