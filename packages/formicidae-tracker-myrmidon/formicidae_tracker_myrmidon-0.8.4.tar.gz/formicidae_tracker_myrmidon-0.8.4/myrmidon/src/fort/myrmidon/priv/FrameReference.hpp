#pragma once

#include <memory>
#include <string>

#include <fort/time/Time.hpp>

#include "LocatableTypes.hpp"
#include "Typedefs.hpp"


namespace fort {
namespace myrmidon {
namespace priv {

class FrameReference : public Identifiable {
public:
	typedef std::shared_ptr<FrameReference> Ptr;
	typedef std::shared_ptr<const FrameReference> ConstPtr;

	FrameReference();

	FrameReference(const std::string & parentURI,
	               priv::FrameID frameID,
	               const fort::Time & Time);

	virtual ~FrameReference();

	const std::string & ParentURI() const;

	// The Time of the Frame
	//
	// @return the <Time> of the designated frame
	const fort::Time & Time() const;

	// The FrameID of the frame
	//
	// @return the <FrameID> of the designated frame
	priv::FrameID FrameID() const;

	// A Path uniquely defining the FramePointer
	//
	// @return a fs::path uniquely identifying the Frame
	const std::string & URI() const override;

	bool operator<(const FrameReference & other) const;


private:
	std::string    d_parentURI;
	std::string    d_URI;
	priv::FrameID  d_id;
	fort::Time     d_time;
};

// Formats a FrameReference
// @out the std::ostream to format to
// @p the <fort::myrmidon::priv::FrameReference> to format
// @return a reference to <out>
std::ostream& operator<<(std::ostream & out,
                         const fort::myrmidon::priv::FrameReference & p);


} //namespace priv

} //namespace myrmidon

} //namespace fort
