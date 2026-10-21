#ifndef NITRO_INTEGRITY_TEST_GAME_HPP
#define NITRO_INTEGRITY_TEST_GAME_HPP
#include <cstdarg>
#include <cstdio>
typedef unsigned int u32;
typedef unsigned char u8;
struct Vec3 { float x,y,z; };
struct BootHook { BootHook(void (*)(), unsigned short) {} };
struct RaceFrameHook { RaceFrameHook(void (*)()) {} };
struct RaceLoadHook { RaceLoadHook(void (*)()) {} };
struct SectionLoadHook { SectionLoadHook(void (*)()) {} };
namespace GX { struct Color { u8 r,g,b,a; }; }
namespace OS {
extern unsigned int reports,fatals;
inline void Report(const char *,...) { ++reports; }
inline void Fatal(GX::Color,GX::Color,const char *) { ++fatals; }
}
namespace RKNet {
enum { ROOMTYPE_NONE=0, ROOMTYPE_ACTIVE=1 };
struct Controller { static Controller *sInstance; int currentSub,roomType; };
}
namespace Kart {
struct Movement { float engineSpeed,hardSpeedLimit; };
struct Physics { Vec3 position; };
struct Body { Physics *kartPhysicsHolder; };
struct Pointers { Movement *kartMovement; Body *kartBody; };
struct Player { Pointers pointers; };
struct Manager { static Manager *sInstance; Player **players; u8 playerCount; };
}
namespace Item {
struct Inventory { int currentItemId; u32 currentItemCount; };
struct Player { u8 id; bool isHuman,isRemote; Inventory inventory; };
struct Manager { static Manager *sInstance; Player *players; u8 playerCount; };
}
enum { RACESTAGE_RACE=4 };
struct Raceinfo { static Raceinfo *sInstance; int stage; };
#endif
