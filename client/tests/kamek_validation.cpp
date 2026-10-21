#include "kamekValidation.hpp"
#include <cassert>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>
#include <cstring>

typedef std::vector<unsigned char> Bytes;
static void Put(Bytes &b, unsigned offset, unsigned value) {
    for (unsigned i=0; i<4; ++i) b[offset+i]=static_cast<unsigned char>(value>>(24-i*8));
}
static Bytes Minimal() {
    Bytes b(60,0); std::memcpy(&b[0],"Kamek\0\0\2",8);
    Put(b,12,16); Put(b,48,0x20fffffe); Put(b,52,0x80001000); Put(b,56,0x12345678);
    return b;
}
static bool Valid(const Bytes &b) {
    NitroKamek::Section section;
    return !NitroKamek::ValidateSection(&b[0],static_cast<unsigned>(b.size()),section);
}
int main(int argc,char **argv) {
    assert(argc==2);
    Bytes good=Minimal(); assert(Valid(good));
    for (unsigned n=1;n<32;++n) {
        Bytes b(good.begin(),good.begin()+n); assert(!Valid(b));
    }
    Bytes b=good; b[0]='X'; assert(!Valid(b));
    b=good; b[7]=3; assert(!Valid(b));
    b=good; Put(b,12,100); assert(!Valid(b));
    b=good; Put(b,8,0xfffffff0); assert(!Valid(b));
    b=good; Put(b,16,12); Put(b,20,8); assert(!Valid(b));
    b=good; Put(b,20,20); assert(!Valid(b));
    b=good; Put(b,16,1); assert(!Valid(b));
    b=good; Put(b,48,0x7ffffffe); assert(!Valid(b));
    for (unsigned n=49;n<60;++n) {
        b.assign(good.begin(),good.begin()+n); assert(!Valid(b));
    }
    b=good; Put(b,48,0x20000010); assert(!Valid(b));
    b=good; Put(b,52,0x80001001); assert(Valid(b)); // legal byte-positioned data patch
    b=good; Put(b,48,0x01fffffe); Put(b,56,16); assert(!Valid(b));
    b=good; Put(b,48,0x23fffffe); assert(!Valid(b)); // conditional pointer needs two words
    b.resize(64); Put(b,56,0x80002000); Put(b,60,0x1234); assert(Valid(b));

    std::ifstream stream(argv[1],std::ios::binary);
    assert(stream.good());
    Bytes container((std::istreambuf_iterator<char>(stream)),std::istreambuf_iterator<char>());
    assert(container.size()>32);
    for (unsigned region=0;region<4;++region) {
        unsigned offset=0,length=0;
        const char *error=NitroKamek::SelectRegion(&container[0],static_cast<unsigned>(container.size()),region,offset,length);
        if (region==3) { assert(error); continue; }
        if (error) { std::cerr<<error<<"\n"; return 1; }
        NitroKamek::Section section;
        error=NitroKamek::ValidateSection(&container[offset],length,section);
        if (error) { std::cerr<<"Region "<<region<<": "<<error<<"\n"; return 1; }
        unsigned cursor=32+section.code, commands=0, dol=0,rel=0;
        while (cursor<length) {
            NitroKamek::Command c;
            assert(!NitroKamek::ReadCommand(&container[offset],length,cursor,section.code+section.bss,c));
            assert(c.next>cursor);cursor=c.next;++commands;
            // Each parsed command belongs to exactly one load phase. Actual
            // region thresholds are exercised by the game's LoaderParams.
            if (!c.absolute || c.address<0x80500000) ++dol; else ++rel;
        }
        assert(dol+rel==commands && cursor==length);
        std::cout<<"PASS: region "<<region<<", "<<commands<<" complete commands\n";
    }
    unsigned offset=0,length=0;
    assert(NitroKamek::SelectRegion(&container[0],15,0,offset,length));
    assert(NitroKamek::SelectRegion(&container[0],static_cast<unsigned>(container.size()),4,offset,length));
    assert(NitroKamek::SelectRegion(&container[0],static_cast<unsigned>(container.size()-1),0,offset,length));
    b.assign(16,0);Put(b,0,0xffffffff);
    assert(NitroKamek::SelectRegion(&b[0],16,0,offset,length));
    std::cout<<"PASS: malformed headers, lengths, addresses, operands and relative bounds\n";
}
