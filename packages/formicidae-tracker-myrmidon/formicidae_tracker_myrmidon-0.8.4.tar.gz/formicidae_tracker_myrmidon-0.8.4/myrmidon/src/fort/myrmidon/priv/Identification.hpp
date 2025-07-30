#pragma once

#include <memory>
#include <vector>

#include <Eigen/Core>

#include "Isometry2D.hpp"

#include "ForwardDeclaration.hpp"

namespace fort {
namespace myrmidon {
namespace priv {
class Identification;

// Formats an Identification to an std::ostream
// @out the stream to format to
// @a the <fort::myrmidon::priv::Identification> to format
//
// @return a reference to <out>
std::ostream & operator<<(std::ostream & out,
                          const fort::myrmidon::priv::Identification & a);

} // namespae priv
} // namespae myrmidon
} // namespae fort



#include "TimeValid.hpp"

class IdentificationUTest;

namespace fort {
namespace myrmidon {
namespace priv {


namespace proto {
class IOUtils;
class IOUtilsUTest_IdentificationIO_Test;
}

// An Identification relates TagID to an Ant
//
// An <priv::Identification> relates <TagID> to an <priv::Ant>.
// <priv::Identification> can be bounded in time through their <Start>
// and <End> <FramePointer::Ptr>. An empty pointer indicates an
// abscence of boundary.
//
// <priv::Identification> also contains geometric information about how a
// physical tag is positionned on the ant. The <SetTagPosition> can be
// used to define the position of the Tag in the actual Ant reference
// frame. The Helper method <ComputeTagToAntTransform> can be used to
// compute these values from a Ant head / tail position and a Tag
// position in any reference (but they have to be the same for both
// ofc).
//
// TODO: It seems weird that sometimes we use <Isometry2D>, and some
// time pair of point and sometimes translation and orientation. A
// bbit of uniformity would help.

class Identification : public TimeValid {
public:
	virtual ~Identification() {}

	// A Pointer to an Identification
	typedef std::shared_ptr<Identification> Ptr;
	// A Pointer to a const Identification
	typedef std::shared_ptr<const Identification> ConstPtr;
	// A List of Identification
	typedef std::vector<Ptr>      List;
	// A List of Identification
	typedef std::vector<ConstPtr> ConstList;


	// Gets the TagID of this Identification
	// @return <TagID> this <priv::Identification> refers to.
	TagID TagValue() const;

	// Sets the starting validity time for this Identification
	// @start the starting <Time>. <Time::SinceEver> is a valid value.
	//
	// Sets the starting validity <Time> for this
	// <Identification>. This methods will throw any
	// <OverlappingIdentification> if such modification will create
	// any collision for the same <TagID> or the same <priv::Ant>. In
	// such a case the boundaries remain unchanged.
	void SetStart(const Time & start);

	// Sets the ending validity time for this Identification
	// @end the ending <Time>. <Time::Forever> is a valid value.
	//
	// Sets the ending validity <Time> for this <Identification>. This
	// methods will throw any <OverlappingIdentification> if such
	// modification will create any collision for the same <TagID> or
	// the same <priv::Ant>. In such a case the boundaries remain
	// unchanged.
	void SetEnd(const Time & end);

	// Gets the starting validity time
	// @return the time after which this Identification is valid.
	const Time & Start() const;

	// Get the ending validity time
	// @return the time after which this identification is unvalid.
	const Time & End() const;

	// Gets the tag position in the Ant reference frame
	// @return a vector from the <priv::Ant> origin to the tag center
	Eigen::Vector2d AntPosition() const;
	// Gets the tag rotation
	// @return the angle in radian between the <priv::Ant> reference and the tag.
	double AntAngle() const;

	void SetTagSize(double size);

	double TagSize() const;

	bool UseDefaultTagSize() const;


	// Gets the transformation from the Ant reference to the Tag reference
	// @return an <Isometry2D> that performs the transformation from
	//         the Ant reference to the tag one.
	//
	// Given a tag position tp and angle ta in image space, one would
	// be able to get the actual position and orientation of the ant
	// in image space by computing : `Isometry2D(tp,ta) *
	// AntToTagTransform()`, and using <Isometry2D::angle> and
	// <Isometry2D::translation>.
	inline const Isometry2Dd & AntToTagTransform() const {
		return d_antToTag;
	}

	void ComputePositionFromTag(double & x,
	                            double & y,
	                            double & angle,
	                            const Eigen::Vector2d & tagPosition,
	                            double tagAngle) const;

	// Gets the identified Ant
	// @return an <Ant::Ptr> to the identified Ant
	//
	// Gets the identified <priv::Ant>. It can throw
	// <DeletedReference> if by any bug the referenced object has been
	// destroyed.
	AntPtr Target() const;

	// Gets the parent Identifier
	// @return an <Indentifier::Ptr> to the parent <Identifier>
	//
	// Gets the parent <Identifier>. It can throw
	// <DeletedReference> if by any bug the referenced object has been
	// destroyed.
	IdentifierPtr ParentIdentifier() const;

	inline bool HasUserDefinedAntPose() const {
		return d_userDefinedPose;
	}

	void SetUserDefinedAntPose(const Eigen::Vector2d & antPosition, double antAngle);
	void ClearUserDefinedAntPose();

	class Accessor {
	private:
		static Ptr Create(TagID tagValue,
		                  const IdentifierPtr & identifier,
		                  const AntPtr & ant);
		static void SetStart(Identification & identification,
		                     const Time & start);
		static void SetEnd(Identification & identification,
		                   const Time & end);
		static void SetAntPosition(Identification & identification,
		                           const Eigen::Vector2d& position,
		                           double angle);
	public:
		friend class Identifier;
		friend class IdentificationUTest;
		friend class proto::IOUtils;
		friend class proto::IOUtilsUTest_IdentificationIO_Test;
	};


private:
	Identification & operator=(const Identification&) = delete;
	Identification(const Identification&)  = delete;

	Identification(TagID tagValue,
	               const IdentifierPtr & identifier,
	               const AntPtr & ant);

	// Sets the Target Position relative to the tag
	//
	// @position the translation from the tag  origin to the Tag center.
	// @angle the angle between the <priv::Ant> and the tag.
	void SetAntPosition(const Eigen::Vector2d & position,
	                    double angle);

	void SetBound(const Time & start,
	              const Time & end);
	friend class IdentificationUTest;

	Isometry2Dd               d_antToTag;

	int32_t                   d_tagValue;
	double                    d_tagSize;
	std::weak_ptr<Ant>        d_target;
	std::weak_ptr<Identifier> d_identifier;
	bool                      d_userDefinedPose;
};


} // namespace priv
} // namespace myrmidon
} // namespace fort
