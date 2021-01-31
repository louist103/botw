#include "KingSystem/Utils/Thread/Message.h"

namespace ksys {

Message::Message() = default;

Message::Message(const MesTransceiverId& source, const MesTransceiverId& destination,
                 const MessageType& type, void* user_data, const Message::DelayParams& delay_params,
                 bool x)
    : mSource(source), mDestination(destination), mType(type), mUserData(user_data),
      mDelayParams(delay_params), _60(x) {}

Message::Message(const MesTransceiverId& source, const MessageType& type, void* user_data,
                 const Message::DelayParams& delay_params, bool x)
    : mSource(source), mType(type), mUserData(user_data), mDelayParams(delay_params), _60(x) {}

Message::~Message() = default;

const MesTransceiverId& Message::getSource() const {
    return mSource;
}

const MesTransceiverId& Message::getDestination() const {
    return mDestination;
}

const MessageType& Message::getType() const {
    return mType;
}

void* Message::getUserData() const {
    return mUserData;
}

u32 Message::getField48() const {
    return _48;
}

bool Message::shouldBeProcessed() const {
    if (mDelayParams.delay_ticks != 0)
        return false;

    if (!mDelayParams.delayer)
        return true;

    return mDelayParams.delayer->shouldProcessMessage();
}

bool Message::getField60() const {
    return _60;
}

void Message::setDestination(const MesTransceiverId& dest) {
    mDestination = dest;
}

void Message::setField48(const u32& v) {
    _48 = v;
}

}  // namespace ksys
