#include "actDropData.h"
#include <cstdio>
#include "KingSystem/ActorSystem/actActor.h"
#include "KingSystem/ActorSystem/actActorLinkConstDataAccess.h"
#include "KingSystem/ActorSystem/actActorParam.h"
#include "KingSystem/ActorSystem/actActorUtil.h"
#include "KingSystem/ActorSystem/actAiRoot.h"
#include "KingSystem/Map/mapMubinIter.h"
#include "KingSystem/Resource/Actor/resResourceDrop.h"
#include "KingSystem/System/StageInfo.h"
#include "heap/seadHeap.h"
#include "prim/seadSafeString.h"


namespace ksys::act {

static sead::SafeArray<const char*, 7> sDropTableNames = {
    "Normal",
    "Burnout",
    "Iced",
    "Electronic",
    "Boiled",
    "Happy",
    "Rain",
};

static bool getDropActor(sead::SafeString* drop_actor, ksys::act::Actor* actor,
                         const sead::SafeString& key) {
    if (auto* ai = actor->getRootAi(); ai && ai->getMapUnitParam(drop_actor, key)) {
        return true;
    }

    const char* value = nullptr;
    if (actor->getMapObjIter().tryGetParamStringByKey(&value, key)) {
        *drop_actor = value;
        return true;
    }

    *drop_actor = sead::SafeString::cEmptyString;
    return false;
}

static bool getDropActor(sead::SafeString* drop_actor, ksys::act::Actor* actor) {
    return getDropActor(drop_actor, actor, "DropActor");
}

// NON Matching: Constructor is not right.
DropData* DropData::makeDropData(ksys::act::Actor* actor, sead::Heap* heap) {
    sead::SafeString dropActor;
    if (!getDropActor(&dropActor, actor) || dropActor.isEmpty()) {
        if (actor->getParam()->isDummyParam(ksys::res::ActorLink::User::DropTable))
            return nullptr;
    }

    if (ksys::StageInfo::sIsAocField && ksys::act::isEnemyProfile(actor)) {
        return nullptr;
    }

    auto* dropData = new (heap) ksys::act::DropData;

    if (dropData != nullptr) {
        dropData->init(actor, &dropActor);
    }
    return dropData;
}

void DropData::init(Actor* actor, sead::SafeString* dropActor) {
    res::Drop* drop = actor->getParam()->getRes().mDropTable;
    sead::SafeString tableName;
    mFlags &= ~0x100;
    if (getDropActor(&tableName, actor, "DropTable") || tableName->isEqual(sDropTableNames[0])) {

    }
}

}  // namespace ksys::act
