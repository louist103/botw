#pragma once

#include <basis/seadTypes.h>
#include <cstddef>
#include <prim/seadSafeString.h>
#include "container/seadSafeArray.h"
#include "KingSystem/ActorSystem/actActor.h"

namespace ksys::act {

class DropDataTableEntry {
    u16 mNum;
    u8 mApproachType;
    u8 mOccurenceSpeedType;
    u8 _4;
    u8 _5;
    u8 _6;
    u8 _7;
    sead::SafeString mDropName{};
};

class DropDataTable {
    sead::SafeArray<DropDataTableEntry, 16> mEntries;
};

class DropData {
    public:
    u32 mStatus = 0;
    u16 mFlags{};
    u16 mExisexistTableFlag = 0;

    sead::SafeArray<DropDataTable, 7> mTables{} ;
    
    static DropData* makeDropData(ksys::act::Actor* actor, sead::Heap* heap);
    void init(Actor* actor, sead::SafeString* dropActor);
    virtual void dummy();
};

}
