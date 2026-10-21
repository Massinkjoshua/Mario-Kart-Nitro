#define NITRO_INTEGRITY_HOST_TEST 1
#include <GameMock.hpp>
#include <Security/NitroIntegrity/Manifest.hpp>
#include <cassert>
#include <map>
using namespace Pulsar::NitroIntegrity;
namespace OS { unsigned int reports=0,fatals=0; }
RKNet::Controller *RKNet::Controller::sInstance=0;
Kart::Manager *Kart::Manager::sInstance=0;
Item::Manager *Item::Manager::sInstance=0;
Raceinfo *Raceinfo::sInstance=0;
static std::map<Word,Word> memory;
static bool relReadable=false;
namespace Pulsar { namespace NitroIntegrity {
Word TestReadWord(Word address) {
    if (address >= 0x80500000u) assert(relReadable); // Catches unsafe boot REL access.
    return memory[address];
}
} }
#include <Security/NitroIntegrity/IntegrityGuard.cpp>
#include <Security/NitroIntegrity/LocalStateAudit.cpp>
int main() {
    memory[0x80000000]=0x524d4350;
    for (Word i=0;i<kCheckCount;++i)memory[kChecks[i].address]=kChecks[i].expected;
    OnBoot(); assert(!sRelReady && OS::fatals==0);
    assert(CanEnterOnline()==!Enforce);
    relReadable=true;OnSectionLoad();assert(sRelReady);
    assert(Audit().mismatches==0);
    memory[0x80002000]=memory[0x80002004]=0x00d0c0de;
    ObserveHeader();assert(sHeaderLogged);
    assert(CanEnterOnline() == (!Enforce || ManifestRuntimeReviewed));
    RKNet::Controller network={0,RKNet::ROOMTYPE_ACTIVE};RKNet::Controller::sInstance=&network;
    OnRaceLoad(); assert(OS::fatals==((Enforce && !ManifestRuntimeReviewed)?1u:0u)); // Unreviewed enforcing build fails closed.
    memory[kChecks[0].address]^=1;
    assert(Audit().mismatches==1);
    if (!Enforce) assert(CanEnterOnline());
    const Word before=OS::fatals;
    for (Word i=0;i<59;++i) { OnRaceFrame(); }
    assert(OS::fatals==before);
    OnRaceFrame();assert(OS::fatals==before+(Enforce?1u:0u));
    memory[kChecks[0].address]^=1; // Restored code cannot clear the session latch.
    assert(Audit().mismatches==0);
    assert(CanEnterOnline()==!Enforce);
    if (Enforce && ManifestRuntimeReviewed) assert(sViolationLatched);
    if (!Enforce) assert(!sViolationLatched);
    network.roomType=RKNet::ROOMTYPE_NONE;
    OnRaceLoad();assert(OS::fatals==before+(Enforce?1u:0u)); // Offline has no enforced stop.
    memory[0x80000000]=0x524d4345;
    relReadable=false;OnBoot();assert(!Audit().valid); // Non-PAL does not read PAL checks.
    if (!Enforce)assert(CanEnterOnline());
    memory[0x80000000]=0x524d4350;relReadable=true;network.roomType=RKNet::ROOMTYPE_ACTIVE;
    Raceinfo race={RACESTAGE_RACE};Raceinfo::sInstance=&race;
    Kart::Movement move={150.0f,120.0f};Kart::Physics physics={{1,2,3}};Kart::Body body={&physics};
    Kart::Player kart={{&move,&body}};Kart::Player *karts[]={&kart,&kart};Kart::Manager km={karts,2};Kart::Manager::sInstance=&km;
    Item::Player players[]={{0,true,false,{15,1}},{1,true,false,{8,1}}};Item::Manager im={players,2};Item::Manager::sInstance=&im;
    Word reports=OS::reports, fatals=OS::fatals;
    ResetStateAudit();for(Word i=0;i<300;++i)AuditLocalState();
    assert(OS::reports==reports+2 && OS::fatals==fatals);
    // Carrying the same items longer, with high speed, never triggers a sanction.
    for(Word i=0;i<600;++i) { AuditLocalState(); }
    assert(OS::fatals==fatals);
    im.playerCount=13;reports=OS::reports;
    for(Word i=0;i<300;++i) { AuditLocalState(); }
    assert(OS::reports==reports);
    im.playerCount=2;players[1].isRemote=true;reports=OS::reports;
    for(Word i=0;i<300;++i) { AuditLocalState(); }
    assert(OS::reports==reports+1);
    std::puts(!Enforce ? "adapter audit-only tests passed"
        : ManifestRuntimeReviewed ? "adapter reviewed enforcement: clean login, tamper stop and persistent deny passed"
        : "adapter unreviewed enforcement gate tests passed");
}
