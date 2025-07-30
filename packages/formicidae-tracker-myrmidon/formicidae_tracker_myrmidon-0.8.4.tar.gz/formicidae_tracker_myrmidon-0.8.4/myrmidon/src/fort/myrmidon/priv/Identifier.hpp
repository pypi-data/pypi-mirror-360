#pragma once

#include <memory>
#include <unordered_map>
#include <set>

#include <fort/time/Time.hpp>
#include <fort/myrmidon/Ant.hpp>

#include "LocatableTypes.hpp"

#include "ForwardDeclaration.hpp"

#include "DeletedReference.hpp"

#include "ContiguousIDContainer.hpp"

namespace fort {


namespace myrmidon {

namespace pb {
class AntMetadata;
}


namespace priv {

class IdentifierIF {
public:
	typedef std::shared_ptr<IdentifierIF>       Ptr;
	typedef std::shared_ptr<const IdentifierIF> ConstPtr;
	virtual ~IdentifierIF();
	virtual IdentificationConstPtr Identify(TagID tagID, const Time & time) const = 0;
};


// An Identifier identifies Ants through Identification
//
// The <Identifier> is responsible to keep track in the the
// <priv::Experiment> of the <priv::Ant> i and their
// Identification. Both <priv::Ant> and <priv::Identification> need to
// be created and deleted through its interface as it the only way to
// make sure that we respect the non-<OverlappingIdentification>
// invariant in the library.
class Identifier : public IdentifierIF, protected AlmostContiguousIDContainer<AntID,Ant> {
private:
	struct this_is_private;
public:
	// A Pointer to an Identifier
	typedef std::shared_ptr<Identifier> Ptr;
	// A Pointer to a const Identifier
	typedef std::shared_ptr<const Identifier> ConstPtr;


	typedef std::function<void(const IdentificationPtr &,
	                           const std::vector<AntPoseEstimateConstPtr> &)> OnPositionUpdateCallback;

	static Ptr Create();
	Identifier(const this_is_private &);
	virtual ~Identifier();

	// A default asking for the next available ID
	const static AntID NEXT_AVAILABLE_ID = 0;

	// Create an Ant
	// @ID the desired ID
	//
	// Creats a new Ant with the given ID. It will throw an
	// <AlreadyExistingAnt> if the ID is already used. If
	// NEXT_AVAILABLE_ID is used, a unique ID will be automatically
	// chosen.
	AntPtr CreateAnt(const AntShapeTypeContainerConstPtr & shapeTypes,
	                 const AntMetadataConstPtr & metadataColumns,
	                 AntID ID = NEXT_AVAILABLE_ID);

	// Deletes an Ant
	// @ID the <priv::Ant> to delete
	//
	// Deletes an <priv::Ant> from the Identifier. It should have no
	// Identification targetting her otherwise an exception will be
	// thrown.
	void DeleteAnt(AntID );

	// Gets the Ants in the Identifier
	// @return the map of <priv::Ant> by their <myrmidon::Ant::ID>
	const AntByID & Ants() const;

	// Adds a new Identification
	// @id the targeted <priv::Ant>
	// @tagValue the used TagID
	// @start the first valid time for this <priv::Identification>
	// @end the last valid time for this <proiv::Identification>
	//
	// Adds a new Identification. It may throw
	// <OverlappingIdentification> if any exists for the desired
	// <priv::Ant> or <TagID>.
	static IdentificationPtr AddIdentification(const Identifier::Ptr & itself,
	                                           AntID id,
	                                           TagID tagValue,
	                                           const Time & start,
	                                           const Time & end);

	// Removes an Identification
	// @ident the <priv::Identification> to remove
	//
	// Any <priv::Identification> targetting a given <priv::Ant>
	// should be deleted before removing the <priv::Ant>
	void DeleteIdentification(const IdentificationPtr & ident);

	// An exeption when a TagID is not managed by this Identifier
	class UnmanagedTag : public std::runtime_error {
	public:
		UnmanagedTag(TagID tagValue) noexcept;
		virtual ~UnmanagedTag() noexcept {};
	};
	// An exeption when an Identification is not managed by this Identifier
	class UnmanagedIdentification : public std::runtime_error {
	public:
		UnmanagedIdentification(const Identification & ident) noexcept;
		virtual ~UnmanagedIdentification() noexcept {};
	};

	class Accessor {
	private:
		static IdentificationList & IdentificationsForTag(Identifier & identifier,TagID tagID);
		static void UpdateIdentificationAntPosition(Identifier & identifier,
		                                            const IdentificationPtr & identification);
		static void UpdateIdentificationAntPosition(Identifier & identifier,
		                                            Identification * identificationPtr);

	public:
		friend class Identification;
		friend class IdentifierUTest_CanIdentifyAntByTag_Test;
	};

	// Performs invarinat checks for two tags sharing the same ant or the same TagID
	static void SortAndCheck(IdentificationList & tagSibling,
	                         IdentificationList & antSibling);

	// Identifies an ant from a point in time and a TagID
	// @tag <TagID> to look for
	// @frame the frame to look for
	// @return an <Identification::Ptr> if any exists for that tag at this point in time.
	IdentificationConstPtr Identify(TagID tag,const Time & frame) const override;


	// Return the first next frame if any where tag is not used
	Time UpperUnidentifiedBound(TagID tag, const Time & t) const;
	// Return the first previoys frame if any where tag is not used
	Time LowerUnidentifiedBound(TagID tag, const Time & t) const;

	// Returns the number of time a given tag is used.
	size_t UseCount(TagID tag) const;

	// Found the largest time range where a <TagID> is unused.
	// @start is set to the first frametime the tag is unused, or an
	//        empty pointer if the tag isn't used before <t>
	// @end   set the last time where the tag is unused, or an
	//        empty pointer if the tag isn't used after <t>
	// @tag the <TagID> to inquire for
	// @t the <Time> designating the point in time we want a free range.
	// @return true if such a range was found, false if <tag> is already used at time <t>
	//
	// Try to find the largest range where the <tag> is not used,
	// containing the <Time> <f>. If the tag is actually used at this
	// time, returns false. Otherwise returns true and sets <start>
	// and <end> accordingly. Note that a reset <time::ConstPtr> means
	// +/-∞.
	bool FreeRangeContaining(Time & start,
	                         Time & end,
	                         TagID tag,
	                         const Time & t) const;


	void SetAntPoseEstimate(const AntPoseEstimateConstPtr & ape);

	void DeleteAntPoseEstimate(const AntPoseEstimateConstPtr & ape);

	void QueryAntPoseEstimate(std::vector<AntPoseEstimateConstPtr> & estimations,
	                          const IdentificationConstPtr & identification) const;

	void SetAntPositionUpdateCallback(const OnPositionUpdateCallback & callback);

	class Compiled : public IdentifierIF {
	public:
		typedef std::shared_ptr<const Compiled>     ConstPtr;
		typedef std::vector<IdentificationConstPtr> IdentificationConstList;

		Compiled(const Identifier::ConstPtr & parent);
		virtual ~Compiled();

		IdentificationConstPtr Identify(TagID tagID, const Time & time) const override;

	private:
		typedef DenseMap<TagID,IdentificationConstList> IdentificationsByTagID;
		IdentificationsByTagID d_identifications;
		Identifier::ConstPtr   d_parent;
	};

	static Compiled::ConstPtr Compile(const Identifier::ConstPtr & identifier);


	// Gets AntID <- TagID correspondances at a given time
	// @time the wanted <Time> to query for the correspondances
	// @removeUnidentifiedAnt if `true`, just do not report
	//                        unidentified at this time. If `false`
	//                        `std::numeric_limits<TagID>::max()` will
	//                        be returned as a TagID for unidentified
	//                        Ant (or `NA` for R).
	//
	// R Version
	// ```R
	// # will report NA for unidentified Ant
	// e$identificationsAt(fmTimeParse("2029-11-02T23:42:00.000Z"),FALSE)
	// ```
	//
	// @return a map with the correspondance between AntID and TagID. Unidentified Ant will be ommi
	std::map<AntID,TagID> IdentificationsAt(const Time & time,
	                                        bool removeUnidentifiedAnt = true) const;


private:
	struct this_is_private{};
	Identifier();

	class AntPoseEstimateComparator {
	public:
		bool operator() (const AntPoseEstimateConstPtr & a,
		                 const AntPoseEstimateConstPtr & b) const;

	};

	void UpdateIdentificationAntPosition(const IdentificationPtr & identification);

	typedef std::unordered_map<TagID,IdentificationList> IdentificationByTagID;

	typedef std::set<AntPoseEstimateConstPtr,AntPoseEstimateComparator>     AntPoseEstimateList;
	typedef std::map<TagID,AntPoseEstimateList>                             AntPoseEstimateByTagID;

	Identifier(const Identifier&) = delete;
	Identifier & operator=(const Identifier&) = delete;



	std::weak_ptr<Identifier> d_itself;

	IdentificationByTagID    d_identifications;
	AntPoseEstimateByTagID   d_tagPoseEstimates;
	OnPositionUpdateCallback d_callback;

};



} // namespace priv

} // namespace myrmidon

} // namespace fort
