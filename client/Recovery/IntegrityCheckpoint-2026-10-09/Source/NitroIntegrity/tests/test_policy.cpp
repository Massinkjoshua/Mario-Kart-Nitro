#include <Security/NitroIntegrity/Policy.hpp>
#include <cassert>
#include <cstdio>
#include <limits>
#include <map>
using namespace Pulsar::NitroIntegrity;
static std::map<Word,Word> memory;
static Word reads;
static Word Read(Word a) { ++reads; return memory[a]; }
int main() {
    CheckWord checks[]={{0x80005000u,10,0},{0x80520000u,20,1}};
    memory[0x80005000u]=10; memory[0x80520000u]=20;
    Scan s=Inspect(checks,2,false,Read);
    assert(s.valid && s.checked==1 && s.mismatches==0 && reads==1);
    s=Inspect(checks,2,true,Read);
    assert(s.valid && s.checked==2 && s.mismatches==0);
    memory[0x80520000u]=0x60000000;
    s=Inspect(checks,2,true,Read);
    assert(s.mismatches==1 && s.firstAddress==0x80520000u && s.expected==20 && s.actual==0x60000000u);
    assert(!DenyOnline(false,false,true,true,s));
    assert(DenyOnline(true,true,true,true,s));
    memory[0x80520000u]=20; s=Inspect(checks,2,true,Read);
    assert(!DenyOnline(true,true,true,true,s));
    assert(DenyOnline(true,false,true,true,s));
    assert(DenyOnline(true,true,false,true,s));
    assert(DenyOnline(true,true,true,false,s));
    Scan empty; assert(DenyOnline(true,true,true,true,empty));
    reads=0;
    assert(!Inspect(0,2,true,Read).valid);
    assert(!Inspect(checks,257,true,Read).valid);
    assert(!Inspect(checks,2,true,0).valid);
    CheckWord invalid[]={{0x80005000u,10,0},{0x80001800u,1,0}};
    assert(!Inspect(invalid,2,true,Read).valid && reads==0);
    invalid[1].address=0x80520001;
    assert(!Inspect(invalid,2,true,Read).valid && reads==0);
    invalid[1].address=0x81800000;
    assert(!Inspect(invalid,2,true,Read).valid && reads==0);
    invalid[1].address=0x80520000; invalid[1].phase=2;
    assert(!Inspect(invalid,2,true,Read).valid && reads==0);
    assert(FindGctHeader(0)==0);
    assert(FindGctHeader(Read)==0);
    memory[0x80002000]=0x00d0c0de;
    assert(FindGctHeader(Read)==0);
    memory[0x80002004]=0x00d0c0de;
    assert(FindGctHeader(Read)==0x80002000);
    s=Inspect(checks,2,true,Read);
    assert(!DenyOnline(true,true,true,true,s)); // Header alone NEVER denies online.
    assert(Finite(0.0f) && Finite(-150.0f) && Finite(100000.0f));
    assert(!Finite(std::numeric_limits<float>::infinity()));
    assert(!Finite(std::numeric_limits<float>::quiet_NaN()));
    // Mutate every bit of each protected word: all selected-word changes signal.
    for (Word i=0;i<2;++i) for (Word bit=0;bit<32;++bit) {
        memory[checks[i].address]=checks[i].expected^(1u<<bit);
        s=Inspect(checks,2,true,Read);
        assert(s.mismatches==1 && s.firstAddress==checks[i].address);
        memory[checks[i].address]=checks[i].expected;
    }
    std::puts("policy: phase safety, invalid inputs, all-bit mutations and header non-enforcement passed");
}
